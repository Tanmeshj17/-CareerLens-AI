"""
CareerLens AI — Comprehensive Link & Resource Validator
========================================================
Audits, validates, and classifies:
  1. Opportunities: ACTIVE | STALE | CLOSED | EXPIRED | INVALID_LINK
  2. Learning Resources: VERIFIED | INVALID_RESOURCE

Detects HTTP status codes (404, 410, 403, 429) & in-page dead strings:
  - "video isn't available" / "video unavailable" / "this video has been removed" / "private video"
  - "page not found" / "we were not able to find the page"
  - "no longer accepting applications" / "job expired" / "applications closed" / "position no longer available"
"""

import asyncio
import aiohttp
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger("careerlens.link_validator")

# Trusted corporate/platform domains that block automated scrapers
# If these timeout or return 403/429, treat as VALID (bot protection)
TRUSTED_DOMAINS = [
    # Job Board Platforms (Lever, Greenhouse, Workday, Oracle, etc.)
    "lever.co", "greenhouse.io", "workday.com", "myworkdayjobs.com",
    "eightfold.ai", "oraclecloud.com", "tal.net", "smartrecruiters.com",
    # Indian IT Services
    "tcs.com", "ibegin.tcs.com", "tcsionhub.in", "infosys.com",
    "wipro.com", "hcltech.com", "techmahindra.com", "cognizant.com",
    "capgemini.com", "accenture.com", "ltimindtree.com", "mphasis.com",
    # MNCs
    "google.com", "microsoft.com", "amazon.jobs", "apple.com",
    "metacareers.com", "meta.com", "oracle.com", "sap.com",
    "ibm.com", "salesforce.com", "adobe.com", "qualcomm.com",
    "nvidia.com", "atlassian.com", "uber.com", "stripe.com",
    "linkedin.com", "intuit.com", "servicenow.com", "vmware.com",
    "cisco.com", "paypal.com", "bytedance.com",
    # Indian Startups/Unicorns
    "flipkartcareers.com", "swiggy.com", "zomato.com", "razorpay.com",
    "phonepe.com", "cred.club", "zerodha.com", "paytm.com",
    "meesho.io", "groww.in", "freshworks.com", "zoho.com",
    "postman.com", "browserstack.com", "inmobi.com", "darwinbox.com",
    "chargebee.com", "druva.com", "lenskart.com", "urbancompany.com",
    # Consulting/Banking
    "deloitte.com", "pwc.in", "ey.com", "kpmg.com",
    "goldmansachs.com", "jpmorgan.com", "morganstanley.com",
    "db.com", "walmart.com", "target.com", "grab.careers",
    # Telecom / Others
    "jio.com", "airtel.in", "makemytrip.com",
    # Learning Platforms
    "youtube.com", "youtu.be", "github.com", "freecodecamp.org",
    "nptel.ac.in", "swayam.gov.in", "hackerrank.com",
    "coursera.org", "skillbuilder.aws", "learn.microsoft.com",
    "learndigital.withgoogle.com",
]

# Regex patterns that indicate a job is CLOSED or EXPIRED
CLOSED_JOB_PATTERNS = [
    re.compile(r"applications (are )?closed", re.IGNORECASE),
    re.compile(r"job (has )?expired", re.IGNORECASE),
    re.compile(r"position (is )?no longer available", re.IGNORECASE),
    re.compile(r"no longer accepting applications", re.IGNORECASE),
    re.compile(r"position (has been )?filled", re.IGNORECASE),
    re.compile(r"this job is no longer active", re.IGNORECASE),
    re.compile(r"requisition (is )?closed", re.IGNORECASE),
    re.compile(r"posting (has )?expired", re.IGNORECASE),
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

            if status_code in (403, 429):
                # Bot protection / Cloudflare challenge: URL exists, treat as valid active URL
                cls = "VERIFIED" if is_resource else "ACTIVE"
                return ValidationResult(True, cls, final_url)

            if status_code in (404, 410):
                cls = "INVALID_RESOURCE" if is_resource else "INVALID_LINK"
                return ValidationResult(False, cls, final_url, error=f"HTTP {status_code}")

            if status_code >= 500:
                cls = "INVALID_RESOURCE" if is_resource else "INVALID_LINK"
                return ValidationResult(False, cls, final_url, error=f"HTTP {status_code}")

            # If HTTP 200/302, check body text for dead resource / closed job keywords
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
                                return ValidationResult(False, "CLOSED", final_url, is_closed=True, error="Closed job text detected")
            except Exception:
                pass  # If reading body fails, rely on status code

            cls = "VERIFIED" if is_resource else "ACTIVE"
            return ValidationResult(True, cls, final_url)

    except asyncio.TimeoutError:
        # Timeout — check if it's a known trusted domain (bot protection)
        parsed = urlparse(clean_url)
        domain = parsed.netloc.lower()
        if any(d in domain for d in TRUSTED_DOMAINS):
            cls = "VERIFIED" if is_resource else "ACTIVE"
            return ValidationResult(True, cls, clean_url)
        cls = "INVALID_RESOURCE" if is_resource else "INVALID_LINK"
        return ValidationResult(False, cls, clean_url, error="Connection Timeout")
    except Exception as e:
        # Connection error — check if it's a known trusted domain
        parsed = urlparse(clean_url)
        domain = parsed.netloc.lower()
        if any(d in domain for d in TRUSTED_DOMAINS):
            cls = "VERIFIED" if is_resource else "ACTIVE"
            return ValidationResult(True, cls, clean_url)
        cls = "INVALID_RESOURCE" if is_resource else "INVALID_LINK"
        return ValidationResult(False, cls, clean_url, error=str(e))


async def validate_urls_async(urls: List[str], is_resource: bool = False, concurrency: int = 15) -> List[ValidationResult]:
    """Validate a batch of URLs asynchronously."""
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [_fetch_url(session, url, is_resource=is_resource) for url in urls]
        return await asyncio.gather(*tasks)


def run_full_audit_and_cleanup(db) -> Dict[str, Any]:
    """
    Complete audit and cleanup task:
    1. Audits all Opportunities & Learning Resources in PostgreSQL
    2. Sanitizes legacy ?req_id= query strings
    3. Classifies invalid/closed/expired/stale records
    4. Updates DB statuses
    5. Returns statistics dictionary
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
        "jobs_invalid_link": 0,
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

    # Step 2: Classify Expired jobs (>45 days old)
    expired_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.posted_date < expired_cutoff,
        models.Opportunity.is_active == True
    ).all()
    for j in expired_jobs:
        j.lifecycle_status = "EXPIRED"
        j.is_active = False
        j.status = "Expired"
        stats["jobs_expired"] += 1
    db.commit()

    # Step 3: Classify Stale jobs (30-45 days old)
    stale_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.posted_date >= expired_cutoff,
        models.Opportunity.posted_date < stale_cutoff,
        models.Opportunity.lifecycle_status.in_(["ACTIVE", "NEW", None])
    ).all()
    for j in stale_jobs:
        j.lifecycle_status = "STALE"
        stats["jobs_stale"] += 1
    db.commit()

    # Step 4: Audit & validate active jobs
    active_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.lifecycle_status.in_(["ACTIVE", "NEW", None])
    ).limit(500).all()

    stats["total_jobs_audited"] = len(active_jobs)

    if active_jobs:
        urls = [j.apply_url for j in active_jobs]
        results = asyncio.run(validate_urls_async(urls, is_resource=False))

        for job, res in zip(active_jobs, results):
            job.last_url_verified_at = now
            job.last_verified_at = now

            if not res.is_valid:
                src = job.primary_source or "Unknown"
                stats["noisy_sources"][src] = stats["noisy_sources"].get(src, 0) + 1

                if res.classification == "CLOSED" or res.is_closed:
                    job.lifecycle_status = "CLOSED"
                    job.apply_url_status = "CLOSED"
                    job.is_active = False
                    job.status = "Closed"
                    stats["jobs_closed"] += 1
                else:
                    job.lifecycle_status = "INVALID_LINK"
                    job.apply_url_status = "INVALID_LINK"
                    job.is_active = False
                    job.status = "Invalid Link"
                    stats["jobs_invalid_link"] += 1
            else:
                job.lifecycle_status = "ACTIVE"
                job.apply_url_status = "VALID"
                job.verified_apply_url = res.final_url
                job.is_active = True
                job.status = "Active"
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
