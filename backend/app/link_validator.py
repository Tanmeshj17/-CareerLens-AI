import asyncio
import aiohttp
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from urllib.parse import urlparse

logger = logging.getLogger("link_validator")

# Keywords that strongly indicate a job is closed
CLOSED_KEYWORDS = [
    re.compile(r"applications (are )?closed", re.IGNORECASE),
    re.compile(r"job (has )?expired", re.IGNORECASE),
    re.compile(r"position is no longer available", re.IGNORECASE),
    re.compile(r"no longer accepting applications", re.IGNORECASE),
    re.compile(r"position (has been )?filled", re.IGNORECASE),
    re.compile(r"this job is no longer active", re.IGNORECASE)
]

class ValidationResult:
    def __init__(self, is_valid: bool, status: str, final_url: str, is_closed: bool = False, error: str = None):
        self.is_valid = is_valid
        self.status = status
        self.final_url = final_url
        self.is_closed = is_closed
        self.error = error

async def _fetch_url(session: aiohttp.ClientSession, url: str, retries: int = 2) -> ValidationResult:
    for attempt in range(retries + 1):
        try:
            # 1. Try HEAD first
            try:
                async with session.head(url, allow_redirects=True, timeout=10) as resp:
                    if resp.status in (404, 410):
                        return ValidationResult(False, "BROKEN", str(resp.url), error=f"HTTP {resp.status}")
                    if resp.status == 403 or resp.status == 429:
                        # Cloudflare or rate limit - fallback to GET if possible, or mark as blocked
                        pass
                    elif resp.status < 400:
                        # Success, but we can't read text for closed keywords
                        final_url = str(resp.url)
                        return ValidationResult(True, "VERIFIED_DIRECT", final_url)
            except Exception:
                pass # Fallback to GET

            # 2. Try GET to read body for 'closed' keywords
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            async with session.get(url, allow_redirects=True, timeout=15, headers=headers) as resp:
                final_url = str(resp.url)
                
                if resp.status in (404, 410):
                    return ValidationResult(False, "BROKEN", final_url, error=f"HTTP {resp.status}")
                
                if resp.status >= 500:
                    if attempt < retries:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    return ValidationResult(False, "UNKNOWN", final_url, error=f"HTTP {resp.status}")
                    
                if resp.status in (403, 429):
                    # Probably bot protection.
                    return ValidationResult(True, "BROWSER_VERIFICATION_REQUIRED", final_url)
                    
                # Read text to check for closed keywords
                try:
                    text = await resp.text()
                    for keyword_re in CLOSED_KEYWORDS:
                        if keyword_re.search(text):
                            return ValidationResult(False, "CLOSED", final_url, is_closed=True)
                except Exception:
                    pass # If can't read text, assume valid if status < 400
                    
                return ValidationResult(True, "VERIFIED_DIRECT", final_url)

        except asyncio.TimeoutError:
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
                continue
            return ValidationResult(False, "UNKNOWN", url, error="Timeout")
        except Exception as e:
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
                continue
            return ValidationResult(False, "BROKEN", url, error=str(e))
    return ValidationResult(False, "UNKNOWN", url, error="Max retries reached")

async def validate_links_async(urls: List[str], concurrency: int = 20) -> List[ValidationResult]:
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def run_tier_validation(db):
    """
    Tiered strategy:
    0-3 days: 6 hours
    4-7 days: 12 hours
    8-30 days: 24 hours
    >30 days: archived (handled separately)
    """
    from app.models import Opportunity
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    
    # Tier 1: 0-3 days, validated > 6h ago
    tier1_limit_time = now - timedelta(hours=6)
    tier1_age_limit = now - timedelta(days=3)
    
    # Tier 2: 4-7 days, validated > 12h ago
    tier2_limit_time = now - timedelta(hours=12)
    tier2_age_limit = now - timedelta(days=7)
    
    # Tier 3: 8-30 days, validated > 24h ago
    tier3_limit_time = now - timedelta(hours=24)
    tier3_age_limit = now - timedelta(days=30)
    
    # Find records to validate
    # This is a simplified logic, we should ideally fetch records falling in each bucket
    
    # A generic query that fetches any active record needing validation based on the tier
    # Using SQLAlchemy OR logic
    from sqlalchemy import or_, and_
    
    # Age is (now - first_seen)
    opps = db.query(Opportunity).filter(
        Opportunity.status == "ACTIVE",
        Opportunity.apply_url.isnot(None),
        or_(
            # Tier 1
            and_(Opportunity.first_seen >= tier1_age_limit, 
                 or_(Opportunity.last_url_verified_at < tier1_limit_time, Opportunity.last_url_verified_at.is_(None))),
            # Tier 2
            and_(Opportunity.first_seen < tier1_age_limit, Opportunity.first_seen >= tier2_age_limit, 
                 or_(Opportunity.last_url_verified_at < tier2_limit_time, Opportunity.last_url_verified_at.is_(None))),
            # Tier 3
            and_(Opportunity.first_seen < tier2_age_limit, Opportunity.first_seen >= tier3_age_limit, 
                 or_(Opportunity.last_url_verified_at < tier3_limit_time, Opportunity.last_url_verified_at.is_(None)))
        )
    ).limit(500).all()
    
    if not opps:
        return 0
        
    urls = [opp.apply_url for opp in opps]
    results = asyncio.run(validate_links_async(urls))
    
    for opp, result in zip(opps, results):
        opp.last_url_verified_at = now
        opp.last_verified_at = now
        opp.apply_url_status = result.status
        opp.verified_apply_url = result.final_url
        
        if result.is_closed:
            opp.status = "CLOSED"
            opp.lifecycle_status = "CLOSED"
        elif not result.is_valid and result.status == "BROKEN":
            # For simplicity, if it's broken, mark as INVALID.
            opp.status = "INVALID"
            opp.lifecycle_status = "INVALID"
            
    db.commit()
    return len(opps)

async def _fetch_resource_url(session: aiohttp.ClientSession, url: str) -> ValidationResult:
    try:
        async with session.get(url, allow_redirects=True, timeout=15) as resp:
            final_url = str(resp.url)
            if resp.status in (404, 410, 403):
                return ValidationResult(False, "INVALID_RESOURCE", final_url, error=f"HTTP {resp.status}")
            
            # Simple check for youtube video unavailable
            if "youtube.com" in url or "youtu.be" in url:
                try:
                    text = await resp.text()
                    if "Video unavailable" in text or "Private video" in text:
                        return ValidationResult(False, "INVALID_RESOURCE", final_url, error="Video Unavailable")
                except Exception:
                    pass
            
            return ValidationResult(True, "VERIFIED", final_url)
    except Exception as e:
        return ValidationResult(False, "INVALID_RESOURCE", url, error=str(e))

async def validate_resources_async(urls: List[str], concurrency: int = 10) -> List[ValidationResult]:
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_fetch_resource_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def run_learning_validation(db):
    """Validates learning resources and marks broken ones as INVALID_RESOURCE"""
    from app.models import LearningResource
    
    resources = db.query(LearningResource).filter(
        LearningResource.status == "VERIFIED"
    ).limit(100).all()
    
    if not resources:
        return 0
        
    urls = [res.url for res in resources]
    results = asyncio.run(validate_resources_async(urls))
    
    for res, result in zip(resources, results):
        if not result.is_valid:
            res.status = "INVALID_RESOURCE"
            
    db.commit()
    return len(resources)
