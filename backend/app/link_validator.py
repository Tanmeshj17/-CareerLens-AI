"""
CareerLens AI — Smart Link & Resource Validator (Phase 11.8)
=============================================================
Audits, validates, and classifies using a safe lifecycle:
  ACTIVE → STALE → CLOSED → ARCHIVED

Rules:
  - Single HTTP 4xx / 5xx / timeout → STALE (retry next cycle)
  - Explicit page text confirming closure → CLOSED immediately
  - Repeated (validation_attempts ≥ 2) confirmed 404/410 → CLOSED
  - VERIFIED_DIRECT jobs are NEVER closed due to bot-protection (403/429)
  - No permanent DELETE operations — all lifecycle changes preserve historical data
"""

import asyncio
import aiohttp
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger("careerlens.link_validator")

# Regex patterns that indicate a job is definitively CLOSED.
# These are only matched against actual page body text.
CLOSED_JOB_PATTERNS = [
    # Requested patterns (Phase 11.8)
    re.compile(r"job (is )?not available", re.IGNORECASE),
    re.compile(r"job is no longer available", re.IGNORECASE),
    re.compile(r"job is no longer open", re.IGNORECASE),
    re.compile(r"this job is no longer available", re.IGNORECASE),
    re.compile(r"position (is )?closed", re.IGNORECASE),
    re.compile(r"this position is no longer accepting applications", re.IGNORECASE),
    re.compile(r"no results found", re.IGNORECASE),
    # Legacy patterns (preserved)
    re.compile(r"applications (are )?closed", re.IGNORECASE),
    re.compile(r"job (has )?expired", re.IGNORECASE),
    re.compile(r"position (is )?no longer available", re.IGNORECASE),
    re.compile(r"no longer accepting applications", re.IGNORECASE),
    re.compile(r"position (has been )?filled", re.IGNORECASE),
    re.compile(r"this job is no longer active", re.IGNORECASE),
    re.compile(r"requisition (is )?closed", re.IGNORECASE),
    re.compile(r"posting (has )?expired", re.IGNORECASE),
    # ATS-specific patterns
    re.compile(r"this req is (no longer )?open", re.IGNORECASE),
    re.compile(r"vacancy (is )?closed", re.IGNORECASE),
    re.compile(r"application deadline (has )?passed", re.IGNORECASE),
]

# Regex patterns that indicate a learning resource / video is BROKEN
INVALID_RESOURCE_PATTERNS = [
    re.compile(r"this video isn['’]t available (anymore)?", re.IGNORECASE),
    re.compile(r"video unavailable", re.IGNORECASE),
    re.compile(r"this video has been removed", re.IGNORECASE),
    re.compile(r"private video", re.IGNORECASE),
    re.compile(r"page not found", re.IGNORECASE),
    re.compile(r"we were not able to find the page", re.IGNORECASE),
    re.compile(r"404 - page not found", re.IGNORECASE),
    re.compile(r"course not found", re.IGNORECASE),
]


class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        classification: str,
        final_url: str,
        is_closed: bool = False,
        error: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.classification = classification  # ACTIVE | STALE | CLOSED | EXPIRED | INVALID_LINK | INVALID_RESOURCE
        self.final_url = final_url
        self.is_closed = is_closed
        self.error = error


async def _fetch_url(session: aiohttp.ClientSession, url: str, is_resource: bool = False) -> ValidationResult:
    """Fetch URL and classify its status based on HTTP code and body text."""
    if not url or not url.startswith(("http://", "https://")):
        cls = "INVALID_RESOURCE" if is_resource else "INVALID_LINK"
        return ValidationResult(False, cls, url or "", error="Malformed URL")

    # Quick check for legacy fake req_id URLs
    if "?req_id=" in url:
        clean_url = url.split("?req_id=")[0]
    else:
        clean_url = url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        async with session.get(clean_url, allow_redirects=True, timeout=12, headers=headers) as resp:
            final_url = str(resp.url)
            status_code = resp.status

            # Bot-protection / rate-limit responses: STALE, never CLOSED
            if status_code in (403, 429):
                cls = "VERIFIED" if is_resource else "STALE"
                return ValidationResult(True, cls, final_url, error=f"HTTP {status_code} (bot protection — STALE)")

            # Server errors: STALE (transient)
            if status_code >= 500:
                cls = "INVALID_RESOURCE" if is_resource else "STALE"
                return ValidationResult(False, cls, final_url, error=f"HTTP {status_code} (server error — STALE)")

            # 404/410: classify as STALE here — run_full_audit promotes to CLOSED
            # only after repeated failures (validation_attempts tracks this)
            if status_code in (404, 410):
                cls = "INVALID_RESOURCE" if is_resource else "STALE"
                return ValidationResult(False, cls, final_url, error=f"HTTP {status_code}")

            # HTTP 200 — scan body text for explicit closure messages
            try:
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" in content_type or "text/plain" in content_type:
                    body_text = await resp.text()

                    if is_resource:
                        for pat in INVALID_RESOURCE_PATTERNS:
                            if pat.search(body_text):
                                return ValidationResult(False, "INVALID_RESOURCE", final_url, error="Broken resource text detected")
                    else:
                        for pat in CLOSED_JOB_PATTERNS:
                            if pat.search(body_text):
                                # Explicit text match → CLOSED immediately (no retry needed)
                                return ValidationResult(False, "CLOSED", final_url, is_closed=True, error="Closed job text detected")
            except Exception:
                pass  # If reading body fails, rely on status code

            cls = "VERIFIED" if is_resource else "ACTIVE"
            return ValidationResult(True, cls, final_url)

    except asyncio.TimeoutError:
        # Timeout: treat as STALE (transient network issue)
        cls = "INVALID_RESOURCE" if is_resource else "STALE"
        return ValidationResult(False, cls, clean_url, error="Connection Timeout — STALE")
    except Exception as e:
        cls = "INVALID_RESOURCE" if is_resource else "STALE"
        return ValidationResult(False, cls, clean_url, error=str(e))


# Trusted domains — known corporate career portals and learning platforms that may block bots
TRUSTED_DOMAINS = [
    # Major tech companies
    "google.com", "microsoft.com", "amazon.jobs", "apple.com", "meta.com", "metacareers.com",
    "oracle.com", "sap.com", "ibm.com", "salesforce.com", "adobe.com", "qualcomm.com",
    "nvidia.com", "atlassian.com", "uber.com", "stripe.com", "linkedin.com", "intuit.com",
    "servicenow.com", "vmware.com", "cisco.com", "paypal.com", "bytedance.com",
    # Indian IT/Services
    "tcs.com", "ibegin.tcs.com", "infosys.com", "wipro.com", "hcltech.com",
    "techmahindra.com", "cognizant.com", "capgemini.com", "accenture.com",
    "ltimindtree.com", "mphasis.com",
    # Indian Startups/Unicorns
    "flipkartcareers.com", "swiggy.com", "zomato.com", "razorpay.com", "phonepe.com",
    "cred.club", "zerodha.com", "meesho.io", "groww.in", "freshworks.com", "zoho.com",
    "postman.com", "browserstack.com", "inmobi.com", "darwinbox.com", "chargebee.com",
    "druva.com", "urbancompany.com", "makemytrip.com",
    # Lever/Greenhouse ATS (used by startups)
    "lever.co", "jobs.lever.co", "greenhouse.io", "boards.greenhouse.io",
    # Consulting/Big4
    "deloitte.com", "pwc.in", "ey.com", "kpmg.com",
    # Telecom
    "jio.com", "airtel.in",
    # Finance
    "goldmansachs.com", "jpmc.fa.oraclecloud.com", "morganstanley.tal.net", "db.com",
    # Other MNCs
    "walmart.com", "target.com", "grab.careers",
    # Learning platforms
    "youtube.com", "youtu.be", "github.com", "freecodecamp.org", "nptel.ac.in",
    "swayam.gov.in", "hackerrank.com", "tcsionhub.in", "skillbuilder.aws",
    "learn.microsoft.com", "coursera.org", "udemy.com",
    # Workday / ATS
    "myworkdayjobs.com", "eightfold.ai", "oraclecloud.com", "tal.net",
]


def _is_trusted_domain(domain: str) -> bool:
    """Check if a domain belongs to a known trusted career portal or learning platform."""
    return any(td in domain for td in TRUSTED_DOMAINS)


async def validate_urls_async(urls: List[str], is_resource: bool = False, concurrency: int = 15) -> List[ValidationResult]:
    """Validate a batch of URLs asynchronously."""
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [_fetch_url(session, url, is_resource=is_resource) for url in urls]
        return await asyncio.gather(*tasks)


# Number of failed validation_attempts before STALE→CLOSED promotion
CLOSED_AFTER_FAILURES = 2


def run_full_audit_and_cleanup(db) -> Dict[str, Any]:
    """
    Smart audit and lifecycle cleanup (Phase 11.8):
    - ACTIVE → STALE on first HTTP failure (any error)
    - STALE → CLOSED only after CLOSED_AFTER_FAILURES repeated failures
    - CLOSED immediately on explicit page-text match
    - VERIFIED_DIRECT jobs cannot be CLOSED due to bot-protection (403/429)
    - No permanent DELETE — all changes preserve history
    - Validates only the oldest last_validated_at batch (rate-limited)
    """
    try:
        from app import models
    except ImportError:
        from backend.app import models

    now = datetime.utcnow()
    expired_cutoff = now - timedelta(days=45)
    stale_cutoff = now - timedelta(days=30)

    stats = {
        "audited_at": now.isoformat(),
        "total_jobs_audited": 0,
        "jobs_closed": 0,
        "jobs_expired": 0,
        "jobs_stale": 0,
        "jobs_active": 0,
        "legacy_urls_sanitized": 0,
        "total_resources_audited": 0,
        "resources_invalid": 0,
        "resources_verified": 0,
        "noisy_sources": {}
    }

    # Step 1: Sanitize legacy ?req_id= URLs across DB
    bad_urls = db.query(models.Opportunity).filter(models.Opportunity.apply_url.like("%?req_id=%")).all()
    if bad_urls:
        stats["legacy_urls_sanitized"] = len(bad_urls)
        for row in bad_urls:
            row.apply_url = row.apply_url.split("?req_id=")[0]
        db.commit()

    # Step 2: Classify Expired jobs (>45 days old) → ARCHIVED (inactive)
    expired_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.posted_date < expired_cutoff,
        models.Opportunity.is_active == True
    ).all()
    for j in expired_jobs:
        j.lifecycle_status = "EXPIRED"
        j.is_active = False
        j.status = "Expired"
        j.validation_status = "EXPIRED"
        j.validation_reason = "Exceeded 45-day age limit"
        stats["jobs_expired"] += 1
    db.commit()

    # Step 3: Classify Stale jobs (30-45 days old) → STALE (still active)
    stale_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.posted_date >= expired_cutoff,
        models.Opportunity.posted_date < stale_cutoff,
        models.Opportunity.lifecycle_status.in_(["ACTIVE", "NEW", None])
    ).all()
    for j in stale_jobs:
        j.lifecycle_status = "STALE"
        j.validation_status = "STALE"
        j.validation_reason = "Job is 30-45 days old"
        stats["jobs_stale"] += 1
    db.commit()

    # Step 4: Batched smart URL validation (oldest last_validated_at first)
    # Pick up to 200 active jobs that haven't been checked recently
    active_jobs = (
        db.query(models.Opportunity)
        .filter(
            models.Opportunity.is_active == True,
            models.Opportunity.lifecycle_status.in_(["ACTIVE", "NEW", "STALE", None])
        )
        .order_by(
            models.Opportunity.last_validated_at.asc().nullsfirst()
        )
        .limit(200)
        .all()
    )

    stats["total_jobs_audited"] = len(active_jobs)

    if active_jobs:
        urls = [j.apply_url for j in active_jobs]
        results = asyncio.run(validate_urls_async(urls, is_resource=False))

        for job, res in zip(active_jobs, results):
            job.last_url_verified_at = now
            job.last_validated_at = now
            job.validation_attempts = (job.validation_attempts or 0) + 1

            if not res.is_valid:
                src = job.primary_source or "Unknown"
                stats["noisy_sources"][src] = stats["noisy_sources"].get(src, 0) + 1

                if res.classification == "CLOSED" or res.is_closed:
                    # Explicit page-text match → CLOSED immediately (no retry needed)
                    job.lifecycle_status = "CLOSED"
                    job.apply_url_status = "CLOSED"
                    job.is_active = False
                    job.status = "Closed"
                    job.validation_status = "CLOSED"
                    job.validation_reason = res.error or "Page text confirms closure"
                    stats["jobs_closed"] += 1

                elif res.classification == "STALE":
                    # Temporary failure (403, 429, 500, timeout, single 404/410)
                    is_verified_direct = job.apply_url_status == "VERIFIED_DIRECT"

                    if is_verified_direct:
                        # VERIFIED_DIRECT: NEVER close due to single failure / bot protection
                        job.lifecycle_status = "ACTIVE"
                        job.validation_status = "STALE"
                        job.validation_reason = f"Transient error (VERIFIED_DIRECT protected): {res.error}"
                        stats["jobs_active"] += 1
                    elif job.validation_attempts >= CLOSED_AFTER_FAILURES:
                        # Repeated failure → promote to CLOSED
                        job.lifecycle_status = "CLOSED"
                        job.apply_url_status = "CLOSED"
                        job.is_active = False
                        job.status = "Closed"
                        job.validation_status = "CLOSED"
                        job.validation_reason = f"Repeated validation failure ({job.validation_attempts}x): {res.error}"
                        stats["jobs_closed"] += 1
                    else:
                        # First failure → STALE (will retry next cycle)
                        job.lifecycle_status = "STALE"
                        job.validation_status = "STALE"
                        job.validation_reason = f"Transient failure (attempt {job.validation_attempts}): {res.error}"
                        stats["jobs_stale"] += 1

            else:
                # Successful validation → reset to ACTIVE
                job.lifecycle_status = "ACTIVE"
                job.apply_url_status = "VALID"
                job.verified_apply_url = res.final_url
                job.is_active = True
                job.status = "Active"
                job.validation_status = "VALID"
                job.validation_reason = None
                job.validation_attempts = 0  # Reset retry counter on success
                stats["jobs_active"] += 1

        db.commit()

    # Step 5: Audit Learning Resources
    resources = db.query(models.LearningResource).all()
    stats["total_resources_audited"] = len(resources)

    if resources:
        res_urls = [r.url for r in resources]
        res_results = asyncio.run(validate_urls_async(res_urls, is_resource=True))

        for res, val in zip(resources, res_results):
            if not val.is_valid or val.classification == "INVALID_RESOURCE":
                res.status = "INVALID_RESOURCE"
                res.availability_status = "INVALID"
                stats["resources_invalid"] += 1
            else:
                res.status = "VERIFIED"
                res.availability_status = "VERIFIED"
                stats["resources_verified"] += 1

        db.commit()

    return stats
