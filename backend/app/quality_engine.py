"""
Phase 9.0 Wave 2: Data Quality Engine
Assigns a Quality Score (0-100) to every opportunity based on:
- Completeness (fields filled) × 40
- Link Quality × 20
- Confidence Score × 20
- Freshness × 20
"""
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Opportunity, JobQualityMetrics
from typing import Dict, Any
import logging

logger = logging.getLogger("quality_engine")


def compute_quality_score(opp: Opportunity) -> int:
    """Compute a 0-100 quality score for a single opportunity."""
    score = 0

    # 1. Completeness (40 pts) — how many key fields are present
    fields = [
        opp.title, opp.company, opp.location, opp.description,
        opp.apply_url, opp.salary_range, opp.required_skills,
        opp.job_type, opp.opportunity_category, opp.posted_date
    ]
    filled = sum(1 for f in fields if f)
    completeness_pct = filled / len(fields)
    score += int(completeness_pct * 40)

    # 2. Link Quality (20 pts)
    link_q = opp.link_quality_score or 0
    score += int((link_q / 100) * 20)

    # 3. Confidence (20 pts)
    conf = opp.confidence_score or 0
    score += int((conf / 100) * 20)

    # 4. Freshness (20 pts)
    now = datetime.utcnow()
    posted = opp.posted_date or opp.first_seen or now
    delta_days = (now - posted).days
    if delta_days <= 3:
        freshness = 20
    elif delta_days <= 7:
        freshness = 16
    elif delta_days <= 14:
        freshness = 12
    elif delta_days <= 30:
        freshness = 6
    elif delta_days <= 60:
        freshness = 2
    else:
        freshness = 0
    score += freshness

    # Hard deductions
    lifecycle = opp.lifecycle_status or "NEW"
    if lifecycle == "EXPIRED":
        return 0
    if lifecycle == "BROKEN":
        score = max(score - 40, 0)
    if lifecycle == "STALE":
        score = max(score - 20, 0)

    apply_status = opp.apply_url_status or "UNKNOWN"
    if apply_status == "BROKEN":
        score = max(score - 30, 0)
    elif apply_status == "HOMEPAGE_ONLY":
        score = max(score - 15, 0)

    return min(score, 100)


def run_quality_audit(db: Session) -> Dict[str, Any]:
    """Batch-assign quality scores to all opportunities and generate stats."""
    all_opps = db.query(Opportunity).filter(Opportunity.is_active == True).all()

    total = len(all_opps)
    score_sum = 0
    below_60 = 0
    below_40 = 0
    score_distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}

    for opp in all_opps:
        q_score = compute_quality_score(opp)
        score_sum += q_score

        # Upsert quality metrics row
        qm = db.query(JobQualityMetrics).filter(
            JobQualityMetrics.opportunity_id == opp.id
        ).first()
        if not qm:
            qm = JobQualityMetrics(opportunity_id=opp.id)
            db.add(qm)
        qm.quality_score = q_score
        qm.trust_score = opp.trust_score or 0
        qm.last_verified = datetime.utcnow()

        if q_score < 40:
            below_40 += 1
        if q_score < 60:
            below_60 += 1

        if q_score <= 20: score_distribution["0-20"] += 1
        elif q_score <= 40: score_distribution["21-40"] += 1
        elif q_score <= 60: score_distribution["41-60"] += 1
        elif q_score <= 80: score_distribution["61-80"] += 1
        else: score_distribution["81-100"] += 1

    db.commit()

    avg_score = round(score_sum / total, 2) if total else 0
    logger.info(f"Quality Audit Complete: {total} opps, avg_score={avg_score}, below_60={below_60}")

    return {
        "total_audited": total,
        "avg_quality_score": avg_score,
        "below_60_count": below_60,
        "below_40_count": below_40,
        "score_distribution": score_distribution
    }


def get_database_quality_stats(db: Session) -> Dict[str, Any]:
    """Generate comprehensive DB quality statistics."""
    now = datetime.utcnow()
    total = db.query(func.count(Opportunity.id)).scalar()
    active = db.query(func.count(Opportunity.id)).filter(Opportunity.is_active == True).scalar()
    expired = db.query(func.count(Opportunity.id)).filter(Opportunity.lifecycle_status == "EXPIRED").scalar()
    broken = db.query(func.count(Opportunity.id)).filter(Opportunity.lifecycle_status == "BROKEN").scalar()
    stale = db.query(func.count(Opportunity.id)).filter(Opportunity.lifecycle_status == "STALE").scalar()

    verified_links = db.query(func.count(Opportunity.id)).filter(
        Opportunity.apply_url_status.in_(["VERIFIED_DIRECT", "VERIFIED_POSTING"])
    ).scalar()
    broken_links = db.query(func.count(Opportunity.id)).filter(
        Opportunity.apply_url_status == "BROKEN"
    ).scalar()

    missing_salary = db.query(func.count(Opportunity.id)).filter(
        Opportunity.salary_range == None
    ).scalar()
    missing_skills = db.query(func.count(Opportunity.id)).filter(
        Opportunity.required_skills == None
    ).scalar()
    missing_exp = db.query(func.count(Opportunity.id)).filter(
        Opportunity.experience_min == None
    ).scalar()
    missing_location = db.query(func.count(Opportunity.id)).filter(
        Opportunity.location == None
    ).scalar()

    avg_conf = db.query(func.avg(Opportunity.confidence_score)).scalar() or 0
    avg_comp = db.query(func.avg(Opportunity.completeness_score)).scalar() or 0

    # Freshness: jobs posted in last 7 days
    fresh_cutoff = now - timedelta(days=7)
    fresh_count = db.query(func.count(Opportunity.id)).filter(
        Opportunity.posted_date >= fresh_cutoff, Opportunity.is_active == True
    ).scalar()
    avg_freshness_pct = round((fresh_count / active * 100), 2) if active else 0

    return {
        "total_opportunities": total,
        "active_opportunities": active,
        "expired_opportunities": expired,
        "broken_lifecycle": broken,
        "stale_opportunities": stale,
        "verified_links": verified_links,
        "broken_links": broken_links,
        "missing_salary": missing_salary,
        "missing_skills": missing_skills,
        "missing_experience": missing_exp,
        "missing_location": missing_location,
        "avg_confidence": round(float(avg_conf), 2),
        "avg_completeness": round(float(avg_comp), 2),
        "fresh_pct": avg_freshness_pct,
    }
