"""
Phase 11.4 T8: Freshness Monitor
Tracks the age distribution of active opportunities.
Goal: >80% of active opportunities should be ≤7 days old.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import Opportunity

logger = logging.getLogger("freshness_monitor")

# Age buckets (days)
BUCKETS = [
    (0, 0, "today"),
    (1, 1, "1_day"),
    (2, 3, "2_3_days"),
    (4, 7, "4_7_days"),
    (8, 14, "8_14_days"),
    (15, 30, "15_30_days"),
    (31, None, "30_plus_days"),
]


def get_freshness_distribution(db: Session) -> Dict[str, Any]:
    """
    Returns a breakdown of active opportunities by age bucket.
    """
    now = datetime.utcnow()
    total = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "ACTIVE"
    ).scalar() or 0

    if total == 0:
        return {
            "total_active": 0,
            "buckets": {},
            "within_7_days_pct": 0.0,
            "within_7_days_count": 0,
            "freshness_score": 0,
        }

    buckets: Dict[str, int] = {}
    within_7 = 0

    for low, high, label in BUCKETS:
        low_dt = now - timedelta(days=(high if high is not None else 9999))
        high_dt = now - timedelta(days=low)

        q = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.posted_date <= high_dt,
        )
        if high is not None:
            q = q.filter(Opportunity.posted_date > low_dt)

        count = q.scalar() or 0
        buckets[label] = count

        if high is not None and high <= 7:
            within_7 += count
        elif low == 0 and high == 0:
            within_7 += count

    within_7_pct = round((within_7 / total) * 100, 1) if total > 0 else 0.0
    freshness_score = _compute_freshness_score(buckets, total)

    return {
        "total_active": total,
        "buckets": buckets,
        "within_7_days_count": within_7,
        "within_7_days_pct": within_7_pct,
        "freshness_score": freshness_score,
        "target_met": within_7_pct >= 80.0,
        "checked_at": now.isoformat(),
    }


def _compute_freshness_score(buckets: Dict[str, int], total: int) -> int:
    """
    Freshness Score (0-100):
    Weighted average age penalty. 100 = all jobs from today.
    """
    if total == 0:
        return 0

    weights = {
        "today": 1.0,
        "1_day": 0.9,
        "2_3_days": 0.75,
        "4_7_days": 0.5,
        "8_14_days": 0.25,
        "15_30_days": 0.1,
        "30_plus_days": 0.0,
    }

    weighted_sum = sum(
        buckets.get(label, 0) * w for label, w in weights.items()
    )
    return round((weighted_sum / total) * 100)


def get_freshness_score(db: Session) -> int:
    """Quick accessor — returns freshness score 0-100."""
    dist = get_freshness_distribution(db)
    return dist.get("freshness_score", 0)


def get_freshness_report_data(db: Session) -> Dict[str, Any]:
    """
    Extended freshness report including per-collector breakdown.
    """
    dist = get_freshness_distribution(db)
    now = datetime.utcnow()

    # Per-collector freshness
    collector_freshness = []
    collectors = (
        db.query(Opportunity.collected_by, func.count(Opportunity.id))
        .filter(
            Opportunity.status == "ACTIVE",
            Opportunity.collected_by != None,
        )
        .group_by(Opportunity.collected_by)
        .order_by(func.count(Opportunity.id).desc())
        .limit(20)
        .all()
    )

    for collector, count in collectors:
        recent = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.collected_by == collector,
            Opportunity.posted_date >= now - timedelta(days=7),
        ).scalar() or 0
        pct = round((recent / count) * 100, 1) if count > 0 else 0
        collector_freshness.append({
            "collector": collector,
            "total": count,
            "fresh_7d": recent,
            "fresh_pct": pct,
        })

    dist["collector_breakdown"] = collector_freshness
    return dist


def generate_freshness_report(db: Session) -> str:
    """Generate a markdown freshness report."""
    data = get_freshness_report_data(db)
    now = datetime.utcnow()

    buckets = data.get("buckets", {})
    total = data.get("total_active", 0)

    def pct(val):
        return f"{round((val/total)*100, 1)}%" if total > 0 else "0%"

    lines = [
        "# Freshness Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"**Total Active Opportunities:** {total:,}",
        f"**Freshness Score:** {data.get('freshness_score', 0)}/100",
        f"**Within 7 Days:** {data.get('within_7_days_count', 0):,} ({data.get('within_7_days_pct', 0)}%)",
        f"**Target Met (≥80% within 7d):** {'✅ YES' if data.get('target_met') else '❌ NO'}",
        "",
        "## Age Distribution",
        "",
        "| Bucket | Count | % of Total |",
        "|---|---|---|",
        f"| Today | {buckets.get('today', 0):,} | {pct(buckets.get('today', 0))} |",
        f"| 1 Day | {buckets.get('1_day', 0):,} | {pct(buckets.get('1_day', 0))} |",
        f"| 2–3 Days | {buckets.get('2_3_days', 0):,} | {pct(buckets.get('2_3_days', 0))} |",
        f"| 4–7 Days | {buckets.get('4_7_days', 0):,} | {pct(buckets.get('4_7_days', 0))} |",
        f"| 8–14 Days | {buckets.get('8_14_days', 0):,} | {pct(buckets.get('8_14_days', 0))} |",
        f"| 15–30 Days | {buckets.get('15_30_days', 0):,} | {pct(buckets.get('15_30_days', 0))} |",
        f"| 30+ Days | {buckets.get('30_plus_days', 0):,} | {pct(buckets.get('30_plus_days', 0))} |",
        "",
        "## Top Collectors by Freshness",
        "",
        "| Collector | Total | Fresh (≤7d) | Fresh % |",
        "|---|---|---|---|",
    ]

    for c in data.get("collector_breakdown", []):
        status = "✅" if c["fresh_pct"] >= 80 else "⚠️" if c["fresh_pct"] >= 50 else "❌"
        lines.append(
            f"| {c['collector']} | {c['total']:,} | {c['fresh_7d']:,} | {status} {c['fresh_pct']}% |"
        )

    return "\n".join(lines)
