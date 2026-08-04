"""
Phase 11.4: Admin Dashboard API Router (T1, T2, T3, Alerts, Quality Reports)
Provides comprehensive data quality, collector health, source coverage, and pipeline observability APIs for system administrators.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import CollectorHealth, Opportunity, PipelineRunMetrics, DataAlert, CompanyAlias, LocationNorm

router = APIRouter(prefix="/api/admin", tags=["Admin & Data Quality"])


# ─────────────────────────────────────────────────────────────
# T1: Collector Health Dashboard API
# ─────────────────────────────────────────────────────────────

@router.get("/collectors/health")
def get_collector_health_dashboard(db: Session = Depends(get_db)):
    """
    Returns complete health dashboard for all tracked collectors.
    Includes score, tier, success rate, broken link %, duplicate %, last run.
    """
    from app.data_quality_reporter import generate_collector_health_report
    collectors = db.query(CollectorHealth).order_by(CollectorHealth.collector_score.desc()).all()
    
    total = len(collectors)
    active = sum(1 for c in collectors if c.status == "Active")
    degraded = sum(1 for c in collectors if c.status == "Degraded")
    failed = sum(1 for c in collectors if c.status == "Failed")
    paused = sum(1 for c in collectors if c.status == "Paused")

    items = []
    for c in collectors:
        items.append({
            "id": c.id,
            "collector_name": c.collector_name,
            "status": c.status,
            "collector_score": round(c.collector_score, 1),
            "roi_tier": c.roi_tier,
            "success_rate": round(c.success_rate, 1),
            "total_runs": c.total_runs,
            "total_jobs_fetched": c.total_jobs_fetched,
            "duplicates_removed": c.duplicates_removed,
            "broken_links_pct": round(c.broken_links_pct or 0.0, 1),
            "duplicate_pct": round(c.duplicate_pct or 0.0, 1),
            "avg_latency_ms": c.avg_latency_ms,
            "last_run": c.last_run.isoformat() if c.last_run else None,
            "error_message": c.error_message,
        })

    return {
        "summary": {
            "total": total,
            "active": active,
            "degraded": degraded,
            "failed": failed,
            "paused": paused,
            "health_pct": round((active / total * 100), 1) if total > 0 else 0.0,
        },
        "collectors": items,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/collectors/{collector_id}/action")
def update_collector_action(
    collector_id: int,
    action: str = Query(..., description="Action: pause | resume | reset | run"),
    db: Session = Depends(get_db)
):
    """
    Perform admin action on a specific collector (pause, resume, reset stats).
    """
    collector = db.query(CollectorHealth).filter(CollectorHealth.id == collector_id).first()
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")

    action_lower = action.lower()
    if action_lower == "pause":
        collector.status = "Paused"
    elif action_lower == "resume":
        collector.status = "Active"
    elif action_lower == "reset":
        collector.success_rate = 100.0
        collector.failed_runs = 0
        collector.status = "Active"
        collector.error_message = None
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")

    db.commit()
    return {"message": f"Collector '{collector.collector_name}' updated to {collector.status}", "status": collector.status}


# ─────────────────────────────────────────────────────────────
# T2: Pipeline Observability & Run Reports API
# ─────────────────────────────────────────────────────────────

@router.get("/pipeline/runs")
def list_pipeline_runs(
    limit: int = Query(20, ge=1, le=100),
    pipeline_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List recent pipeline execution runs with latency, throughput, and error metrics.
    """
    from app.pipeline_observer import get_pipeline_metrics
    runs = get_pipeline_metrics(db, pipeline_name=pipeline_name, limit=limit)
    return {"runs": runs, "count": len(runs)}


@router.get("/pipeline/report")
def get_pipeline_report(db: Session = Depends(get_db)):
    """
    Returns markdown pipeline observability report.
    """
    from app.pipeline_observer import generate_pipeline_observability_report
    report_md = generate_pipeline_observability_report(db)
    return {"report_markdown": report_md, "timestamp": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────────────────────
# T3: Source Coverage Dashboard API
# ─────────────────────────────────────────────────────────────

@router.get("/coverage/summary")
def get_source_coverage_summary(db: Session = Depends(get_db)):
    """
    Returns high-level source coverage breakdown by company, location, source type, job type.
    """
    from app.data_quality_reporter import generate_source_coverage_report
    from sqlalchemy import func

    total_active = db.query(func.count(Opportunity.id)).filter(Opportunity.status == "ACTIVE").scalar() or 0
    unique_companies = db.query(func.count(func.distinct(Opportunity.company))).filter(Opportunity.status == "ACTIVE").scalar() or 0
    unique_locations = db.query(func.count(func.distinct(Opportunity.location))).filter(Opportunity.status == "ACTIVE").scalar() or 0
    india_jobs = db.query(func.count(Opportunity.id)).filter(Opportunity.status == "ACTIVE", Opportunity.is_india_job == True).scalar() or 0

    return {
        "metrics": {
            "total_active_jobs": total_active,
            "unique_companies": unique_companies,
            "unique_locations": unique_locations,
            "india_jobs_count": india_jobs,
            "india_ratio_pct": round((india_jobs / total_active * 100), 1) if total_active > 0 else 0.0,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/coverage/companies")
def get_top_hiring_companies(limit: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    """Top companies by active opportunity count."""
    from sqlalchemy import func
    top = (
        db.query(Opportunity.company, func.count(Opportunity.id).label("count"))
        .filter(Opportunity.status == "ACTIVE", Opportunity.company != None)
        .group_by(Opportunity.company)
        .order_by(func.count(Opportunity.id).desc())
        .limit(limit)
        .all()
    )
    return [{"company": c, "active_jobs": count} for c, count in top]


@router.get("/coverage/locations")
def get_top_hiring_locations(limit: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    """Top locations by active opportunity count."""
    from sqlalchemy import func
    top = (
        db.query(Opportunity.location, func.count(Opportunity.id).label("count"))
        .filter(Opportunity.status == "ACTIVE", Opportunity.location != None)
        .group_by(Opportunity.location)
        .order_by(func.count(Opportunity.id).desc())
        .limit(limit)
        .all()
    )
    return [{"location": l, "active_jobs": count} for l, count in top]


# ─────────────────────────────────────────────────────────────
# Quality Score & System Reports
# ─────────────────────────────────────────────────────────────

@router.get("/quality/score")
def get_system_quality_score(db: Session = Depends(get_db)):
    """
    Returns overall 0-100 composite data quality score and sub-domain metrics.
    """
    from app.data_quality_reporter import compute_data_quality_score
    return compute_data_quality_score(db)


@router.get("/quality/reports/all")
def get_all_quality_reports(db: Session = Depends(get_db)):
    """
    Generates and returns all markdown quality reports in one response.
    """
    from app.data_quality_reporter import generate_all_reports
    reports = generate_all_reports(db, save_to_disk=True)
    return {"reports": reports, "generated_at": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────────────────────
# Alert Management API (T13)
# ─────────────────────────────────────────────────────────────

@router.get("/alerts")
def get_alerts(
    unresolved_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    List data quality and pipeline alerts.
    """
    from app.alert_engine import get_active_alerts
    query = db.query(DataAlert)
    if unresolved_only:
        query = query.filter(DataAlert.is_resolved == False)
    alerts = query.order_by(DataAlert.created_at.desc()).limit(limit).all()

    return {
        "count": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "source": a.source,
                "message": a.message,
                "metric_name": a.metric_name,
                "metric_value": a.metric_value,
                "threshold": a.threshold,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]
    }


@router.post("/alerts/{alert_id}/resolve")
def mark_alert_resolved(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved."""
    from app.alert_engine import resolve_alert
    success = resolve_alert(db, alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": f"Alert {alert_id} resolved", "success": True}


# ─────────────────────────────────────────────────────────────
# Trigger Batch Operations
# ─────────────────────────────────────────────────────────────

@router.post("/triggers/duplicate-detection-v2")
def trigger_duplicate_detection(db: Session = Depends(get_db)):
    """
    Trigger 4-pass fuzzy duplicate detection v2.
    """
    from app.duplicate_detector_v2 import run_fuzzy_duplicate_detection
    res = run_fuzzy_duplicate_detection(db)
    return {"status": "SUCCESS", "results": res}


@router.post("/triggers/company-normalization")
def trigger_company_normalization(db: Session = Depends(get_db)):
    """
    Batch normalize company names across all opportunities.
    """
    from app.normalizers.company import run_company_normalization
    res = run_company_normalization(db)
    return {"status": "SUCCESS", "results": res}


@router.post("/triggers/location-normalization")
def trigger_location_normalization(db: Session = Depends(get_db)):
    """
    Batch normalize locations across all opportunities.
    """
    from app.normalizers.location import run_location_normalization
    res = run_location_normalization(db)
    return {"status": "SUCCESS", "results": res}


@router.post("/triggers/lifecycle-validation")
def trigger_lifecycle_validation(db: Session = Depends(get_db)):
    """
    Audit and auto-fix stuck job lifecycle states.
    """
    from app.lifecycle_validator import validate_lifecycle_transitions
    res = validate_lifecycle_transitions(db)
    return {"status": "SUCCESS", "results": res}


@router.post("/triggers/alert-scan")
def trigger_alert_scan(db: Session = Depends(get_db)):
    """
    Run full system alert scan.
    """
    from app.alert_engine import run_alert_scan
    res = run_alert_scan(db)
    return {"status": "SUCCESS", "results": res}
