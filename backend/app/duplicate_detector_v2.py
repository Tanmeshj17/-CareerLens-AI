"""
Phase 11.8: Strict Deduplication
Enforces a strong fingerprint to safely deduplicate jobs without hard-deleting.
Fingerprint: normalized_company + normalized_title + normalized_location + url_path_id
"""
import re
import logging
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.models import Opportunity

logger = logging.getLogger("duplicate_detector_v2")

def _normalize(text: str) -> str:
    if not text: return ""
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    t = re.sub(r'\b(i|ii|iii|1|2|3|senior|sr|junior|jr|lead|principal|staff|associate|fresher|graduate|intern|trainee)\b', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def _extract_identifier(url: Optional[str], source_id: Optional[str]) -> Optional[str]:
    if source_id: return str(source_id)
    if not url: return None
    try:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if 'req_id=' in url:
            return url.split('req_id=')[1].split('&')[0]
        if path:
            return path
        return parsed.netloc
    except:
        return None

def _quality_of(opp: Opportunity) -> int:
    """Quality heuristic to select canonical record."""
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
    if opp.posted_date:
        days_old = (datetime.utcnow() - opp.posted_date).days
        score += max(0, 30 - days_old)
    return score

def run_strict_deduplication(db: Session) -> Dict[str, Any]:
    """
    Strict fingerprint deduplication.
    Archives duplicates by setting them to CLOSED/Inactive instead of hard deleting.
    """
    logger.info("Running strict deduplication...")
    active_jobs = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    
    fingerprints = defaultdict(list)
    for job in active_jobs:
        norm_company = _normalize(job.company)
        norm_title = _normalize(job.title)
        norm_loc = _normalize(job.location)
        identifier = _extract_identifier(job.apply_url, job.source_job_id)
        
        fingerprint = f"{norm_company}|{norm_title}|{norm_loc}|{identifier}"
        fingerprints[fingerprint].append(job)
        
    archived_count = 0
    verified_direct_archived = 0

    for fp, jobs in fingerprints.items():
        if len(jobs) > 1:
            # Sort by ID descending (newer) as baseline, but use quality heuristic
            jobs = sorted(jobs, key=lambda x: (_quality_of(x), x.id), reverse=True)
            keeper = jobs[0]
            dupes = jobs[1:]
            
            for dupe in dupes:
                # Migrate useful data to canonical if missing
                if not keeper.salary_range and dupe.salary_range:
                    keeper.salary_range = dupe.salary_range
                if not keeper.required_skills and dupe.required_skills:
                    keeper.required_skills = dupe.required_skills
                
                # Archive the duplicate safely (DO NOT DELETE)
                dupe.is_active = False
                dupe.status = "Closed"
                dupe.lifecycle_status = "ARCHIVED"
                dupe.validation_status = "ARCHIVED_DUPLICATE"
                dupe.validation_reason = f"Merged into ID {keeper.id}"
                
                if dupe.apply_url_status == "VERIFIED_DIRECT":
                    verified_direct_archived += 1
                
                archived_count += 1
                
            keeper.times_updated = (getattr(keeper, 'times_updated', 0) or 0) + 1
            keeper.duplicates_removed = (getattr(keeper, 'duplicates_removed', 0) or 0) + len(dupes)
            
    db.commit()
    
    logger.info(f"Strict Deduplication Complete. Archived: {archived_count}")
    return {
        "total_active_checked": len(active_jobs),
        "total_archived": archived_count,
        "verified_direct_archived": verified_direct_archived
    }

def run_fuzzy_duplicate_detection(db: Session, max_candidates: int = 50) -> Dict[str, Any]:
    # Deprecated: replaced by strict deduplication for safety.
    return run_strict_deduplication(db)
