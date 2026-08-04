import requests
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class UnstopCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Unstop"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        # We will collect internships, jobs, hackathons, and competitions
        opportunity_types = ["internships", "jobs", "hackathons", "competitions", "scholarships"]
        
        for opp_type in opportunity_types:
            logger.info(f"[Unstop] Fetching {opp_type}")
            page = 1
            consecutive_dupes = 0
            stop_type = False
            
            while page <= max_pages:
                url = f"https://unstop.com/api/public/opportunity/search-result?opportunity={opp_type}&page={page}"
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code == 429:
                        logger.warning(f"[Unstop] Rate limited. Sleeping.")
                        time.sleep(5)
                        continue
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    items = data.get("data", {}).get("data", [])
                    if not items:
                        break # End of pagination
                        
                    for item in items:
                        title = item.get("title", "Unknown Title")
                        company = item.get("organization", {}).get("name") or item.get("seo_url", "").split("-")[0].capitalize()
                        if not company or company == "Unknown":
                            company = "Unstop Host"
                            
                        # Extract location
                        region = item.get("region", "")
                        job_type = "Job"
                        if opp_type == "internships":
                            job_type = "Internship"
                        elif opp_type == "hackathons":
                            job_type = "Hackathon"
                        elif opp_type == "competitions":
                            job_type = "Competition"
                        elif opp_type == "scholarships":
                            job_type = "Scholarship"
                            
                        # Unstop is an India-first platform; default location to India
                        # region="" (empty string) must also fall through to the India default
                        location_str = region.strip() if region and region.strip() else "India"

                        # Build details — include India signal for geographic filter
                        description = f"{job_type} opportunity in India at {company}."
                        if item.get("eligibility"):
                            description += f" Eligibility: {item.get('eligibility')}."

                        apply_url = item.get("seo_url")
                        if apply_url and not apply_url.startswith("http"):
                            apply_url = f"https://unstop.com/{apply_url}"

                        if not apply_url:
                            continue

                        # Phase 8.45: Circuit Breaker
                        if apply_url in known_urls:
                            consecutive_dupes += 1
                        else:
                            consecutive_dupes = 0

                        if consecutive_dupes >= 20:
                            logger.info(f"[Unstop] Circuit breaker triggered on {opp_type}, page {page}")
                            stop_type = True
                            break

                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location_str,
                            "job_type": job_type,
                            "description": description,
                            "apply_url": apply_url,
                            "source_url": "https://unstop.com",
                            "source": self.source_name,
                            "ats_type": "Unstop",
                            "raw_data": item
                        })

                    
                    if stop_type:
                        break
                        
                    page += 1
                    time.sleep(0.5)
                except requests.exceptions.RequestException as e:
                    logger.warning(f"[Unstop] API error on page {page} for {opp_type}: {e}")
                    break
                except Exception as e:
                    logger.error(f"[Unstop] Parsing error: {e}")
                    break
 
        return all_jobs
