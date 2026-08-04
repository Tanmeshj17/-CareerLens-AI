"""
Phase 8.7 — Opportunity History / Timeline API
GET /api/opportunity/{id}/history
GET /api/opportunity/{id}/history/stats
GET /api/history/dashboard
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import auth, models
from app.models import Opportunity
from app.opportunity_history import (
    get_history,
    get_history_dashboard_stats,
    record_event,
)

router = APIRouter(prefix="/api/opportunity", tags=["History"])


@router.get("/{opportunity_id}/history")
def get_opportunity_history(
    opportunity_id: int,
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW | MEDIUM | HIGH | CRITICAL"),
    db: Session = Depends(get_db),
):
    """
    Returns the full change timeline for a job.
    Ordered newest-first.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    timeline = get_history(db, opportunity_id, limit=limit, severity_filter=severity)
    return {
        "opportunity_id": opportunity_id,
        "company": opp.company,
        "title": opp.title,
        "change_score": opp.change_score or 0,
        "times_verified": opp.times_verified or 0,
        "times_updated": opp.times_updated or 0,
        "times_reactivated": opp.times_reactivated or 0,
        "first_seen": opp.first_seen.isoformat() if opp.first_seen else None,
        "last_seen": opp.last_seen.isoformat() if opp.last_seen else None,
        "days_active": (
            (opp.last_seen - opp.first_seen).days
            if opp.last_seen and opp.first_seen else 0
        ),
        "timeline": timeline,
        "total_events": len(timeline),
    }


@router.get("/{opportunity_id}/history/stats")
def get_opportunity_history_stats(
    opportunity_id: int,
    db: Session = Depends(get_db),
):
    """Quick stats for the job detail sidebar."""
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    from app.models import OpportunityHistory
    from sqlalchemy import func

    counts = db.query(
        OpportunityHistory.severity,
        func.count(OpportunityHistory.id)
    ).filter(
        OpportunityHistory.opportunity_id == opportunity_id
    ).group_by(OpportunityHistory.severity).all()

    severity_breakdown = {row[0]: row[1] for row in counts}

    recent = db.query(OpportunityHistory).filter(
        OpportunityHistory.opportunity_id == opportunity_id
    ).order_by(OpportunityHistory.recorded_at.desc()).first()

    return {
        "opportunity_id": opportunity_id,
        "change_score": opp.change_score or 0,
        "times_verified": opp.times_verified or 0,
        "times_updated": opp.times_updated or 0,
        "times_reactivated": opp.times_reactivated or 0,
        "first_seen": opp.first_seen.isoformat() if opp.first_seen else None,
        "last_seen": opp.last_seen.isoformat() if opp.last_seen else None,
        "severity_breakdown": severity_breakdown,
        "last_event": recent.event_type if recent else None,
        "last_event_time": recent.recorded_at.isoformat() if recent else None,
    }


# ─────────────────────────────────────────────────────────────
# Platform dashboard endpoint (separate prefix)
# ─────────────────────────────────────────────────────────────
dashboard_router = APIRouter(prefix="/api/history", tags=["History Dashboard"])

def require_admin(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return current_user

@dashboard_router.get("/dashboard")
def history_dashboard(db: Session = Depends(get_db), admin_user: models.User = Depends(require_admin)):
    """Platform-level history metrics for the Data Intelligence Dashboard."""
    return get_history_dashboard_stats(db)
