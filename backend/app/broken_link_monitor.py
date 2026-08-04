"""
Phase 11.4 T9: Broken Link Monitor
Tracks broken, redirected, timed-out, and SSL-failed links.
Reports per-collector and overall broken link rates.
Target: broken link rate < 2%.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Opportunity

logger = logging.getLogger("broken_link_monitor")

# Define which apply_url_status values count as "broken"
BROKEN_STATUSES = {"BROKEN", "HOMEPAGE_ONLY", "EXPIRED", "CLOSED"}
REDIRECT_STATUSES = {"CAREER_BOARD", "BROWSER_VERIFICATION_REQUIRED"}
VERIFIED_STATUSES = {"VERIFIED_DIRECT", "VERIFIED_POSTING"}


def get_broken_link_stats(db: Session) -> Dict[str, Any]:
    """
    Returns overall broken link statistics.
    """
    total = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.apply_url != None,
    ).scalar() or 0

    broken = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.apply_url_status.in_(BROKEN_STATUSES),
    ).scalar() or 0

    verified = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.apply_url_status.in_(VERIFIED_STATUSES),
    ).scalar() or 0

    redirected = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.apply_url_status.in_(REDIRECT_STATUSES),
    ).scalar() or 0

    unknown = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.apply_url_status == "UNKNOWN",
    ).scalar() or 0

    broken_rate = round((broken / total) * 100, 2) if total > 0 else 0.0
    verified_rate = round((verified / total) * 100, 2) if total > 0 else 0.0

    # Per-status breakdown
    status_breakdown = (
        db.query(
            Opportunity.apply_url_status,
            func.count(Opportunity.id)
        )
        .filter(
            Opportunity.status == "ACTIVE",
            Opportunity.apply_url != None,
        )
        .group_by(Opportunity.apply_url_status)
        .all()
    )

    return {
        "total_with_url": total,
        "broken_count": broken,
        "broken_rate_pct": broken_rate,
        "verified_count": verified,
        "verified_rate_pct": verified_rate,
        "redirected_count": redirected,
        "unknown_count": unknown,
        "target_met": broken_rate < 2.0,
        "status_breakdown": {s: c for s, c in status_breakdown},
        "checked_at": datetime.utcnow().isoformat(),
    }


def get_broken_link_rate(db: Session) -> float:
    """Quick accessor — returns broken link rate as a percentage."""
    stats = get_broken_link_stats(db)
    return stats.get("broken_rate_pct", 0.0)


def get_collector_broken_stats(db: Session) -> List[Dict[str, Any]]:
    """
    Returns broken link stats per collector.
    """
    results = []
    collectors = (
        db.query(Opportunity.collected_by, func.count(Opportunity.id))
        .filter(
            Opportunity.status == "ACTIVE",
            Opportunity.collected_by != None,
            Opportunity.apply_url != None,
        )
        .group_by(Opportunity.collected_by)
        .order_by(func.count(Opportunity.id).desc())
        .limit(30)
        .all()
    )

    for collector, total in collectors:
        broken = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.collected_by == collector,
            Opportunity.apply_url_status.in_(BROKEN_STATUSES),
        ).scalar() or 0
        verified = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.collected_by == collector,
            Opportunity.apply_url_status.in_(VERIFIED_STATUSES),
        ).scalar() or 0
        rate = round((broken / total) * 100, 1) if total > 0 else 0.0
        results.append({
            "collector": collector,
            "total": total,
            "broken": broken,
            "broken_rate_pct": rate,
            "verified": verified,
            "verified_pct": round((verified / total) * 100, 1) if total > 0 else 0.0,
        })

    return results


def generate_broken_link_report(db: Session) -> str:
    """Generate a markdown broken link report."""
    stats = get_broken_link_stats(db)
    collector_stats = get_collector_broken_stats(db)
    now = datetime.utcnow()

    lines = [
        "# Broken Link Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"**Total Active Jobs with URL:** {stats['total_with_url']:,}",
        f"**Broken Links:** {stats['broken_count']:,} ({stats['broken_rate_pct']}%)",
        f"**Verified Links:** {stats['verified_count']:,} ({stats['verified_rate_pct']}%)",
        f"**Unknown Status:** {stats['unknown_count']:,}",
        f"**Target Met (<2% broken):** {'✅ YES' if stats['target_met'] else '❌ NO'}",
        "",
        "## Link Status Breakdown",
        "",
        "| Status | Count |",
        "|---|---|",
    ]

    for status, count in sorted(stats.get("status_breakdown", {}).items()):
        lines.append(f"| {status} | {count:,} |")

    lines.extend([
        "",
        "## Per-Collector Broken Link Analysis",
        "",
        "| Collector | Total | Broken | Broken % | Verified % |",
        "|---|---|---|---|---|",
    ])

    for c in collector_stats:
        status_icon = "✅" if c["broken_rate_pct"] < 2 else "⚠️" if c["broken_rate_pct"] < 10 else "❌"
        lines.append(
            f"| {c['collector']} | {c['total']:,} | {c['broken']:,} | "
            f"{status_icon} {c['broken_rate_pct']}% | {c['verified_pct']}% |"
        )

    return "\n".join(lines)
