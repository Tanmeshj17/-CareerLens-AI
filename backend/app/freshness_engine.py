from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import Opportunity
from app.link_engine import verify_batch, LinkStatus

def run_freshness_verification(batch_size: int = 150):
    """
    Phase 8.6: Freshness Verification Engine
    Verifies HTTP status, redirect, apply page, posting validity.
    Degrades lifecycle_status after repeated failures instead of hard deleting.
    """
    db = SessionLocal()
    now = datetime.utcnow()
    metrics = {"verified": 0, "degraded": 0, "broken": 0, "recovered": 0}

    try:
        # Get active jobs that haven't been verified in 3 days
        check_limit = now - timedelta(days=3)
        urls_to_check = db.query(Opportunity).filter(
            Opportunity.lifecycle_status.in_(["NEW", "ACTIVE", "STALE"]),
            Opportunity.apply_url != None,
            (Opportunity.last_verified_at < check_limit) | (Opportunity.last_verified_at == None)
        ).order_by(Opportunity.last_verified_at.asc().nulls_first()).limit(batch_size).all()

        if not urls_to_check:
            return metrics

        # Verify links using the Link Engine
        results = verify_batch(urls_to_check, timeout=10)
        
        for opp, status, classification, score, final_url in results:
            opp.last_verified_at = now
            opp.apply_url_status = status
            opp.link_classification = classification
            opp.verified_apply_url = final_url or opp.apply_url
            
            if status == LinkStatus.BROKEN or status == LinkStatus.HOMEPAGE_ONLY:
                # Failed verification — explicitly set score to 0 for BROKEN, 10 for HOMEPAGE_ONLY
                # This prevents the default score of 100 from misleading the rank engine
                opp.link_quality_score = 0 if status == LinkStatus.BROKEN else 10
                opp.verification_count = (opp.verification_count or 0) + 1
                
                # After 3 failures over time, degrade
                if opp.verification_count >= 3:
                    opp.lifecycle_status = "BROKEN" if status == LinkStatus.BROKEN else "STALE"
                    opp.expired_reason = "Repeated Link Failures"
                    metrics["broken"] += 1
                else:
                    metrics["degraded"] += 1
            else:
                # Success — store the engine-returned score (>0)
                opp.link_quality_score = max(score, 1)  # ensure positive
                if opp.lifecycle_status in ["BROKEN", "EXPIRED"]:
                    metrics["recovered"] += 1
                opp.lifecycle_status = "ACTIVE"
                opp.verification_count = 0 # Reset on success
                metrics["verified"] += 1
                
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Freshness verification error: {e}")
    finally:
        db.close()
        
    return metrics
