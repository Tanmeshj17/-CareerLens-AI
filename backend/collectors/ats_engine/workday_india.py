"""
Shared Workday Career Site Collector Base
Uses the undocumented but publicly accessible Workday CXS job board JSON API.
Each Workday tenant uses: POST https://{company}.wd{n}.myworkdayjobs.com/wday/cxs/{company}/{board}/jobs
"""
import logging
import requests
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger("workday_base")

INDIA_KEYWORDS = {
    "india", "bangalore", "bengaluru", "chennai", "hyderabad", "pune",
    "mumbai", "noida", "delhi", "kolkata", "gurugram", "gurgaon",
    "ncr", "ahmedabad", "kochi", "cochin", "coimbatore", "nagpur"
}

WORKDAY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}


def is_india_location(location: str) -> bool:
    loc_lower = location.lower()
    return any(kw in loc_lower for kw in INDIA_KEYWORDS)


def fetch_workday_jobs(
    subdomain: str,       # e.g. "hcl"
    tenant_num: str,      # e.g. "wd1"
    company_path: str,    # e.g. "hcl"
    board_name: str,      # e.g. "HCLCareers"
    company_display: str, # e.g. "HCL Technologies"
    max_results: int = 50,
    india_only: bool = True,
) -> List[Dict[str, Any]]:
    """Fetch jobs from a Workday-powered careers site."""
    jobs = []
    base_url = f"https://{subdomain}.{tenant_num}.myworkdayjobs.com"
    api_url = f"{base_url}/wday/cxs/{company_path}/{board_name}/jobs"

    # Try with India location facet first, then without
    payloads = [
        # With India keyword search
        {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "India"},
        # Without filter (get all, then filter client-side)
        {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""},
    ]

    for payload in payloads:
        try:
            resp = requests.post(
                api_url,
                json=payload,
                headers=WORKDAY_HEADERS,
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                postings = data.get("jobPostings", [])
                count = 0
                for job in postings:
                    title = job.get("title", "")
                    location = job.get("locationsText", "India")
                    job_path = job.get("externalPath", "")
                    apply_url = f"{base_url}/{board_name}{job_path}" if job_path else base_url

                    if india_only and location and not is_india_location(location):
                        continue

                    jobs.append({
                        "title": title,
                        "company": company_display,
                        "location": location or "India",
                        "job_type": "Full-time",
                        "description": f"{title} at {company_display}. Location: {location}. Apply via official career portal.",
                        "apply_url": apply_url,
                        "source": f"{company_display} Careers",
                        "source_url": apply_url,
                        "ats_type": "Workday",
                        "raw_data": {"source_type": "Workday CXS API"},
                    })
                    count += 1

                if count > 0:
                    logger.info(f"  {company_display}: {count} India jobs via Workday")
                    break  # Success — no need to try second payload
                elif postings:
                    # Got results but none matched India filter — try second payload
                    continue
                else:
                    break  # Empty response
            elif resp.status_code in (403, 429):
                logger.warning(f"  {company_display}: Rate limited ({resp.status_code})")
                break
            else:
                logger.debug(f"  {company_display}: HTTP {resp.status_code} from {api_url}")
                break
        except Exception as e:
            logger.warning(f"  {company_display} Workday fetch error: {e}")
            break

        time.sleep(0.5)

    return jobs
