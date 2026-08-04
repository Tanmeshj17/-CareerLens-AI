"""
Phase 11.4 T13: Alert Engine
System-wide data quality alert system.
Uses CollectorAlert (per-collector) + DataAlert (global system alerts).

Alert Types:
  BROKEN_LINKS_HIGH       — broken link rate > threshold
  DUPLICATE_RATE_HIGH     — duplicate rate > threshold
  FRESHNESS_LOW           — fresh jobs < threshold
  INDIA_RATIO_LOW         — India jobs < threshold
  PIPELINE_FAILED         — pipeline completed with failures
  COLLECTOR_ZERO_RESULT   — collector returned 0 jobs
  COLLECTOR_SLOW          — collector took > 30s
  LIFECYCLE_STUCK         — jobs stuck in wrong lifecycle state
  RESOURCE_INVALID_HIGH   — too many invalid learning resources

Thresholds (targets from Phase 11.4 spec):
  broken_links:  > 5% → WARNING, > 10% → CRITICAL
  duplicates:    > 5% → WARNING
  freshness:     < 80% within 7d → WARNING, < 50% → CRITICAL
  india_ratio:   < 70% → WARNING
  pipeline_fail: any failure → CRITICAL
  zero_result:   any → WARNING

Cooldown: 24h per (alert_type + source) to avoid spam.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import DataAlert, CollectorAlert, Opportunity, CollectorHealth

logger = logging.getLogger("alert_engine")

# ─── Alert thresholds ────────────────────────────────────────
THRESHOLDS = {
    "broken_links_warning": 5.0,
    "broken_links_critical": 10.0,
    "duplicate_rate_warning": 5.0,
    "freshness_warning_pct": 80.0,    # below this → WARNING
    "freshness_critical_pct": 50.0,   # below this → CRITICAL
    "india_ratio_warning": 70.0,
    "resource_invalid_warning": 10.0,  # % of resources that are INVALID
}

COOLDOWN_HOURS = 24


def _cooldown_key(alert_type: str, source: str) -> str:
    return f"{alert_type}::{source}"


def _is_on_cooldown(db: Session, alert_type: str, source: str) -> bool:
    """Check if same alert fired within cooldown window."""
    key = _cooldown_key(alert_type, source)
    cutoff = datetime.utcnow() - timedelta(hours=COOLDOWN_HOURS)
    existing = db.query(DataAlert).filter(
        DataAlert.cooldown_key == key,
        DataAlert.created_at > cutoff,
        DataAlert.is_resolved == False,
    ).first()
    return existing is not None


def _fire_alert(
    db: Session,
    alert_type: str,
    severity: str,
    message: str,
    source: str = "system",
    metric_name: Optional[str] = None,
    metric_value: Optional[float] = None,
    threshold: Optional[float] = None,
) -> Optional[DataAlert]:
    """Create a new DataAlert if not on cooldown."""
    if _is_on_cooldown(db, alert_type, source):
        logger.debug(f"Alert {alert_type}/{source} on cooldown — skipped")
        return None

    alert = DataAlert(
        alert_type=alert_type,
        severity=severity,
        source=source,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold=threshold,
        message=message,
        cooldown_key=_cooldown_key(alert_type, source),
    )
    db.add(alert)
    logger.warning(f"[{severity}] {alert_type} — {message}")
    return alert


def run_alert_scan(db: Session, pipeline_stats: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Full alert scan. Should be called after every pipeline run.
    Returns count of alerts fired.
    """
    alerts_fired = 0
    now = datetime.utcnow()

    # ── 1. Broken Link Rate ───────────────────────────────────
    try:
        from app.broken_link_monitor import get_broken_link_rate
        broken_rate = get_broken_link_rate(db)
        if broken_rate >= THRESHOLDS["broken_links_critical"]:
            a = _fire_alert(
                db, "BROKEN_LINKS_HIGH", "CRITICAL",
                f"Broken link rate is {broken_rate:.1f}% — CRITICAL threshold {THRESHOLDS['broken_links_critical']}% exceeded",
                "system", "broken_link_rate_pct", broken_rate, THRESHOLDS["broken_links_critical"]
            )
            alerts_fired += 1 if a else 0
        elif broken_rate >= THRESHOLDS["broken_links_warning"]:
            a = _fire_alert(
                db, "BROKEN_LINKS_HIGH", "WARNING",
                f"Broken link rate is {broken_rate:.1f}% — warning threshold {THRESHOLDS['broken_links_warning']}% exceeded",
                "system", "broken_link_rate_pct", broken_rate, THRESHOLDS["broken_links_warning"]
            )
            alerts_fired += 1 if a else 0
    except Exception as e:
        logger.error(f"Alert scan: broken link check failed: {e}")

    # ── 2. Freshness ─────────────────────────────────────────
    try:
        from app.freshness_monitor import get_freshness_distribution
        dist = get_freshness_distribution(db)
        within_7_pct = dist.get("within_7_days_pct", 100.0)
        if within_7_pct < THRESHOLDS["freshness_critical_pct"]:
            a = _fire_alert(
                db, "FRESHNESS_LOW", "CRITICAL",
                f"Only {within_7_pct}% of jobs are ≤7 days old — CRITICAL (target ≥80%)",
                "system", "within_7d_pct", within_7_pct, THRESHOLDS["freshness_critical_pct"]
            )
            alerts_fired += 1 if a else 0
        elif within_7_pct < THRESHOLDS["freshness_warning_pct"]:
            a = _fire_alert(
                db, "FRESHNESS_LOW", "WARNING",
                f"Only {within_7_pct}% of jobs are ≤7 days old — target is ≥80%",
                "system", "within_7d_pct", within_7_pct, THRESHOLDS["freshness_warning_pct"]
            )
            alerts_fired += 1 if a else 0
    except Exception as e:
        logger.error(f"Alert scan: freshness check failed: {e}")

    # ── 3. India Ratio ───────────────────────────────────────
    try:
        total_active = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE"
        ).scalar() or 0
        india_active = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.is_india_job == True,
        ).scalar() or 0

        if total_active > 0:
            india_pct = round((india_active / total_active) * 100, 1)
            if india_pct < THRESHOLDS["india_ratio_warning"]:
                a = _fire_alert(
                    db, "INDIA_RATIO_LOW", "WARNING",
                    f"India opportunity ratio is {india_pct}% — target is ≥{THRESHOLDS['india_ratio_warning']}%",
                    "system", "india_ratio_pct", india_pct, THRESHOLDS["india_ratio_warning"]
                )
                alerts_fired += 1 if a else 0
    except Exception as e:
        logger.error(f"Alert scan: India ratio check failed: {e}")

    # ── 4. Pipeline failure stats (from passed stats) ─────────
    if pipeline_stats:
        collectors_run = pipeline_stats.get("collectors_run", 0)
        collectors_failed = pipeline_stats.get("collectors_failed", 0)
        collectors_zero = pipeline_stats.get("collectors_zero_result", 0)
        collectors_slow = pipeline_stats.get("collectors_slow", 0)

        if collectors_failed > 0:
            a = _fire_alert(
                db, "PIPELINE_FAILED", "CRITICAL",
                f"{collectors_failed}/{collectors_run} collectors FAILED in last pipeline run",
                "pipeline", "collectors_failed", float(collectors_failed)
            )
            alerts_fired += 1 if a else 0

        if collectors_zero > 0:
            a = _fire_alert(
                db, "COLLECTOR_ZERO_RESULT", "WARNING",
                f"{collectors_zero} collectors returned zero results in last run",
                "pipeline", "collectors_zero_result", float(collectors_zero)
            )
            alerts_fired += 1 if a else 0

        if collectors_slow > 0:
            a = _fire_alert(
                db, "COLLECTOR_SLOW", "INFO",
                f"{collectors_slow} collectors exceeded 30s runtime threshold",
                "pipeline", "collectors_slow", float(collectors_slow)
            )
            alerts_fired += 1 if a else 0

    # ── 5. CollectorHealth — check for degraded collectors ────
    try:
        degraded_collectors = db.query(CollectorHealth).filter(
            CollectorHealth.success_rate < 50.0,
            CollectorHealth.status != "Paused",
        ).all()

        for collector in degraded_collectors:
            a = _fire_alert(
                db, "COLLECTOR_DEGRADED", "WARNING",
                f"Collector '{collector.collector_name}' has success_rate={collector.success_rate:.0f}% (below 50%)",
                collector.collector_name,
                "success_rate", collector.success_rate, 50.0
            )
            alerts_fired += 1 if a else 0
    except Exception as e:
        logger.error(f"Alert scan: collector health check failed: {e}")

    # ── 6. Learning resources ─────────────────────────────────
    try:
        from app.models import LearningResource
        total_resources = db.query(func.count(LearningResource.id)).scalar() or 0
        invalid_resources = db.query(func.count(LearningResource.id)).filter(
            LearningResource.status == "INVALID_RESOURCE"
        ).scalar() or 0
        if total_resources > 0:
            invalid_pct = round((invalid_resources / total_resources) * 100, 1)
            if invalid_pct >= THRESHOLDS["resource_invalid_warning"]:
                a = _fire_alert(
                    db, "RESOURCE_INVALID_HIGH", "WARNING",
                    f"{invalid_pct}% of learning resources are INVALID — {invalid_resources}/{total_resources}",
                    "system", "resource_invalid_pct", invalid_pct, THRESHOLDS["resource_invalid_warning"]
                )
                alerts_fired += 1 if a else 0
    except Exception as e:
        logger.debug(f"Alert scan: learning resource check skipped: {e}")

    db.commit()

    return {
        "alerts_fired": alerts_fired,
        "scanned_at": now.isoformat(),
        "thresholds": THRESHOLDS,
    }


def get_active_alerts(db: Session, limit: int = 50) -> List[Dict]:
    """Return unresolved data alerts."""
    alerts = (
        db.query(DataAlert)
        .filter(DataAlert.is_resolved == False)
        .order_by(DataAlert.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "source": a.source,
            "metric_name": a.metric_name,
            "metric_value": a.metric_value,
            "threshold": a.threshold,
            "message": a.message,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


def resolve_alert(db: Session, alert_id: int) -> bool:
    """Mark an alert as resolved."""
    alert = db.query(DataAlert).filter(DataAlert.id == alert_id).first()
    if not alert:
        return False
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return True


def resolve_all_alerts(db: Session, alert_type: Optional[str] = None) -> int:
    """Resolve all (or type-specific) alerts."""
    q = db.query(DataAlert).filter(DataAlert.is_resolved == False)
    if alert_type:
        q = q.filter(DataAlert.alert_type == alert_type)
    alerts = q.all()
    for a in alerts:
        a.is_resolved = True
        a.resolved_at = datetime.utcnow()
    db.commit()
    return len(alerts)
