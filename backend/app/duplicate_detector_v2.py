"""
Phase 11.4 T4: Fuzzy Duplicate Detection v2
Detects near-duplicates that the v1 hash-based system misses.

Strategy — 4 progressive passes:
  Pass 1: Exact hash (fast, inherited from v1)
  Pass 2: Exact (title+company) — catches the same posting from 2 sources
  Pass 3: Normalized title + company — catches role-level variants
           e.g. "Software Engineer I" == "Graduate Software Engineer" (same company)
  Pass 4: Same company + URL domain — catches multiple ATS path variants

Duplicate Score (0–100):
  Title exact match            → +40
  Title normalized match       → +30
  Same company (canonical)     → +20
  Same URL domain              → +15
  Same location                → +10
  Description similarity ≥70%  → +15
  Score ≥ 70 → auto-merge
  Score 50–69 → flag (logged but not merged)

Uses difflib.SequenceMatcher only — no external C deps required.
"""
import re
import logging
from datetime import datetime
from difflib import SequenceMatcher
from urllib.parse import urlparse
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import Opportunity, JobQualityMetrics

logger = logging.getLogger("duplicate_detector_v2")

# ─── Role-level title normalization ───────────────────────────
# Strip ordinal suffixes and experience qualifiers to get the core role
_TITLE_STRIP = re.compile(
    r'\b(i|ii|iii|iv|v|1|2|3|senior|sr\.?|junior|jr\.?|lead|principal|staff|'
    r'associate|fresher|graduate|entry.?level|intern|trainee|apprentice|'
    r'new grad|ng|ng\.?|experienced?|mid.?level)\b',
    re.IGNORECASE
)
_WHITESPACE = re.compile(r'\s+')


def _normalize_title(title: str) -> str:
    """Strip experience qualifiers and normalize whitespace for comparison."""
    if not title:
        return ""
    t = title.lower().strip()
    t = _TITLE_STRIP.sub(" ", t)
    t = _WHITESPACE.sub(" ", t).strip()
    return t


def _similarity(a: str, b: str) -> float:
    """Return similarity ratio 0.0–1.0 between two strings using SequenceMatcher."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _url_domain(url: Optional[str]) -> Optional[str]:
    """Extract the base domain from a URL, stripped of www prefix."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return re.sub(r'^www\.', '', domain)
    except Exception:
        return None


def _quality_of(opp: Opportunity) -> int:
    """Quality heuristic — used to select canonical record during merge."""
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
    # Prefer newer records as canonical
    if opp.posted_date:
        from datetime import timedelta
        days_old = (datetime.utcnow() - opp.posted_date).days
        score += max(0, 30 - days_old)  # up to +30 for recency
    return score


def _duplicate_score(a: Opportunity, b: Opportunity) -> int:
    """
    Compute a duplicate confidence score (0–100) between two opportunities.
    """
    score = 0

    # Title exact match
    if a.title and b.title and a.title.lower().strip() == b.title.lower().strip():
        score += 40
    else:
        # Normalized title similarity
        nt_a = _normalize_title(a.title or "")
        nt_b = _normalize_title(b.title or "")
        if nt_a and nt_b:
            sim = _similarity(nt_a, nt_b)
            if sim >= 0.90:
                score += 30
            elif sim >= 0.75:
                score += 15

    # Same company (canonical)
    if a.company and b.company:
        if a.company.lower().strip() == b.company.lower().strip():
            score += 20
        else:
            comp_sim = _similarity(a.company or "", b.company or "")
            if comp_sim >= 0.85:
                score += 10

    # Same URL domain
    da, db_ = _url_domain(a.apply_url), _url_domain(b.apply_url)
    if da and db_ and da == db_:
        score += 15

    # Same location
    if a.location and b.location:
        if a.location.lower().strip() == b.location.lower().strip():
            score += 10

    # Description similarity (expensive — only if score already promising)
    if score >= 40 and a.description and b.description:
        desc_sim = _similarity(a.description[:500], b.description[:500])
        if desc_sim >= 0.70:
            score += 15

    return min(score, 100)


from sqlalchemy import text


def _merge_into_canonical(db: Session, canonical: Opportunity, dupes: list) -> None:
    """Merge metadata from dupes into the canonical record, then delete dupes."""
    for dupe in dupes:
        if not canonical.salary_range and dupe.salary_range:
            canonical.salary_range = dupe.salary_range
        if not canonical.required_skills and dupe.required_skills:
            canonical.required_skills = dupe.required_skills
        if not canonical.description and dupe.description:
            canonical.description = dupe.description
        if not canonical.apply_url and dupe.apply_url:
            canonical.apply_url = dupe.apply_url

        # Clean up foreign key references using savepoints
        for sql_stmt in [
            "DELETE FROM job_match_scores WHERE opportunity_id = :id",
            "DELETE FROM job_quality_metrics WHERE opportunity_id = :id",
            "DELETE FROM user_application_history WHERE opportunity_id = :id",
            "DELETE FROM opportunity_histories WHERE opportunity_id = :id",
        ]:
            try:
                with db.begin_nested():
                    db.execute(text(sql_stmt), {"id": dupe.id})
            except Exception as ex:
                logger.debug(f"FK cleanup statement ignored: {ex}")

        db.delete(dupe)

    canonical.times_updated = (canonical.times_updated or 0) + 1
    canonical.last_seen = datetime.utcnow()
    canonical.duplicates_removed = (getattr(canonical, 'duplicates_removed', 0) or 0) + len(dupes)


def run_fuzzy_duplicate_detection(db: Session, max_candidates: int = 50) -> Dict[str, Any]:
    """
    Full 4-pass fuzzy duplicate detection.
    Returns stats dict.
    """
    merged_count = 0
    flagged_count = 0
    groups_processed = 0
    processed_ids: set = set()

    # ─── Pass 1: Exact hash (fast) ────────────────────────────
    hash_groups = (
        db.query(Opportunity.opportunity_hash, func.count(Opportunity.id))
        .filter(Opportunity.opportunity_hash != None)
        .group_by(Opportunity.opportunity_hash)
        .having(func.count(Opportunity.id) > 1)
        .limit(max_candidates)
        .all()
    )
    for opp_hash, _ in hash_groups:
        dupes = (
            db.query(Opportunity)
            .filter(Opportunity.opportunity_hash == opp_hash)
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
    logger.info(f"Pass 1 (exact hash): {merged_count} merged")

    # ─── Pass 2: Exact title + company ───────────────────────
    exact_groups = (
        db.query(
            func.lower(Opportunity.title),
            func.lower(Opportunity.company),
            func.count(Opportunity.id)
        )
        .filter(
            Opportunity.title != None,
            Opportunity.company != None,
            Opportunity.status != "ARCHIVED",
        )
        .group_by(func.lower(Opportunity.title), func.lower(Opportunity.company))
        .having(func.count(Opportunity.id) > 1)
        .limit(max_candidates)
        .all()
    )
    for title_lower, company_lower, _ in exact_groups:
        dupes = (
            db.query(Opportunity)
            .filter(
                func.lower(Opportunity.title) == title_lower,
                func.lower(Opportunity.company) == company_lower,
            )
            .all()
        )
        dupes = [d for d in dupes if d.id not in processed_ids]
        if len(dupes) < 2:
            continue
        canonical = max(dupes, key=_quality_of)
        others = [d for d in dupes if d.id != canonical.id]
        _merge_into_canonical(db, canonical, others)
        merged_count += len(others)
        pass2_merged += len(others)
        groups_processed += 1
        processed_ids.update(d.id for d in others)
    db.commit()
    logger.info(f"Pass 2 (exact title+company): {pass2_merged} merged")

    # ─── Pass 3: Normalized title fuzzy match per company ────
    # Group active opps by company where company has >1 active job
    company_counts = (
        db.query(Opportunity.company)
        .filter(
            Opportunity.company != None,
            Opportunity.status == "ACTIVE",
        )
        .group_by(Opportunity.company)
        .having(func.count(Opportunity.id) > 1)
        .limit(10)
        .all()
    )
    companies = company_counts

    pass3_merged = 0
    pass3_flagged = 0
    for (company,) in companies:
        opps = (
            db.query(Opportunity)
            .filter(
                Opportunity.company == company,
                Opportunity.status == "ACTIVE",
                ~Opportunity.id.in_(processed_ids),
            )
            .all()
        )
        if len(opps) < 2:
            continue

        # O(n²) within each company group — safe since groups are small
        paired: set = set()
        for i, a in enumerate(opps):
            for j, b in enumerate(opps):
                if i >= j:
                    continue
                pair_key = (min(a.id, b.id), max(a.id, b.id))
                if pair_key in paired:
                    continue
                paired.add(pair_key)

                dup_score = _duplicate_score(a, b)
                if dup_score >= 70:
                    # Auto-merge: keep higher quality
                    canonical = a if _quality_of(a) >= _quality_of(b) else b
                    dupe = b if canonical.id == a.id else a
                    if dupe.id not in processed_ids:
                        _merge_into_canonical(db, canonical, [dupe])
                        merged_count += 1
                        pass3_merged += 1
                        groups_processed += 1
                        processed_ids.add(dupe.id)
                elif dup_score >= 50:
                    # Flag but don't merge
                    logger.warning(
                        f"Possible duplicate (score={dup_score}): "
                        f"[{a.id}] '{a.title}' vs [{b.id}] '{b.title}' @ {company}"
                    )
                    flagged_count += 1
                    pass3_flagged += 1

    db.commit()
    logger.info(f"Pass 3 (fuzzy title/company): {pass3_merged} merged, {pass3_flagged} flagged")

    # ─── Pass 4: Same company + URL domain ───────────────────
    pass4_merged = 0
    all_opps_with_url = (
        db.query(Opportunity)
        .filter(
            Opportunity.apply_url != None,
            Opportunity.company != None,
            Opportunity.status == "ACTIVE",
            ~Opportunity.id.in_(processed_ids),
        )
        .limit(max_candidates)
        .all()
    )

    # Group by (company, url_domain)
    from collections import defaultdict
    domain_groups: dict = defaultdict(list)
    for opp in all_opps_with_url:
        domain = _url_domain(opp.apply_url)
        if domain and opp.company:
            key = (opp.company.lower().strip(), domain)
            domain_groups[key].append(opp)

    for (comp_key, domain), group in domain_groups.items():
        if len(group) < 2:
            continue
        # Within same company+domain, check for title similarity
        paired = set()
        for i, a in enumerate(group):
            for j, b in enumerate(group):
                if i >= j:
                    continue
                pair_key = (min(a.id, b.id), max(a.id, b.id))
                if pair_key in paired or a.id in processed_ids or b.id in processed_ids:
                    continue
                paired.add(pair_key)
                title_sim = _similarity(
                    _normalize_title(a.title or ""),
                    _normalize_title(b.title or "")
                )
                if title_sim >= 0.85:
                    canonical = a if _quality_of(a) >= _quality_of(b) else b
                    dupe = b if canonical.id == a.id else a
                    _merge_into_canonical(db, canonical, [dupe])
                    merged_count += 1
                    pass4_merged += 1
                    groups_processed += 1
                    processed_ids.add(dupe.id)

    db.commit()
    logger.info(f"Pass 4 (URL domain+title): {pass4_merged} merged")

    total = merged_count
    logger.info(
        f"Fuzzy Duplicate Detection v2 complete: "
        f"{total} total merged, {flagged_count} flagged, "
        f"{groups_processed} groups processed"
    )

    return {
        "total_merged": total,
        "total_flagged": flagged_count,
        "groups_processed": groups_processed,
        "passes_run": 4,
        "pass_1_hash_merged": merged_count - (pass2_merged if 'pass2_merged' in dir() else 0),
        "pass_2_exact_merged": pass2_merged if 'pass2_merged' in dir() else 0,
        "pass_3_fuzzy_merged": pass3_merged,
        "pass_3_flagged": pass3_flagged,
        "pass_4_domain_merged": pass4_merged,
    }
