"""
Phase 8.7 — Opportunity History Engine
=======================================
Full lifecycle audit trail for every opportunity.
Powers:
  - "Recently Updated" feeds
  - Salary change tracking
  - Link repair detection
  - Hiring trend signals
  - Future job-change notifications
  - Job detail timeline view
"""
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models import Opportunity, OpportunityHistory

logger = logging.getLogger("opportunity_history")

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

EVENT_SEVERITY = {
    # CRITICAL
    "EXPIRED": "CRITICAL",
    "REMOVED": "CRITICAL",
    "LINK_BROKEN": "HIGH",
    # HIGH
    "STATUS_CHANGED": "HIGH",
    "LIFECYCLE_CHANGED": "HIGH",
    "REACTIVATED": "HIGH",
    # MEDIUM
    "SALARY_CHANGED": "MEDIUM",
    "EXPERIENCE_CHANGED": "MEDIUM",
    "LINK_FIXED": "MEDIUM",
    "LINK_CHANGED": "MEDIUM",
    "COMPANY_CHANGED": "MEDIUM",
    # LOW
    "DESCRIPTION_CHANGED": "LOW",
    "SKILLS_CHANGED": "LOW",
    "LOCATION_CHANGED": "LOW",
    "CONFIDENCE_CHANGED": "LOW",
    "COMPLETENESS_CHANGED": "LOW",
    "VERIFIED": "LOW",
    "REVERIFIED": "LOW",
    "UPDATED": "LOW",
    "FIRST_SEEN": "LOW",
    "DUPLICATE_MERGED": "LOW",
    "MANUAL_EDIT": "LOW",
}

# Points added to change_score per event severity
SEVERITY_SCORE = {"CRITICAL": 30, "HIGH": 15, "MEDIUM": 10, "LOW": 3}

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _md5(value: str) -> str:
    return hashlib.md5(value.encode("utf-8", errors="ignore")).hexdigest()

def _fmt_salary(val_lakh: Optional[int]) -> str:
    if val_lakh is None:
        return "N/A"
    return f"₹{val_lakh}L" if val_lakh < 100 else f"₹{val_lakh / 100:.1f}L"

def _fmt_exp(years: Optional[int]) -> str:
    if years is None:
        return "N/A"
    if years == 0:
        return "Fresher"
    return f"{years} yr" if years == 1 else f"{years} yrs"

def _fmt_link(url: Optional[str]) -> str:
    if not url:
        return "N/A"
    return url[:60] + "…" if len(url) > 60 else url

# ─────────────────────────────────────────────────────────────
# Core: record_event
# ─────────────────────────────────────────────────────────────

def record_event(
    db: Session,
    opp: Opportunity,
    event_type: str,
    changed_field: Optional[str] = None,
    old_value: Any = None,
    new_value: Any = None,
    change_summary: Optional[str] = None,
    collector_name: Optional[str] = None,
    detected_by: str = "system",
) -> OpportunityHistory:
    """Create a single history event and update the opportunity's change_score."""
    severity = EVENT_SEVERITY.get(event_type, "LOW")

    event = OpportunityHistory(
        opportunity_id=opp.id,
        event_type=event_type,
        changed_field=changed_field,
        old_value=old_value,
        new_value=new_value,
        change_summary=change_summary,
        severity=severity,
        # Snapshot
        confidence_before=opp.confidence_score,
        confidence_after=opp.confidence_score,
        completeness_before=opp.completeness_score,
        completeness_after=opp.completeness_score,
        link_quality_before=opp.link_quality_score,
        link_quality_after=opp.link_quality_score,
        lifecycle_before=opp.lifecycle_status,
        lifecycle_after=opp.lifecycle_status,
        # Attribution
        collector_name=collector_name or opp.collected_by,
        source=opp.primary_source,
        detected_by=detected_by,
        recorded_at=datetime.utcnow(),
    )
    db.add(event)

    # Update change_score (capped at 100)
    delta = SEVERITY_SCORE.get(severity, 3)
    opp.change_score = min(100, (opp.change_score or 0) + delta)

    # Update lifecycle counters
    if event_type in ("VERIFIED", "REVERIFIED"):
        opp.times_verified = (opp.times_verified or 0) + 1
    elif event_type == "REACTIVATED":
        opp.times_reactivated = (opp.times_reactivated or 0) + 1
    elif event_type == "UPDATED":
        opp.times_updated = (opp.times_updated or 0) + 1

    opp.last_seen = datetime.utcnow()
    return event

# ─────────────────────────────────────────────────────────────
# Core: detect_changes
# ─────────────────────────────────────────────────────────────

def detect_changes(
    db: Session,
    opp: Opportunity,
    new_data: Dict[str, Any],
    collector_name: Optional[str] = None,
) -> List[OpportunityHistory]:
    """
    Compare new_data against existing opportunity fields.
    Emit history events for every meaningful change.
    Returns the list of events created.
    """
    events: List[OpportunityHistory] = []

    def _emit(event_type: str, field: str, old: Any, new: Any, summary: str):
        ev = record_event(
            db, opp,
            event_type=event_type,
            changed_field=field,
            old_value=old,
            new_value=new,
            change_summary=summary,
            collector_name=collector_name,
        )
        events.append(ev)

    # ── Salary
    new_sal_min = new_data.get("salary_min")
    new_sal_max = new_data.get("salary_max")
    if new_sal_min is not None and new_sal_min != opp.salary_min:
        _emit("SALARY_CHANGED", "salary_min",
              opp.salary_min, new_sal_min,
              f"{_fmt_salary(opp.salary_min)} → {_fmt_salary(new_sal_min)}")
    if new_sal_max is not None and new_sal_max != opp.salary_max:
        _emit("SALARY_CHANGED", "salary_max",
              opp.salary_max, new_sal_max,
              f"{_fmt_salary(opp.salary_max)} → {_fmt_salary(new_sal_max)}")

    # ── Experience
    new_exp_min = new_data.get("experience_min")
    new_exp_max = new_data.get("experience_max")
    if new_exp_min is not None and new_exp_min != opp.experience_min:
        _emit("EXPERIENCE_CHANGED", "experience_min",
              opp.experience_min, new_exp_min,
              f"{_fmt_exp(opp.experience_min)} → {_fmt_exp(new_exp_min)}")
    if new_exp_max is not None and new_exp_max != opp.experience_max:
        _emit("EXPERIENCE_CHANGED", "experience_max",
              opp.experience_max, new_exp_max,
              f"{_fmt_exp(opp.experience_max)} → {_fmt_exp(new_exp_max)}")

    # ── Location
    new_loc = new_data.get("location")
    if new_loc and new_loc != opp.location:
        _emit("LOCATION_CHANGED", "location",
              opp.location, new_loc,
              f"{opp.location} → {new_loc}")

    # ── Company
    new_company = new_data.get("company")
    if new_company and new_company != opp.company:
        _emit("COMPANY_CHANGED", "company",
              opp.company, new_company,
              f"{opp.company} → {new_company}")

    # ── Description (hash-based)
    new_desc = new_data.get("description", "")
    if new_desc:
        new_hash = _md5(new_desc[:2000])
        if opp.description_hash and new_hash != opp.description_hash:
            _emit("DESCRIPTION_CHANGED", "description",
                  opp.description_hash, new_hash,
                  "Company updated job description")
        opp.description_hash = new_hash

    # ── Skills (hash-based)
    new_skills = new_data.get("required_skills", "")
    if new_skills:
        new_skh = _md5(str(sorted(new_skills.split(","))) if new_skills else "")
        if opp.skills_hash and new_skh != opp.skills_hash:
            _emit("SKILLS_CHANGED", "required_skills",
                  opp.skills_hash, new_skh,
                  "Required skills updated")
        opp.skills_hash = new_skh

    # ── Apply URL
    new_url = new_data.get("apply_url")
    if new_url and new_url != opp.apply_url:
        _emit("LINK_CHANGED", "apply_url",
              opp.apply_url, new_url,
              f"{_fmt_link(opp.apply_url)} → {_fmt_link(new_url)}")

    # ── Link quality transitions
    new_url_status = new_data.get("apply_url_status")
    if new_url_status:
        old_status = opp.apply_url_status
        if old_status != new_url_status:
            if new_url_status == "BROKEN":
                _emit("LINK_BROKEN", "apply_url_status",
                      old_status, new_url_status,
                      "Apply link is now broken")
            elif old_status == "BROKEN" and new_url_status in ("VERIFIED_DIRECT", "VERIFIED_POSTING"):
                _emit("LINK_FIXED", "apply_url_status",
                      old_status, new_url_status,
                      "Apply link has been repaired")

    # ── Lifecycle status
    new_lifecycle = new_data.get("lifecycle_status")
    if new_lifecycle and new_lifecycle != opp.lifecycle_status:
        event_type = "REACTIVATED" if new_lifecycle == "ACTIVE" else \
                     "EXPIRED" if new_lifecycle == "EXPIRED" else "STATUS_CHANGED"
        _emit(event_type, "lifecycle_status",
              opp.lifecycle_status, new_lifecycle,
              f"Status: {opp.lifecycle_status} → {new_lifecycle}")

    # ── Confidence score (±10 threshold to avoid noise)
    new_conf = new_data.get("confidence_score")
    if new_conf is not None and abs(new_conf - (opp.confidence_score or 0)) >= 10:
        _emit("CONFIDENCE_CHANGED", "confidence_score",
              opp.confidence_score, new_conf,
              f"Confidence: {opp.confidence_score} → {new_conf}")

    # ── Completeness score (±10 threshold)
    new_comp = new_data.get("completeness_score")
    if new_comp is not None and abs(new_comp - (opp.completeness_score or 0)) >= 10:
        _emit("COMPLETENESS_CHANGED", "completeness_score",
              opp.completeness_score, new_comp,
              f"Completeness: {opp.completeness_score} → {new_comp}")

    if events:
        record_event(db, opp, "UPDATED", detected_by="system",
                     change_summary=f"{len(events)} field(s) updated")

    return events

# ─────────────────────────────────────────────────────────────
# get_history — for the timeline API
# ─────────────────────────────────────────────────────────────

def get_history(
    db: Session,
    opportunity_id: int,
    limit: int = 50,
    severity_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return the human-readable timeline for a job."""
    q = db.query(OpportunityHistory).filter(
        OpportunityHistory.opportunity_id == opportunity_id
    )
    if severity_filter:
        q = q.filter(OpportunityHistory.severity == severity_filter)

    events = q.order_by(OpportunityHistory.recorded_at.desc()).limit(limit).all()

    return [
        {
            "id": e.id,
            "event": _humanize(e.event_type),
            "event_type": e.event_type,
            "changed_field": e.changed_field,
            "summary": e.change_summary or _humanize(e.event_type),
            "old_value": e.old_value,
            "new_value": e.new_value,
            "severity": e.severity or "LOW",
            "confidence_before": e.confidence_before,
            "confidence_after": e.confidence_after,
            "completeness_before": e.completeness_before,
            "completeness_after": e.completeness_after,
            "detected_by": e.detected_by or "system",
            "collector": e.collector_name,
            "time": e.recorded_at.isoformat() if e.recorded_at else None,
        }
        for e in events
    ]

def _humanize(event_type: str) -> str:
    return {
        "FIRST_SEEN": "Job first discovered",
        "VERIFIED": "Apply link verified",
        "REVERIFIED": "Apply link re-verified",
        "UPDATED": "Job details updated",
        "SALARY_CHANGED": "Salary updated",
        "DESCRIPTION_CHANGED": "Description updated",
        "LOCATION_CHANGED": "Location changed",
        "SKILLS_CHANGED": "Required skills updated",
        "EXPERIENCE_CHANGED": "Experience requirement changed",
        "LINK_CHANGED": "Apply link changed",
        "LINK_FIXED": "Apply link repaired",
        "LINK_BROKEN": "Apply link broken",
        "STATUS_CHANGED": "Job status changed",
        "CONFIDENCE_CHANGED": "Confidence score updated",
        "COMPLETENESS_CHANGED": "Completeness score updated",
        "COMPANY_CHANGED": "Company updated",
        "REACTIVATED": "Job reactivated",
        "EXPIRED": "Job marked as expired",
        "REMOVED": "Job removed",
        "DUPLICATE_MERGED": "Merged duplicate",
        "MANUAL_EDIT": "Manually edited",
    }.get(event_type, event_type.replace("_", " ").title())

# ─────────────────────────────────────────────────────────────
# Dashboard snapshot queries
# ─────────────────────────────────────────────────────────────

def get_history_dashboard_stats(db: Session) -> Dict[str, int]:
    """Returns key metrics for the Platform Intelligence dashboard."""
    from sqlalchemy import func
    from datetime import timedelta

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today_start - timedelta(days=1)

    base = db.query(OpportunityHistory)

    def count_today(event_type: str) -> int:
        return base.filter(
            OpportunityHistory.event_type == event_type,
            OpportunityHistory.recorded_at >= today_start
        ).count()

    updated_today = base.filter(
        OpportunityHistory.event_type == "UPDATED",
        OpportunityHistory.recorded_at >= today_start
    ).count()

    return {
        "jobs_updated_today": updated_today,
        "jobs_expired_today": count_today("EXPIRED"),
        "jobs_reactivated_today": count_today("REACTIVATED"),
        "salary_changes_today": count_today("SALARY_CHANGED"),
        "link_repairs_today": count_today("LINK_FIXED"),
        "link_broken_today": count_today("LINK_BROKEN"),
        "total_history_events": base.count(),
    }
