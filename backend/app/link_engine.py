"""
Phase 8.55: Direct Apply Link Integrity Engine
Classifies, verifies, and scores job apply URLs.
"""
import re
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger("link_engine")

# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------
class LinkStatus:
    VERIFIED_DIRECT = "VERIFIED_DIRECT"           # Exact direct job posting URL (score 100)
    VERIFIED_POSTING = "VERIFIED_POSTING"          # Stable per-job ATS page (score 95)
    BROWSER_VERIFICATION_REQUIRED = "BROWSER_VERIFICATION_REQUIRED"  # 403/Cloudflare (score 85)
    CAREER_BOARD = "CAREER_BOARD"                 # Company careers board (score 50)
    UNKNOWN = "UNKNOWN"                            # Timeout / unable to verify (score 25)
    HOMEPAGE_ONLY = "HOMEPAGE_ONLY"               # Redirects to generic homepage (score 0)
    BROKEN = "BROKEN"                              # 404 / 410 / DNS failure (score 0)

LINK_QUALITY_SCORES = {
    LinkStatus.VERIFIED_DIRECT:               100,
    LinkStatus.VERIFIED_POSTING:               95,
    LinkStatus.BROWSER_VERIFICATION_REQUIRED:  85,
    LinkStatus.CAREER_BOARD:                   50,
    LinkStatus.UNKNOWN:                        25,
    LinkStatus.HOMEPAGE_ONLY:                   0,
    LinkStatus.BROKEN:                          0,
}

# ---------------------------------------------------------------------------
# Source Tier definitions (used for link classification labels)
# ---------------------------------------------------------------------------
TIER_A_PATTERNS = [
    ("greenhouse", r"boards\.greenhouse\.io/[\w-]+/jobs/\d+"),
    ("lever",      r"jobs\.lever\.co/[\w-]+/[\w-]+"),
    ("ashby",      r"jobs\.ashbyhq\.com/[\w-]+/"),
    ("smartrecruiters", r"jobs\.smartrecruiters\.com/[\w-]+/"),
]

TIER_B_PATTERNS = [
    ("workday",    r"myworkdayjobs\.com"),
    ("icims",      r"careers\.icims\.com/jobs/\d+"),
    ("taleo",      r"\.taleo\.net/careersection/"),
    ("successfactors", r"successfactors\.(eu|com)/career"),
    ("eightfold",  r"app\.eightfold\.ai/careers"),
    ("phenom",     r"[\w-]+\.phenompeople\.com"),
    ("brassring",  r"tbe\.taleo\.net|brassring\.com"),
    ("kenexa",     r"krb-xjobs\.brassring\.com"),
]

TIER_C_PATTERNS = [
    ("internshala", r"internshala\.com/internship|internshala\.com/jobs"),
    ("unstop",      r"unstop\.com/(competitions|jobs|internships)/"),
    ("foundit",     r"foundit\.in/job/"),
    ("wellfound",   r"wellfound\.com/jobs"),
    ("instahyre",   r"instahyre\.com/jobs"),
    ("freshersworld", r"freshersworld\.com/jobs"),
    ("naukri",      r"naukri\.com/job-listings"),
    ("linkedin",    r"linkedin\.com/jobs/view/"),
    ("indeed",      r"indeed\.com/viewjob"),
    ("shine",       r"shine\.com/job-search/"),
    ("timesjobs",   r"timesjobs\.com/job-detail"),
]

# Generic career page and homepage patterns to detect redirects
CAREER_BOARD_PATTERNS = [
    r"careers\.([\w-]+)\.(com|io|co|in|net)/?$",
    r"([\w-]+)\.(com|io|co|in|net)/careers/?$",
    r"([\w-]+)\.(com|io|co|in|net)/jobs/?$",
    r"([\w-]+)\.(com|io|co|in|net)/job-openings/?$",
    r"([\w-]+)\.(com|io|co|in|net)/work-with-us/?$",
    r"([\w-]+)\.(com|io|co|in|net)/join-us/?$",
    r"([\w-]+)\.(com|io|co|in|net)/en-us/careers/?$",
    r"boards\.greenhouse\.io/[\w-]+/?$",       # Greenhouse company board (no job id)
    r"jobs\.lever\.co/[\w-]+/?$",              # Lever company board
]

HOMEPAGE_PATTERNS = [
    r"^https?://(www\.)?([\w-]+)\.(com|io|co|in|net|org)/?$",       # Bare domain
    r"^https?://(www\.)?([\w-]+)\.(com|io|co|in|net|org)/?(#.*)?$", # With hash
]


# ---------------------------------------------------------------------------
# URL Pattern Classification (no network required)
# ---------------------------------------------------------------------------
def classify_url_by_pattern(url: Optional[str]) -> Tuple[str, str, int]:
    """
    Classify a URL purely by pattern matching (no network call).
    Returns: (status, classification_label, quality_score)
    """
    if not url or not url.startswith("http"):
        return LinkStatus.BROKEN, "No URL", 0

    # Tier A — Direct ATS job posting URLs
    for platform, pattern in TIER_A_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return LinkStatus.VERIFIED_DIRECT, f"Tier A - {platform.title()}", 100

    # Tier B — ATS platforms (may require browser verification)
    for platform, pattern in TIER_B_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return LinkStatus.BROWSER_VERIFICATION_REQUIRED, f"Tier B - {platform.title()}", 85

    # Tier C — Aggregators with per-job URLs
    for platform, pattern in TIER_C_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return LinkStatus.VERIFIED_POSTING, f"Tier C - {platform.title()}", 70

    # Career board detection (known generic board pages, no specific job ID)
    for pattern in CAREER_BOARD_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return LinkStatus.CAREER_BOARD, "Company Career Board", 50

    # Homepage detection
    for pattern in HOMEPAGE_PATTERNS:
        if re.match(pattern, url, re.IGNORECASE):
            return LinkStatus.HOMEPAGE_ONLY, "Company Homepage", 0

    # Default: unknown but has URL
    return LinkStatus.UNKNOWN, "Unknown Source", 25


# ---------------------------------------------------------------------------
# Extract source_job_id from URL
# ---------------------------------------------------------------------------
def extract_job_id(url: Optional[str]) -> Optional[str]:
    """Extract a stable job/posting ID from known ATS URL patterns."""
    if not url:
        return None
    # Greenhouse: /jobs/12345
    m = re.search(r'/jobs/(\d+)', url)
    if m:
        return m.group(1)
    # Lever: /company/uuid
    m = re.search(r'lever\.co/[\w-]+/([\w-]{8,})', url)
    if m:
        return m.group(1)
    # Internshala: /internship/detail/ID
    m = re.search(r'/(?:internship|job)s?(?:/detail)?/[\w-]+-(\d+)', url)
    if m:
        return m.group(1)
    # Unstop: /competitions/ID or /jobs/ID
    m = re.search(r'/(competitions|jobs|internships)/[^/]+-(\d+)', url)
    if m:
        return m.group(2)
    return None


# ---------------------------------------------------------------------------
# Async URL Verification (with network call)
# ---------------------------------------------------------------------------
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

async def verify_url_async(url: str, timeout: int = 8) -> Tuple[str, str, int, Optional[str]]:
    """
    Verify a URL with an async HTTP request.
    Returns: (status, classification, quality_score, final_url)
    """
    if not url or not url.startswith("http"):
        return LinkStatus.BROKEN, "No URL", 0, None

    try:
        conn = aiohttp.TCPConnector(ssl=False)
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
            connector=conn,
            headers=REQUEST_HEADERS,
            timeout=timeout_obj
        ) as session:
            # Try HEAD first, fall back to GET if needed
            try:
                async with session.head(url, allow_redirects=True, max_redirects=5) as resp:
                    status_code = resp.status
                    final_url = str(resp.url)
                    # Some servers block HEAD — if we get 405, fall through to GET
                    if status_code == 405:
                        raise aiohttp.ClientError("HEAD blocked, retry GET")
            except (aiohttp.ClientError, asyncio.TimeoutError):
                async with session.get(url, allow_redirects=True, max_redirects=5) as resp:
                    status_code = resp.status
                    final_url = str(resp.url)

        return _evaluate_result(url, status_code, final_url)

    except asyncio.TimeoutError:
        # Timeout → Unknown, but don't punish (might be a slow ATS)
        pattern_status, label, score = classify_url_by_pattern(url)
        return LinkStatus.UNKNOWN, label, min(score, 25), url
    except Exception as e:
        logger.debug(f"verify_url_async error for {url}: {e}")
        return LinkStatus.UNKNOWN, "Verification Error", 25, url


def _evaluate_result(
    original_url: str, http_status: int, final_url: str
) -> Tuple[str, str, int, str]:
    """
    Decide the link status given the HTTP result.
    Key rule: 403 → BROWSER_VERIFICATION_REQUIRED, never BROKEN.
    """
    # --- Bot-blocked (Cloudflare/Incapsula/etc.) ---
    if http_status == 403:
        pattern_status, label, pattern_score = classify_url_by_pattern(original_url)
        return LinkStatus.BROWSER_VERIFICATION_REQUIRED, label, max(pattern_score, 85), original_url

    # --- Definitively broken ---
    if http_status in (404, 410, 0):
        return LinkStatus.BROKEN, "Broken / Expired", 0, final_url

    # --- Server error (5xx) — treat as UNKNOWN to avoid false negatives ---
    if http_status >= 500:
        return LinkStatus.UNKNOWN, "Server Error", 25, final_url

    # --- Successful redirect / 200 ---
    if http_status in (200, 301, 302, 307, 308) or (200 <= http_status < 400):
        # Detect homepage redirect (original had job ID, final doesn't)
        original_has_id = bool(extract_job_id(original_url))
        final_has_id = bool(extract_job_id(final_url))

        if original_has_id and not final_has_id:
            # Job ID was stripped → likely redirected to homepage/board
            return LinkStatus.HOMEPAGE_ONLY, "Redirected to Homepage", 0, final_url

        # Classify the final URL by pattern
        status, label, score = classify_url_by_pattern(final_url)
        return status, label, score, final_url

    # Fallback
    return classify_url_by_pattern(original_url) + (original_url,)


# ---------------------------------------------------------------------------
# Synchronous wrapper (for use in sync ETL jobs)
# ---------------------------------------------------------------------------
def verify_url(url: str, timeout: int = 8) -> Tuple[str, str, int, Optional[str]]:
    """
    Synchronous wrapper around verify_url_async.
    Returns: (status, classification, quality_score, final_url)
    """
    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(verify_url_async(url, timeout))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"verify_url sync wrapper error: {e}")
        status, label, score = classify_url_by_pattern(url)
        return status, label, score, url


# ---------------------------------------------------------------------------
# Batch verification helper
# ---------------------------------------------------------------------------
async def verify_batch_async(
    opportunities: list, timeout: int = 8
) -> list:
    """
    Verify a batch of opportunities asynchronously.
    Returns list of (opp, status, classification, score, final_url) tuples.
    """
    async def _verify_one(opp):
        status, classification, score, final_url = await verify_url_async(
            opp.apply_url, timeout
        )
        return opp, status, classification, score, final_url

    tasks = [_verify_one(opp) for opp in opportunities]
    return await asyncio.gather(*tasks)


def verify_batch(opportunities: list, timeout: int = 8) -> list:
    """Synchronous batch verify. Returns list of (opp, status, classification, score, final_url)."""
    loop = asyncio.new_event_loop()
    results = loop.run_until_complete(verify_batch_async(opportunities, timeout))
    loop.close()
    return results


# ---------------------------------------------------------------------------
# Classification-only (no network) — for quick ingest classification
# ---------------------------------------------------------------------------
def classify_and_score(url: Optional[str]) -> dict:
    """
    Pattern-only classification for use during ingestion (no network call).
    Returns a dict ready to merge into an Opportunity record.
    """
    status, classification, score = classify_url_by_pattern(url)
    job_id = extract_job_id(url)
    return {
        "apply_url_status": status,
        "link_classification": classification,
        "link_quality_score": score,
        "source_job_id": job_id,
        "verified_apply_url": url,
    }
