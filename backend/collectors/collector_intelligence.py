"""
Phase 8.7 — Collector Intelligence V2
Data Collection Operating System

Scores every collector across 18 metrics.
Computes Stability + composite Score.
Generates automatic alerts.
Writes daily health history snapshots.
Powers adaptive scheduling.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    Opportunity, CollectorHealth, CollectorHealthHistory,
    CollectorAlert, CompanyRegistry, OpportunityHistory
)
from app.database import SessionLocal

logger = logging.getLogger("collector_intelligence")

# ─────────────────────────────────────────────────────────────
# Alert thresholds
# ─────────────────────────────────────────────────────────────
ALERT_RULES = [
    # (alert_type, metric_attr, threshold, operator, severity, message_template)
    ("LOW_SCORE",        "collector_score",      40,  "<",  "ALERT",    "Collector score {val:.0f} below threshold 40"),
    ("HIGH_BROKEN_LINKS","broken_links_pct",     20,  ">",  "ALERT",    "Broken links {val:.1f}% exceeds 20%"),
    ("HIGH_DUPLICATES",  "duplicate_pct",        30,  ">",  "WARNING",  "Duplicate rate {val:.1f}% exceeds 30%"),
    ("LOW_CONFIDENCE",   "avg_confidence",       50,  "<",  "WARNING",  "Average confidence {val:.0f} below 50"),
    ("TIMEOUT_SPIKE",    "timeout_rate",         15,  ">",  "WARNING",  "Timeout rate {val:.1f}% exceeds 15%"),
    ("UPTIME_DROP",      "crawler_uptime_pct",   80,  "<",  "ALERT",    "Crawler uptime {val:.1f}% below 80%"),
    ("STABILITY_DEGRADED","collector_stability", 30,  "<",  "WARNING",  "Stability score {val:.0f} below 30"),
]

# ─────────────────────────────────────────────────────────────
# Scoring weights
# ─────────────────────────────────────────────────────────────
SCORE_WEIGHTS = {
    "yield_quality": 0.20,   # new_jobs_pct + jobs_collected_today
    "freshness":     0.15,   # avg_freshness_days (lower=better)
    "confidence":    0.15,   # avg_confidence
    "completeness":  0.15,   # avg_completeness
    "verification":  0.15,   # avg_verification_success
    "link_health":   0.10,   # 100 - broken_links_pct
    "stability":     0.10,   # collector_stability
}

STABILITY_WEIGHTS = {
    "success_rate":       0.40,
    "crawler_uptime_pct": 0.20,
    "freshness_inv":      0.15,   # 100 - avg_freshness_days clamped
    "retry_success_rate": 0.10,
    "timeout_penalty":    0.10,   # 100 - timeout_rate
    "failure_penalty":    0.05,   # subtracted
}

# ─────────────────────────────────────────────────────────────
# Core: compute_collector_score
# ─────────────────────────────────────────────────────────────

def compute_collector_score(h: CollectorHealth) -> Tuple[float, float]:
    """
    Returns (collector_score, collector_stability) both 0–100.
    """
    def _safe(val, default=0.0):
        return float(val) if val is not None else default

    # ── Stability score
    success = _safe(h.success_rate, 50.0)
    uptime  = _safe(h.crawler_uptime_pct, 50.0)
    fresh_inv = max(0.0, 100.0 - min(_safe(h.avg_freshness_days, 7.0) * 10, 100.0))
    retry   = _safe(h.retry_success_rate, 50.0)
    timeout_pen = max(0.0, 100.0 - _safe(h.timeout_rate, 0.0) * 5)
    fail_pen    = min(30.0, _safe(h.failure_count, 0) * 2.0)

    stability = (
        success      * STABILITY_WEIGHTS["success_rate"] +
        uptime       * STABILITY_WEIGHTS["crawler_uptime_pct"] +
        fresh_inv    * STABILITY_WEIGHTS["freshness_inv"] +
        retry        * STABILITY_WEIGHTS["retry_success_rate"] +
        timeout_pen  * STABILITY_WEIGHTS["timeout_penalty"]
    ) - fail_pen * STABILITY_WEIGHTS["failure_penalty"]
    stability = max(0.0, min(100.0, stability))

    # ── Yield quality component
    new_pct     = _safe(h.new_jobs_pct, 50.0)
    today_score = min(100.0, _safe(h.jobs_collected_today, 0) / 2.0)  # 200+ jobs = 100
    yield_q     = (new_pct * 0.6 + today_score * 0.4)

    # ── Freshness component (fewer days = higher score)
    freshness_days = _safe(h.avg_freshness_days, 7.0)
    freshness_score = max(0.0, 100.0 - freshness_days * 5.0)  # 0 days=100, 20 days=0

    # ── Link health
    link_health = max(0.0, 100.0 - _safe(h.broken_links_pct, 0.0))

    # ── Composite score
    score = (
        yield_q                              * SCORE_WEIGHTS["yield_quality"] +
        freshness_score                      * SCORE_WEIGHTS["freshness"] +
        _safe(h.avg_confidence, 50.0)        * SCORE_WEIGHTS["confidence"] +
        _safe(h.avg_completeness, 50.0)      * SCORE_WEIGHTS["completeness"] +
        _safe(h.avg_verification_success, 50.0) * SCORE_WEIGHTS["verification"] +
        link_health                          * SCORE_WEIGHTS["link_health"] +
        stability                            * SCORE_WEIGHTS["stability"]
    )
    score = max(0.0, min(100.0, score))

    return round(score, 2), round(stability, 2)


def compute_adaptive_interval(h: CollectorHealth, company: Optional[CompanyRegistry] = None) -> float:
    """
    Returns optimal crawl interval in hours.
    Formula: base_interval / (score_factor × priority_factor × velocity_factor)

    Bounds: 1h (min, hot company) → 168h = 7 days (max, cold/retired)
    """
    score = h.collector_score or 0.0
    score_factor = max(0.1, score / 100.0)

    # Priority factor from company registry
    priority_map = {"high": 1.5, "medium": 1.0, "low": 0.6}
    priority = priority_map.get(getattr(company, "priority", "medium"), 1.0)

    # Hiring velocity from recent history events
    hist_events = h.history_events_generated or 0
    velocity_factor = 1.0 + min(1.0, hist_events / 50.0)  # Up to 2× if high change rate

    # Recent yield factor
    recent_yield = min(1.5, (h.jobs_collected_today or 0) / 50.0 + 0.5)

    base_hours = 24.0
    interval = base_hours / (score_factor * priority * velocity_factor * recent_yield)
    return round(max(1.0, min(168.0, interval)), 1)


def assign_tier(score: float) -> str:
    if score >= 80:
        return "Tier A"
    elif score >= 55:
        return "Tier B"
    elif score >= 30:
        return "Tier C"
    return "Tier D"


# ─────────────────────────────────────────────────────────────
# Compute metrics FROM the DB (live)
# ─────────────────────────────────────────────────────────────

def compute_live_metrics(db: Session, collector_name: str) -> Dict[str, Any]:
    """
    Queries the opportunities table to compute live quality metrics
    for a given collector.
    """
    opps = db.query(Opportunity).filter(
        Opportunity.collected_by == collector_name,
        Opportunity.is_active == True
    ).all()

    if not opps:
        return {}

    total = len(opps)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)

    # Quality
    confidences    = [o.confidence_score for o in opps if o.confidence_score]
    completenesses = [o.completeness_score for o in opps if o.completeness_score]
    broken         = [o for o in opps if o.apply_url_status == "BROKEN"]
    collected_today = [o for o in opps if o.first_seen and o.first_seen >= today]

    # Freshness (days since posted)
    freshness_vals = []
    for o in opps:
        if o.posted_date:
            days = (datetime.utcnow() - o.posted_date).days
            freshness_vals.append(days)

    # History events for this collector
    events_today = db.query(OpportunityHistory).filter(
        OpportunityHistory.collector_name == collector_name,
        OpportunityHistory.recorded_at >= today
    ).count()

    salary_events = db.query(OpportunityHistory).filter(
        OpportunityHistory.collector_name == collector_name,
        OpportunityHistory.event_type == "SALARY_CHANGED"
    ).count()

    return {
        "active_jobs": total,
        "jobs_collected_today": len(collected_today),
        "broken_links_pct": round(len(broken) / total * 100, 2) if total else 0.0,
        "avg_confidence": round(sum(confidences) / len(confidences), 1) if confidences else None,
        "avg_completeness": round(sum(completenesses) / len(completenesses), 1) if completenesses else None,
        "avg_freshness_days": round(sum(freshness_vals) / len(freshness_vals), 1) if freshness_vals else None,
        "history_events_generated": events_today,
        "salary_change_rate": round(salary_events / max(total, 1) * 100, 2),
    }


# ─────────────────────────────────────────────────────────────
# generate_alerts
# ─────────────────────────────────────────────────────────────

def generate_alerts(db: Session, h: CollectorHealth):
    """Fire alerts when metrics cross thresholds. Dedup by checking unresolved."""
    for alert_type, metric, threshold, op, severity, msg_tpl in ALERT_RULES:
        val = getattr(h, metric, None)
        if val is None:
            continue

        triggered = (op == "<" and val < threshold) or (op == ">" and val > threshold)
        if not triggered:
            continue

        # Avoid duplicate unresolved alerts
        existing = db.query(CollectorAlert).filter(
            CollectorAlert.collector_name == h.collector_name,
            CollectorAlert.alert_type == alert_type,
            CollectorAlert.is_resolved == False
        ).first()
        if existing:
            continue

        alert = CollectorAlert(
            collector_name=h.collector_name,
            ats_type=h.ats_type,
            alert_type=alert_type,
            severity=severity,
            message=msg_tpl.format(val=val),
            metric_name=metric,
            metric_value=val,
            threshold=float(threshold),
        )
        db.add(alert)
        logger.warning(f"[ALERT:{severity}] {h.collector_name} — {alert.message}")

    # Special: no jobs in 48h
    if h.last_success:
        hours_since = (datetime.utcnow() - h.last_success).total_seconds() / 3600
        if hours_since > 48:
            existing = db.query(CollectorAlert).filter(
                CollectorAlert.collector_name == h.collector_name,
                CollectorAlert.alert_type == "NO_JOBS_48H",
                CollectorAlert.is_resolved == False
            ).first()
            if not existing:
                db.add(CollectorAlert(
                    collector_name=h.collector_name,
                    ats_type=h.ats_type,
                    alert_type="NO_JOBS_48H",
                    severity="CRITICAL",
                    message=f"No jobs collected in {hours_since:.0f} hours",
                    metric_name="last_success",
                    metric_value=hours_since,
                    threshold=48.0,
                ))


# ─────────────────────────────────────────────────────────────
# snapshot_health_history
# ─────────────────────────────────────────────────────────────

def snapshot_health_history(db: Session, h: CollectorHealth):
    """Save daily snapshot for trend analysis."""
    snap = CollectorHealthHistory(
        collector_name=h.collector_name,
        ats_type=h.ats_type,
        snapshot_date=datetime.utcnow(),
        collector_score=h.collector_score,
        collector_stability=h.collector_stability,
        roi_tier=h.roi_tier,
        jobs_collected=h.jobs_collected_today or 0,
        active_jobs=h.active_jobs or 0,
        duplicate_pct=h.duplicate_pct,
        broken_links_pct=h.broken_links_pct,
        avg_confidence=h.avg_confidence,
        avg_freshness_days=h.avg_freshness_days,
        success_rate=h.success_rate,
        crawler_uptime_pct=h.crawler_uptime_pct,
        avg_response_ms=h.avg_response_ms,
    )
    db.add(snap)


# ─────────────────────────────────────────────────────────────
# update_collector_record  —  main entry point called after each run
# ─────────────────────────────────────────────────────────────

def update_collector_record(
    db: Session,
    collector_name: str,
    ats_type: str,
    run_result: Dict[str, Any],
    company_name: Optional[str] = None,
) -> CollectorHealth:
    """
    Called by registry_runner after each company collection.
    Updates or creates a CollectorHealth record, computes score,
    assigns tier, sets adaptive interval, generates alerts.
    """
    record = db.query(CollectorHealth).filter(
        CollectorHealth.collector_name == collector_name
    ).first()

    if not record:
        record = CollectorHealth(collector_name=collector_name, ats_type=ats_type)
        db.add(record)

    # ── Merge run_result into record
    record.ats_type = ats_type
    record.last_run = datetime.utcnow()

    is_success = run_result.get("status") == "success"
    if is_success:
        record.success_count = (record.success_count or 0) + 1
        record.last_success = datetime.utcnow()
        jobs = run_result.get("jobs_count", 0)
        record.jobs_collected_today = (record.jobs_collected_today or 0) + jobs
        record.jobs_collected_total = (record.jobs_collected_total or 0) + jobs
        record.active_jobs = run_result.get("active_jobs", record.active_jobs)
    else:
        record.failure_count = (record.failure_count or 0) + 1
        record.last_failure = datetime.utcnow()
        record.last_error_message = run_result.get("error", "")[:500]
        record.errors = (record.errors or 0) + 1

    # Duration
    if run_result.get("duration_ms"):
        old = record.avg_response_ms or run_result["duration_ms"]
        record.avg_response_ms = round((old * 0.7 + run_result["duration_ms"] * 0.3), 1)

    # Success rate (rolling EMA)
    total_runs = (record.success_count or 0) + (record.failure_count or 0)
    if total_runs > 0:
        record.success_rate = round((record.success_count or 0) / total_runs * 100, 1)

    # Merge live metrics from DB
    live = compute_live_metrics(db, collector_name)
    for key, val in live.items():
        if hasattr(record, key) and val is not None:
            setattr(record, key, val)

    # ── Score + stability
    score, stability = compute_collector_score(record)
    record.collector_score = score
    record.collector_stability = stability
    record.roi_tier = assign_tier(score)

    # Status transition
    if score >= 55:
        record.status = "Active"
    elif score >= 30:
        record.status = "Degraded"
    else:
        record.status = "Paused"

    # ── Adaptive interval
    company = None
    if company_name:
        company = db.query(CompanyRegistry).filter(
            CompanyRegistry.company_name == company_name
        ).first()
    record.adaptive_interval_hours = compute_adaptive_interval(record, company)

    # Set next_run_at
    record.next_run_at = datetime.utcnow() + timedelta(hours=record.adaptive_interval_hours)

    # ── Yield percent
    if record.jobs_collected_total and record.jobs_inserted:
        record.yield_percent = round(record.jobs_inserted / record.jobs_collected_total * 100, 1)

    db.flush()

    # ── Alerts
    generate_alerts(db, record)

    db.commit()
    return record


# ─────────────────────────────────────────────────────────────
# run_daily_snapshot  —  called once per day by scheduler
# ─────────────────────────────────────────────────────────────

def run_daily_snapshot():
    """Snapshot all collector health records for trend analysis."""
    db = SessionLocal()
    try:
        collectors = db.query(CollectorHealth).all()
        for h in collectors:
            snapshot_health_history(db, h)
        db.commit()
        logger.info(f"Daily snapshot saved for {len(collectors)} collectors.")
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────
# get_collector_dashboard  —  for the API
# ─────────────────────────────────────────────────────────────

def get_collector_dashboard(db: Session) -> Dict[str, Any]:
    """Returns full collector intelligence data for the dashboard."""
    collectors = db.query(CollectorHealth).order_by(
        CollectorHealth.collector_score.desc()
    ).all()

    active_alerts = db.query(CollectorAlert).filter(
        CollectorAlert.is_resolved == False
    ).order_by(CollectorAlert.created_at.desc()).limit(20).all()

    rows = []
    for h in collectors:
        # Trend: compare to last snapshot
        last_snap = db.query(CollectorHealthHistory).filter(
            CollectorHealthHistory.collector_name == h.collector_name
        ).order_by(CollectorHealthHistory.snapshot_date.desc()).first()

        trend = "stable"
        if last_snap and last_snap.collector_score is not None and h.collector_score is not None:
            delta = h.collector_score - last_snap.collector_score
            if delta >= 3:
                trend = "up"
            elif delta <= -3:
                trend = "down"

        rows.append({
            "collector": h.collector_name,
            "ats_type": h.ats_type,
            "status": h.status,
            "tier": h.roi_tier,
            "score": h.collector_score,
            "stability": h.collector_stability,
            "adaptive_interval_hours": h.adaptive_interval_hours,
            "jobs_today": h.jobs_collected_today,
            "active_jobs": h.active_jobs,
            "duplicate_pct": h.duplicate_pct,
            "broken_links_pct": h.broken_links_pct,
            "avg_confidence": h.avg_confidence,
            "avg_freshness_days": h.avg_freshness_days,
            "avg_response_ms": h.avg_response_ms,
            "success_rate": h.success_rate,
            "crawler_uptime_pct": h.crawler_uptime_pct,
            "history_events": h.history_events_generated,
            "last_run": h.last_run.isoformat() if h.last_run else None,
            "next_run": h.next_run_at.isoformat() if h.next_run_at else None,
            "trend": trend,
        })

    return {
        "summary": {
            "total_collectors": len(collectors),
            "tier_a": sum(1 for h in collectors if h.roi_tier == "Tier A"),
            "tier_b": sum(1 for h in collectors if h.roi_tier == "Tier B"),
            "tier_c": sum(1 for h in collectors if h.roi_tier == "Tier C"),
            "tier_d": sum(1 for h in collectors if h.roi_tier == "Tier D"),
            "active_alerts": len(active_alerts),
            "avg_score": round(
                sum(h.collector_score or 0 for h in collectors) / max(len(collectors), 1), 1
            ),
        },
        "collectors": rows,
        "alerts": [
            {
                "id": a.id,
                "collector": a.collector_name,
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "metric": a.metric_name,
                "value": a.metric_value,
                "created_at": a.created_at.isoformat(),
            }
            for a in active_alerts
        ],
    }
