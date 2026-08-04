from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models import (
    User, Opportunity, CompanyRegistry, CollectorHealth,
    HiringIntelligenceGlobalSnapshot, HiringIntelligenceCompanySnapshot
)
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/quality/opportunity/{opp_id}")
def get_opportunity_quality(opp_id: int, db: Session = Depends(get_db)):
    """Phase 8.6: Detailed quality metrics for a single opportunity."""
    opp = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Not found")
        
    return {
        "id": opp.id,
        "title": opp.title,
        "company": opp.company,
        "lifecycle_status": opp.lifecycle_status,
        "confidence_score": opp.confidence_score,
        "completeness_score": opp.completeness_score,
        "link_quality_score": opp.link_quality_score,
        "verification_count": opp.verification_count,
        "last_verified_at": opp.last_verified_at,
        "salary_intelligence": {
            "min": opp.salary_min,
            "max": opp.salary_max,
            "currency": opp.salary_currency,
            "period": opp.salary_period
        }
    }

@router.get("/company/health")
def get_company_health(db: Session = Depends(get_db)):
    """Phase 8.6: Get health metrics for all active companies."""
    companies = db.query(CompanyRegistry).filter(
        CompanyRegistry.hiring_in_india == True,
        CompanyRegistry.health_score > 0
    ).order_by(CompanyRegistry.health_score.desc()).limit(100).all()
    
    return [
        {
            "company_name": c.company_name,
            "health_score": c.health_score,
            "india_priority": c.india_hiring_priority,
            "source_type": c.source_type
        } for c in companies
    ]

@router.get("/dashboard/freshness")
def get_freshness_dashboard(db: Session = Depends(get_db)):
    """Phase 8.6: Platform-wide opportunity freshness distribution."""
    counts = db.query(
        Opportunity.lifecycle_status,
        func.count(Opportunity.id)
    ).group_by(Opportunity.lifecycle_status).all()
    
    return [{"status": status, "count": count} for status, count in counts]

@router.get("/dashboard/quality")
def get_quality_dashboard(db: Session = Depends(get_db)):
    """Phase 8.6: Average confidence and completeness scores."""
    avg_scores = db.query(
        func.avg(Opportunity.confidence_score).label('avg_conf'),
        func.avg(Opportunity.completeness_score).label('avg_comp')
    ).filter(Opportunity.lifecycle_status.in_(["NEW", "ACTIVE"])).first()
    
    return {
        "average_confidence": round(avg_scores.avg_conf or 0, 1),
        "average_completeness": round(avg_scores.avg_comp or 0, 1)
    }

@router.get("/dashboard/hiring-trends")
def get_hiring_trends(days: int = 7, db: Session = Depends(get_db)):
    """Phase 8.6: Hiring trend snapshots globally."""
    start_date = datetime.utcnow() - timedelta(days=days)
    snapshots = db.query(HiringIntelligenceGlobalSnapshot).filter(
        HiringIntelligenceGlobalSnapshot.snapshot_date >= start_date
    ).order_by(HiringIntelligenceGlobalSnapshot.snapshot_date.asc()).all()
    
    return [
        {
            "date": s.snapshot_date.strftime("%Y-%m-%d"),
            "jobs_today": s.jobs_today,
            "broken_today": s.broken_today,
            "average_confidence": s.average_confidence
        } for s in snapshots
    ]

@router.get("/dashboard/collector-health")
def get_collector_health(db: Session = Depends(get_db)):
    """Phase 8.6: Collector ROI and health status."""
    collectors = db.query(CollectorHealth).order_by(CollectorHealth.success_count.desc()).all()
    return [
        {
            "collector_name": c.collector_name,
            "roi_tier": c.roi_tier,
            "success_count": c.success_count,
            "failure_count": c.failure_count,
            "jobs_collected": c.jobs_collected,
            "last_success": c.last_success
        } for c in collectors
    ]
