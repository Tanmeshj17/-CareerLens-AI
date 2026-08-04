"""
Phase 9.0 Wave 2: Duplicate Opportunity Detector
Detects near-duplicates using multiple signals:
  - Same opportunity_hash (exact duplicate)
  - Same (title, company) + same description_hash
  - Same (title, company) + same source_job_id (ATS ID)
  - Same (title, company) + same apply_url
Auto-merges duplicates, keeping the highest-quality record.
"""
import hashlib
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import Opportunity, JobQualityMetrics
from typing import Dict, Any

logger = logging.getLogger("duplicate_detector")


def _quality_of(opp: Opportunity) -> int:
    """Quick quality heuristic for choosing the canonical record."""
    score = 0
    score += opp.confidence_score or 0
    score += opp.completeness_score or 0
    score += opp.link_quality_score or 0
    if opp.apply_url_status in ("VERIFIED_DIRECT", "VERIFIED_POSTING"):
        score += 50
    if opp.description:
        score += 10
    if opp.salary_range:
        score += 10
    if opp.required_skills:
        score += 10
    return score


def _merge_into_canonical(db: Session, canonical: Opportunity, dupes: list) -> None:
    """Merge metadata from dupes into the canonical record, then delete dupes."""
    for dupe in dupes:
        # Prefer filled fields from dupes if canonical is missing them
        if not canonical.salary_range and dupe.salary_range:
            canonical.salary_range = dupe.salary_range
        if not canonical.required_skills and dupe.required_skills:
            canonical.required_skills = dupe.required_skills
        if not canonical.description and dupe.description:
            canonical.description = dupe.description

        # Mark the quality record as duplicate before deleting
        qm = db.query(JobQualityMetrics).filter(
            JobQualityMetrics.opportunity_id == dupe.id
        ).first()
        if qm:
            db.delete(qm)

        db.delete(dupe)

    canonical.times_updated = (canonical.times_updated or 0) + 1
    canonical.last_seen = datetime.utcnow()


def run_duplicate_detection(db: Session) -> Dict[str, Any]:
    """Run full duplicate detection and merge pass."""
    merged_count = 0
    groups_processed = 0
    processed_ids = set()

    # --- Pass 1: Exact hash duplicates ---
    hash_dupes = (
        db.query(Opportunity.opportunity_hash, func.count(Opportunity.id))
        .filter(Opportunity.opportunity_hash != None)
        .group_by(Opportunity.opportunity_hash)
        .having(func.count(Opportunity.id) > 1)
        .all()
    )

    for opp_hash, count in hash_dupes:
        dupes = (
            db.query(Opportunity)
            .filter(Opportunity.opportunity_hash == opp_hash)
            .order_by(Opportunity.id.asc())
            .all()
        )
        canonical = max(dupes, key=_quality_of)
        others = [d for d in dupes if d.id != canonical.id and d.id not in processed_ids]
        if others:
            _merge_into_canonical(db, canonical, others)
            merged_count += len(others)
            groups_processed += 1
            processed_ids.update(d.id for d in others)

    db.commit()

    # --- Pass 2: Near-duplicates (same title + company + description_hash) ---
    desc_hash_dupes = (
        db.query(Opportunity.title, Opportunity.company, Opportunity.description_hash)
        .filter(
            Opportunity.description_hash != None,
            Opportunity.title != None,
            Opportunity.company != None,
        )
        .group_by(Opportunity.title, Opportunity.company, Opportunity.description_hash)
        .having(func.count(Opportunity.id) > 1)
        .all()
    )

    for title, company, desc_hash in desc_hash_dupes:
        dupes = (
            db.query(Opportunity)
            .filter(
                Opportunity.title == title,
                Opportunity.company == company,
                Opportunity.description_hash == desc_hash,
                ~Opportunity.id.in_(processed_ids),
            )
            .all()
        )
        if len(dupes) < 2:
            continue
        canonical = max(dupes, key=_quality_of)
        others = [d for d in dupes if d.id != canonical.id]
        _merge_into_canonical(db, canonical, others)
        merged_count += len(others)
        groups_processed += 1
        processed_ids.update(d.id for d in others)

    db.commit()

    # --- Pass 3: ATS ID duplicates (same company + source_job_id) ---
    ats_id_dupes = (
        db.query(Opportunity.company, Opportunity.source_job_id)
        .filter(Opportunity.source_job_id != None, Opportunity.company != None)
        .group_by(Opportunity.company, Opportunity.source_job_id)
        .having(func.count(Opportunity.id) > 1)
        .all()
    )

    for company, ats_id in ats_id_dupes:
        dupes = (
            db.query(Opportunity)
            .filter(
                Opportunity.company == company,
                Opportunity.source_job_id == ats_id,
                ~Opportunity.id.in_(processed_ids),
            )
            .all()
        )
        if len(dupes) < 2:
            continue
        canonical = max(dupes, key=_quality_of)
        others = [d for d in dupes if d.id != canonical.id]
        _merge_into_canonical(db, canonical, others)
        merged_count += len(others)
        groups_processed += 1
        processed_ids.update(d.id for d in others)

    db.commit()

    logger.info(f"Duplicate Detection: {merged_count} dupes merged across {groups_processed} groups.")
    return {
        "duplicate_groups_found": groups_processed,
        "opportunities_merged": merged_count,
        "passes_run": 3,
    }
