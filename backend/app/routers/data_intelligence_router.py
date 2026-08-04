"""
Phase 8.7 + 9.0 — Data Intelligence API
GET  /api/intelligence/collectors
GET  /api/intelligence/quality          - DB quality stats
POST /api/intelligence/quality/audit    - Run quality scoring pass
POST /api/intelligence/duplicates       - Run duplicate detection
POST /api/intelligence/consistency      - Run DB consistency check
POST /api/intelligence/search-event     - Record a user search event
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional

from app.database import get_db
from app import models, auth
from collectors.collector_intelligence import get_collector_dashboard
from app.quality_engine import run_quality_audit, get_database_quality_stats
from app.duplicate_detector import run_duplicate_detection
from app.db_consistency import run_consistency_check

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/intelligence", tags=["Data Intelligence"])

def require_admin(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return current_user

@router.get("/collectors")
@limiter.limit("30/minute")
def get_collectors(request: Request, db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Returns full collector intelligence data for the dashboard."""
    return get_collector_dashboard(db)


@router.get("/lifecycle")
def get_lifecycle_stats(db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Phase 11.3.8: Returns opportunity lifecycle distribution stats."""
    from app.cache import get_or_compute

    def _compute():
        status_counts = dict(
            db.query(models.Opportunity.status, func.count(models.Opportunity.id))
            .group_by(models.Opportunity.status).all()
        )
        source_type_counts = dict(
            db.query(models.Opportunity.source_type, func.count(models.Opportunity.id))
            .group_by(models.Opportunity.source_type).all()
        )
        link_status_counts = dict(
            db.query(models.Opportunity.apply_url_status, func.count(models.Opportunity.id))
            .group_by(models.Opportunity.apply_url_status).all()
        )
        data_origin_counts = dict(
            db.query(models.Opportunity.data_origin, func.count(models.Opportunity.id))
            .group_by(models.Opportunity.data_origin).all()
        )
        lr_status_counts = dict(
            db.query(models.LearningResource.status, func.count(models.LearningResource.id))
            .group_by(models.LearningResource.status).all()
        )

        total = db.query(models.Opportunity).count()
        broken = db.query(models.Opportunity).filter(
            models.Opportunity.apply_url_status == "BROKEN"
        ).count()
        
        return {
            "total_opportunities": total,
            "by_status": {k or "Unknown": v for k, v in status_counts.items()},
            "by_source_type": {k or "Unknown": v for k, v in source_type_counts.items()},
            "by_link_status": {k or "Unknown": v for k, v in link_status_counts.items()},
            "by_data_origin": {k or "Unknown": v for k, v in data_origin_counts.items()},
            "learning_resources_by_status": {k or "Unknown": v for k, v in lr_status_counts.items()},
            "broken_link_count": broken,
            "broken_link_rate": round((broken / total * 100), 2) if total > 0 else 0.0
        }

    return get_or_compute("admin_lifecycle_stats", _compute, ttl_seconds=600)


@router.get("/quality")
def get_quality_stats(db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Returns comprehensive database quality statistics."""
    from app.cache import get_or_compute
    def _compute():
        return get_database_quality_stats(db)
    return get_or_compute("admin_quality_stats", _compute, ttl_seconds=600)


@router.post("/quality/audit")
def trigger_quality_audit(db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Runs the full quality scoring pass and assigns Quality Scores to all opportunities."""
    result = run_quality_audit(db)
    return {"status": "complete", "result": result}


@router.post("/duplicates")
def trigger_duplicate_detection(db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Runs the 3-pass duplicate detection and merge engine."""
    result = run_duplicate_detection(db)
    return {"status": "complete", "result": result}


@router.post("/consistency")
def trigger_consistency_check(db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Runs database consistency audits and auto-repairs detected issues."""
    result = run_consistency_check(db)
    return {"status": "complete", "result": result}


@router.post("/search-event")
def record_search_event(
    query_text: str,
    result_count: int = 0,
    clicked_job_id: Optional[int] = None,
    click_position: Optional[int] = None,
    session_duration_ms: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Records a user search interaction for the Search Learning module."""
    event = models.SearchEvent(
        user_id=user_id,
        query_text=query_text.lower().strip(),
        result_count=result_count,
        clicked_job_id=clicked_job_id,
        click_position=click_position,
        session_duration_ms=session_duration_ms,
        created_at=datetime.utcnow()
    )
    db.add(event)

    # Upsert search aggregate
    agg = db.query(models.SearchAggregate).filter(
        models.SearchAggregate.query_text == query_text.lower().strip()
    ).first()
    if not agg:
        agg = models.SearchAggregate(
            query_text=query_text.lower().strip(),
            total_searches=0,
            zero_result_rate=0.0,
            ctr=0.0
        )
        db.add(agg)

    agg.total_searches += 1
    if result_count == 0:
        # Rolling zero-result rate
        agg.zero_result_rate = (
            (agg.zero_result_rate * (agg.total_searches - 1) + 1.0) / agg.total_searches
        )
    if clicked_job_id:
        agg.ctr = (
            (agg.ctr * (agg.total_searches - 1) + 1.0) / agg.total_searches
        )
    agg.last_searched_at = datetime.utcnow()

    db.commit()
    return {"status": "recorded"}
