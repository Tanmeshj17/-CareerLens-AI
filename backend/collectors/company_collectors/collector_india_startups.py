"""
Phase 7.7: India Startup Collector (Dynamic)
Reads from CompanyRegistry instead of hardcoded lists.
Supports Greenhouse, Lever, SmartRecruiters, Ashby.
"""
import logging
import requests
import time
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..base_collector import BaseCollector
from app.database import SessionLocal
from app.models import CompanyRegistry

logger = logging.getLogger("collector_india_startups")

INDIA_KEYWORDS = {"india", "bangalore", "bengaluru", "chennai", "hyderabad", "pune", "mumbai", "noida", "delhi", "kolkata", "gurugram", "gurgaon", "remote"}

class IndiaStartupCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "India Startups (Dynamic Registry)"

    def _is_india_job(self, location: str) -> bool:
        if not location:
            return False
        loc_lower = location.lower()
        return any(kw in loc_lower for kw in INDIA_KEYWORDS)

    def _fetch_greenhouse(self, slug: str, company: str) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                for job in res.json().get("jobs", []):
                    location = job.get("location", {}).get("name", "India")
                    if not self._is_india_job(location):
                        continue
                    
                    title = job.get("title", "")
                    content = job.get("content", "")
                    apply_url = job.get("absolute_url", "")
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "job_type": "Full-time",
                        "description": (content[:800] if content else title),
                        "apply_url": apply_url,
                        "source": f"{company} via Greenhouse",
                        "source_url": apply_url,
                        "ats_type": "Greenhouse",
                        "raw_data": {"slug": slug}
                    })
        except Exception as e:
            logger.debug(f"Greenhouse fetch failed for {slug}: {e}")
        return jobs

    def _fetch_lever(self, slug: str, company: str) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                for posting in res.json():
                    location = posting.get("categories", {}).get("location", "India")
                    if not self._is_india_job(location):
                        continue
                        
                    title = posting.get("text", "")
                    apply_url = posting.get("hostedUrl", "")
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "job_type": posting.get("categories", {}).get("commitment", "Full-time"),
                        "description": posting.get("descriptionPlain", "")[:800],
                        "apply_url": apply_url,
                        "source": f"{company} via Lever",
                        "source_url": apply_url,
                        "ats_type": "Lever",
                        "raw_data": {"slug": slug}
                    })
        except Exception as e:
            logger.debug(f"Lever fetch failed for {slug}: {e}")
        return jobs

    def _fetch_smartrecruiters(self, slug: str, company: str) -> List[Dict[str, Any]]:
        jobs = []
        try:
            offset = 0
            limit = 50
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            
            while True:
                url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit={limit}&offset={offset}"
                res = requests.get(url, headers=headers, timeout=12)
                if res.status_code != 200:
                    break
                    
                data = res.json()
                content = data.get("content", [])
                if not content:
                    break
                    
                for posting in content:
                    location = posting.get("location", {})
                    city = location.get("city", "")
                    loc_str = f"{city}, India" if city else "India"
                    
                    if not self._is_india_job(loc_str):
                        continue
                        
                    apply_url = f"https://jobs.smartrecruiters.com/{slug}/{posting.get('id', '')}"
                    
                    jobs.append({
                        "title": posting.get("name", ""),
                        "company": company,
                        "location": loc_str,
                        "job_type": "Full-time",
                        "description": f"{posting.get('name', '')} at {company} in {loc_str}",
                        "apply_url": apply_url,
                        "source": f"{company} via SmartRecruiters",
                        "source_url": apply_url,
                        "ats_type": "SmartRecruiters",
                        "raw_data": {"slug": slug}
                    })
                    
                total_found = data.get("totalFound", 0)
                offset += limit
                if offset >= total_found or offset > 500: # hard cap at 500
                    break
        except Exception as e:
            logger.debug(f"SmartRecruiters fetch failed for {slug}: {e}")
        return jobs

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting Dynamic India Startup collection...")
        db: Session = SessionLocal()
        
        # Pull all promoted active startup & product sources from registry
        sources = db.query(CompanyRegistry).filter(
            CompanyRegistry.collector_enabled == True,
            CompanyRegistry.validation_status == "Active"
        ).order_by(CompanyRegistry.india_hiring_priority.desc()).all()
        
        db.close()
        
        all_jobs = []
        
        for source in sources:
            company = source.company_name
            slug = source.ats_identifier
            ats = source.ats_type
            
            if not slug or not ats:
                continue
                
            jobs = []
            if ats == "Greenhouse":
                jobs = self._fetch_greenhouse(slug, company)
            elif ats == "Lever":
                jobs = self._fetch_lever(slug, company)
            elif ats == "SmartRecruiters":
                jobs = self._fetch_smartrecruiters(slug, company)
                
            if jobs:
                logger.info(f"  Collected {len(jobs)} from {company} ({ats})")
                all_jobs.extend(jobs)
                
            time.sleep(0.5)
            
        self.health_status = "Healthy" if all_jobs else "Warning"
        logger.info(f"Dynamic Collector Total: {len(all_jobs)} jobs.")
        return all_jobs
