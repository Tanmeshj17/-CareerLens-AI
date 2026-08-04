"""
Phase 11.4 T10: Lifecycle Validator
Audits that opportunity lifecycle transitions are happening correctly.
Detects stuck jobs, missing transitions, and integrity violations.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import Opportunity

logger = logging.getLogger("lifecycle_validator")

# Thresholds
STALE_THRESHOLD_DAYS = 7
ARCHIVE_THRESHOLD_DAYS = 30
CLOSED_THRESHOLD_DAYS = 60


def validate_lifecycle_transitions(db: Session) -> Dict[str, Any]:
    """
    Audit lifecycle transitions and auto-fix stuck jobs.
    Returns a validation report.
    """
    now = datetime.utcnow()
    issues = []
    fixed = 0

    # ── 1. ACTIVE jobs that should be STALE (>7 days) ─────────
    stale_cutoff = now - timedelta(days=STALE_THRESHOLD_DAYS)
    stuck_active_count = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.posted_date < stale_cutoff,
        Opportunity.lifecycle_status.in_(["NEW", "ACTIVE"]),
    ).scalar() or 0

    if stuck_active_count > 0:
        issues.append({
            "issue": "ACTIVE_SHOULD_BE_STALE",
            "severity": "WARNING",
            "count": stuck_active_count,
            "description": f"{stuck_active_count} jobs are ACTIVE but older than {STALE_THRESHOLD_DAYS} days — should be STALE",
        })
        # Auto-fix: update status
        db.query(Opportunity).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.posted_date < stale_cutoff,
            Opportunity.lifecycle_status.in_(["NEW", "ACTIVE"]),
        ).update({"status": "STALE", "lifecycle_status": "STALE"}, synchronize_session=False)
        fixed += stuck_active_count
        logger.info(f"Lifecycle fix: {stuck_active_count} ACTIVE→STALE")

    # ── 2. STALE jobs that should be ARCHIVED (>30 days) ──────
    archive_cutoff = now - timedelta(days=ARCHIVE_THRESHOLD_DAYS)
    stuck_stale_count = db.query(func.count(Opportunity.id)).filter(
        or_(Opportunity.status == "STALE", Opportunity.lifecycle_status == "STALE"),
        Opportunity.posted_date < archive_cutoff,
    ).scalar() or 0

    if stuck_stale_count > 0:
        issues.append({
            "issue": "STALE_SHOULD_BE_ARCHIVED",
            "severity": "INFO",
            "count": stuck_stale_count,
            "description": f"{stuck_stale_count} STALE jobs older than {ARCHIVE_THRESHOLD_DAYS} days — should be ARCHIVED",
        })
        db.query(Opportunity).filter(
            or_(Opportunity.status == "STALE", Opportunity.lifecycle_status == "STALE"),
            Opportunity.posted_date < archive_cutoff,
        ).update({"status": "ARCHIVED", "lifecycle_status": "ARCHIVED"}, synchronize_session=False)
        fixed += stuck_stale_count
        logger.info(f"Lifecycle fix: {stuck_stale_count} STALE→ARCHIVED")

    # ── 3. Expired jobs (past expires_at) still ACTIVE ────────
    expired_still_active = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.expires_at != None,
        Opportunity.expires_at < now,
    ).scalar() or 0

    if expired_still_active > 0:
        issues.append({
            "issue": "PAST_EXPIRY_STILL_ACTIVE",
            "severity": "WARNING",
            "count": expired_still_active,
            "description": f"{expired_still_active} jobs are past their expires_at date but still ACTIVE",
        })
        db.query(Opportunity).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.expires_at != None,
            Opportunity.expires_at < now,
        ).update({"status": "CLOSED", "expired_reason": "PAST_EXPIRY_DATE"}, synchronize_session=False)
        fixed += expired_still_active
        logger.info(f"Lifecycle fix: {expired_still_active} expired→CLOSED")

    db.commit()

    # ── 4. Status distribution audit ─────────────────────────
    status_distribution = (
        db.query(Opportunity.status, func.count(Opportunity.id))
        .group_by(Opportunity.status)
        .all()
    )
    status_dist = {s: c for s, c in status_distribution}

    # ── 5. Lifecycle consistency check ───────────────────────
    # Find jobs where status != lifecycle_status (should mostly align)
    inconsistent = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status != Opportunity.lifecycle_status,
        Opportunity.status != None,
        Opportunity.lifecycle_status != None,
    ).scalar() or 0

    if inconsistent > 0:
        issues.append({
            "issue": "STATUS_LIFECYCLE_MISMATCH",
            "severity": "INFO",
            "count": inconsistent,
            "description": f"{inconsistent} jobs have mismatched status vs lifecycle_status fields",
        })

    return {
        "validated_at": now.isoformat(),
        "issues_found": len(issues),
        "auto_fixed": fixed,
        "issues": issues,
        "status_distribution": status_dist,
        "is_healthy": len([i for i in issues if i["severity"] in ("WARNING", "CRITICAL")]) == 0,
    }


def generate_lifecycle_report(db: Session) -> str:
    """Generate a markdown lifecycle validation report."""
    data = validate_lifecycle_transitions(db)
    now = datetime.utcnow()

    lines = [
        "# Lifecycle Validation Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"**Issues Found:** {data['issues_found']}",
        f"**Auto-Fixed:** {data['auto_fixed']}",
        f"**System Healthy:** {'✅ YES' if data['is_healthy'] else '⚠️ NO'}",
        "",
        "## Status Distribution",
        "",
        "| Status | Count |",
        "|---|---|",
    ]

    for status, count in sorted(data.get("status_distribution", {}).items()):
        lines.append(f"| {status} | {count:,} |")

    if data["issues"]:
        lines.extend(["", "## Issues Detected", ""])
        for issue in data["issues"]:
            icon = "🔴" if issue["severity"] == "CRITICAL" else "🟡" if issue["severity"] == "WARNING" else "🔵"
            lines.append(f"- {icon} **{issue['issue']}** [{issue['severity']}]: {issue['description']}")

    return "\n".join(lines)
