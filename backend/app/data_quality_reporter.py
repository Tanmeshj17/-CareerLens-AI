"""
Phase 11.4 T14: Data Quality Reporter
Orchestrates all quality monitors into a single composite score (0-100).

Weighted scoring:
  Freshness        25% — >80% jobs ≤7 days
  Broken Links     20% — <2% broken
  Duplicates       20% — <1% duplicate rate
  Collector Health 20% — >95% success rate
  India Ratio      15% — >75% India opportunities

Generates all quality reports and saves them to disk.
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Opportunity, CollectorHealth

logger = logging.getLogger("data_quality_reporter")

# Report output directory
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def _ensure_report_dir():
    os.makedirs(REPORT_DIR, exist_ok=True)


def compute_data_quality_score(db: Session) -> Dict[str, Any]:
    """
    Compute composite data quality score (0-100).
    """
    scores = {}
    details = {}

    # ── Freshness (25%) ───────────────────────────────────────
    try:
        from app.freshness_monitor import get_freshness_distribution
        dist = get_freshness_distribution(db)
        within_7_pct = dist.get("within_7_days_pct", 0.0)
        # Score: 100 if ≥80%, proportional below
        freshness_sub = min(100, round((within_7_pct / 80.0) * 100)) if within_7_pct < 80 else 100
        scores["freshness"] = freshness_sub
        details["freshness"] = {
            "score": freshness_sub,
            "within_7_days_pct": within_7_pct,
            "total_active": dist.get("total_active", 0),
            "target": "≥80% within 7 days",
            "target_met": within_7_pct >= 80.0,
        }
    except Exception as e:
        scores["freshness"] = 0
        details["freshness"] = {"error": str(e)}
        logger.error(f"Quality score: freshness check failed: {e}")

    # ── Broken Links (20%) ────────────────────────────────────
    try:
        from app.broken_link_monitor import get_broken_link_rate
        broken_rate = get_broken_link_rate(db)
        # Score: 100 if <2%, 0 if ≥20%, linear between
        if broken_rate < 2.0:
            link_sub = 100
        elif broken_rate >= 20.0:
            link_sub = 0
        else:
            link_sub = round(100 - ((broken_rate - 2.0) / 18.0 * 100))
        scores["broken_links"] = link_sub
        details["broken_links"] = {
            "score": link_sub,
            "broken_rate_pct": broken_rate,
            "target": "<2% broken",
            "target_met": broken_rate < 2.0,
        }
    except Exception as e:
        scores["broken_links"] = 50  # Default if can't check
        details["broken_links"] = {"error": str(e)}

    # ── Duplicate Rate (20%) ──────────────────────────────────
    try:
        total = db.query(func.count(Opportunity.id)).scalar() or 1
        # Approximate duplicate rate from collector health metrics
        total_dupes = db.query(func.sum(CollectorHealth.duplicates_removed)).scalar() or 0
        dup_rate = round((total_dupes / total) * 100, 2) if total > 0 else 0.0
        if dup_rate < 1.0:
            dup_sub = 100
        elif dup_rate >= 20.0:
            dup_sub = 0
        else:
            dup_sub = round(100 - ((dup_rate - 1.0) / 19.0 * 100))
        scores["duplicates"] = dup_sub
        details["duplicates"] = {
            "score": dup_sub,
            "duplicate_rate_pct": dup_rate,
            "total_dupes_removed": int(total_dupes),
            "target": "<1% duplicate rate",
            "target_met": dup_rate < 1.0,
        }
    except Exception as e:
        scores["duplicates"] = 50
        details["duplicates"] = {"error": str(e)}

    # ── Collector Success Rate (20%) ──────────────────────────
    try:
        collectors = db.query(CollectorHealth).filter(
            CollectorHealth.status != "Paused"
        ).all()
        if collectors:
            avg_success = sum(c.success_rate or 0 for c in collectors) / len(collectors)
        else:
            avg_success = 100.0
        # Score: 100 if ≥95%, 0 if <50%
        if avg_success >= 95.0:
            collector_sub = 100
        elif avg_success < 50.0:
            collector_sub = 0
        else:
            collector_sub = round((avg_success - 50.0) / 45.0 * 100)
        scores["collector_health"] = collector_sub
        details["collector_health"] = {
            "score": collector_sub,
            "avg_success_rate": round(avg_success, 1),
            "total_collectors": len(collectors),
            "target": ">95% success rate",
            "target_met": avg_success >= 95.0,
        }
    except Exception as e:
        scores["collector_health"] = 50
        details["collector_health"] = {"error": str(e)}

    # ── India Ratio (15%) ─────────────────────────────────────
    try:
        total_active = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE"
        ).scalar() or 1
        india_active = db.query(func.count(Opportunity.id)).filter(
            Opportunity.status == "ACTIVE",
            Opportunity.is_india_job == True,
        ).scalar() or 0
        india_pct = round((india_active / total_active) * 100, 1) if total_active > 0 else 0.0
        if india_pct >= 75.0:
            india_sub = 100
        elif india_pct < 30.0:
            india_sub = 0
        else:
            india_sub = round((india_pct - 30.0) / 45.0 * 100)
        scores["india_ratio"] = india_sub
        details["india_ratio"] = {
            "score": india_sub,
            "india_pct": india_pct,
            "india_count": india_active,
            "total_active": total_active,
            "target": "≥75% India opportunities",
            "target_met": india_pct >= 75.0,
        }
    except Exception as e:
        scores["india_ratio"] = 50
        details["india_ratio"] = {"error": str(e)}

    # ── Composite Score ───────────────────────────────────────
    weights = {
        "freshness": 0.25,
        "broken_links": 0.20,
        "duplicates": 0.20,
        "collector_health": 0.20,
        "india_ratio": 0.15,
    }
    composite = round(sum(scores[k] * w for k, w in weights.items()))
    grade = "A" if composite >= 90 else "B" if composite >= 75 else "C" if composite >= 60 else "D" if composite >= 40 else "F"

    return {
        "composite_score": composite,
        "grade": grade,
        "scores": scores,
        "details": details,
        "weights": weights,
        "computed_at": datetime.utcnow().isoformat(),
        "targets_met": sum(1 for d in details.values() if d.get("target_met")),
        "targets_total": len(details),
    }


def generate_quality_score_report(db: Session) -> str:
    """Generate a markdown data quality score report."""
    data = compute_data_quality_score(db)
    now = datetime.utcnow()
    composite = data["composite_score"]
    grade = data["grade"]

    grade_bar = "█" * (composite // 10) + "░" * (10 - composite // 10)

    lines = [
        "# Data Quality Score Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"## Overall Score: **{composite}/100** — Grade **{grade}**",
        f"`{grade_bar}` {composite}%",
        "",
        f"**Targets Met:** {data['targets_met']}/{data['targets_total']}",
        "",
        "## Domain Scores",
        "",
        "| Domain | Weight | Score | Target | Met? |",
        "|---|---|---|---|---|",
    ]

    domain_labels = {
        "freshness": "Freshness",
        "broken_links": "Broken Links",
        "duplicates": "Duplicate Rate",
        "collector_health": "Collector Health",
        "india_ratio": "India Ratio",
    }

    for key, label in domain_labels.items():
        score = data["scores"].get(key, 0)
        detail = data["details"].get(key, {})
        weight = int(data["weights"].get(key, 0) * 100)
        target = detail.get("target", "—")
        met = "✅" if detail.get("target_met") else "❌"
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        lines.append(f"| {label} | {weight}% | {score}/100 `{bar}` | {target} | {met} |")

    lines.extend([
        "",
        "## Domain Details",
    ])

    for key, label in domain_labels.items():
        detail = data["details"].get(key, {})
        lines.append(f"\n### {label}")
        for k, v in detail.items():
            if k not in ("score", "target", "target_met", "error"):
                lines.append(f"- **{k}:** {v}")
        if "error" in detail:
            lines.append(f"- ⚠️ Error: {detail['error']}")

    return "\n".join(lines)


def generate_source_coverage_report(db: Session) -> str:
    """Generate source coverage markdown report (T3)."""
    now = datetime.utcnow()

    # Top companies
    top_companies = (
        db.query(Opportunity.company, func.count(Opportunity.id))
        .filter(Opportunity.status == "ACTIVE", Opportunity.company != None)
        .group_by(Opportunity.company)
        .order_by(func.count(Opportunity.id).desc())
        .limit(20)
        .all()
    )

    # Top locations
    top_locations = (
        db.query(Opportunity.location, func.count(Opportunity.id))
        .filter(Opportunity.status == "ACTIVE", Opportunity.location != None)
        .group_by(Opportunity.location)
        .order_by(func.count(Opportunity.id).desc())
        .limit(20)
        .all()
    )

    # By source_type
    by_source_type = (
        db.query(Opportunity.source_type, func.count(Opportunity.id))
        .filter(Opportunity.status == "ACTIVE")
        .group_by(Opportunity.source_type)
        .all()
    )

    # By employment type
    by_job_type = (
        db.query(Opportunity.job_type, func.count(Opportunity.id))
        .filter(Opportunity.status == "ACTIVE", Opportunity.job_type != None)
        .group_by(Opportunity.job_type)
        .order_by(func.count(Opportunity.id).desc())
        .all()
    )

    lines = [
        "# Source Coverage Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## Top 20 Hiring Companies",
        "",
        "| Rank | Company | Active Jobs |",
        "|---|---|---|",
    ]
    for i, (company, count) in enumerate(top_companies, 1):
        lines.append(f"| {i} | {company} | {count:,} |")

    lines.extend([
        "",
        "## Top 20 Hiring Locations",
        "",
        "| Rank | Location | Active Jobs |",
        "|---|---|---|",
    ])
    for i, (location, count) in enumerate(top_locations, 1):
        lines.append(f"| {i} | {location} | {count:,} |")

    lines.extend([
        "",
        "## By Source Type",
        "",
        "| Source Type | Count |",
        "|---|---|",
    ])
    for source_type, count in sorted(by_source_type, key=lambda x: -x[1]):
        lines.append(f"| {source_type or 'Unknown'} | {count:,} |")

    lines.extend([
        "",
        "## By Employment Type",
        "",
        "| Type | Count |",
        "|---|---|",
    ])
    for job_type, count in by_job_type:
        lines.append(f"| {job_type} | {count:,} |")

    return "\n".join(lines)


def generate_collector_health_report(db: Session) -> str:
    """Generate collector health markdown report (T1/T2)."""
    now = datetime.utcnow()
    collectors = (
        db.query(CollectorHealth)
        .order_by(CollectorHealth.collector_score.desc())
        .all()
    )

    lines = [
        "# Collector Health Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"**Total Collectors Tracked:** {len(collectors)}",
        "",
        "## Collector Health Summary",
        "",
        "| Collector | Status | Score | Tier | Success% | Broken% | Dup% | Last Run |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for c in collectors:
        status_icon = "✅" if c.status == "Active" else "⚠️" if c.status == "Degraded" else "🔴"
        last_run = c.last_run.strftime('%Y-%m-%d') if c.last_run else "Never"
        lines.append(
            f"| {c.collector_name} | {status_icon} {c.status} | "
            f"{c.collector_score:.0f} | {c.roi_tier} | "
            f"{c.success_rate:.0f}% | {c.broken_links_pct or 0:.1f}% | "
            f"{c.duplicate_pct or 0:.1f}% | {last_run} |"
        )

    if not collectors:
        lines.append("| — | No collectors tracked yet | — | — | — | — | — | — |")

    return "\n".join(lines)


def generate_all_reports(db: Session, save_to_disk: bool = True) -> Dict[str, str]:
    """
    Generate all 9 quality reports.
    Returns dict of report_name → content.
    """
    _ensure_report_dir()

    reports = {
        "CollectorHealthReport": generate_collector_health_report(db),
        "SourceCoverageReport": generate_source_coverage_report(db),
        "FreshnessReport": _get_freshness_report(db),
        "BrokenLinkReport": _get_broken_link_report(db),
        "LifecycleReport": _get_lifecycle_report(db),
        "PipelineObservabilityReport": _get_pipeline_report(db),
        "DataQualityScore": generate_quality_score_report(db),
    }

    if save_to_disk:
        timestamp = now_str = datetime.utcnow().strftime("%Y%m%d_%H%M")
        for name, content in reports.items():
            path = os.path.join(REPORT_DIR, f"{name}_{timestamp}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Report saved: {path}")

    return reports


def _get_freshness_report(db: Session) -> str:
    try:
        from app.freshness_monitor import generate_freshness_report
        return generate_freshness_report(db)
    except Exception as e:
        return f"# Freshness Report\n\n⚠️ Error generating report: {e}"


def _get_broken_link_report(db: Session) -> str:
    try:
        from app.broken_link_monitor import generate_broken_link_report
        return generate_broken_link_report(db)
    except Exception as e:
        return f"# Broken Link Report\n\n⚠️ Error generating report: {e}"


def _get_lifecycle_report(db: Session) -> str:
    try:
        from app.lifecycle_validator import generate_lifecycle_report
        return generate_lifecycle_report(db)
    except Exception as e:
        return f"# Lifecycle Report\n\n⚠️ Error generating report: {e}"


def _get_pipeline_report(db: Session) -> str:
    try:
        from app.pipeline_observer import generate_pipeline_observability_report
        return generate_pipeline_observability_report(db)
    except Exception as e:
        return f"# Pipeline Observability Report\n\n⚠️ Error generating report: {e}"
