import json
import time
from typing import Dict, Any, List
from .base_ats import ATSParserBase
import requests

class WorkdayCollector(ATSParserBase):
    def __init__(self, company_name: str, tenant: str, site: str, timeout: int = 15, retries: int = 3):
        super().__init__(company_name, f"{tenant}/{site}", timeout, retries)
        self.tenant = tenant
        self.site = site or "External"

    @property
    def ats_type(self) -> str:
        return "Workday"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.tenant}.myworkdayjobs.com/wday/cxs/{self.tenant}/{self.site}/jobs"
        all_jobs = []
        offset = 0
        limit = 20
        max_pages = 20 # cap at 400 jobs to avoid runaway loops
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        for _ in range(max_pages):
            payload = {
                "appliedFacets": {},
                "limit": limit,
                "offset": offset,
                "searchText": ""
            }
            
            attempt = 0
            success = False
            while attempt < self.retries and not success:
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                    if response.status_code == 429:
                        time.sleep(2 ** attempt)
                        attempt += 1
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    jobs = data.get("jobPostings", [])
                    all_jobs.extend(jobs)
                    
                    if not jobs or len(jobs) < limit:
                        return all_jobs # Reached end
                    
                    offset += limit
                    success = True
                    time.sleep(0.5) # simple rate limit padding
                    
                except requests.exceptions.RequestException as e:
                    attempt += 1
                    self.health_score -= 5
                    self.errors.append(f"Page offset {offset} error: {str(e)[:50]}")
                    if attempt >= self.retries:
                        return all_jobs # Return whatever we got so far

        return all_jobs

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        location = raw_job.get("locationsText", "Remote")
        job_type = raw_job.get("timeType", "Full-time")
        job_id = raw_job.get("bulletinId", raw_job.get("id", ""))
        
        apply_url = f"https://{self.tenant}.myworkdayjobs.com/en-US/{self.site}/job/{job_id}"
        if raw_job.get("externalPath"):
            apply_url = f"https://{self.tenant}.myworkdayjobs.com/en-US/{self.site}{raw_job.get('externalPath')}"
            
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": location,
            "job_type": job_type,
            "description": "", 
            "apply_url": apply_url,
            "source_url": apply_url,
            "raw_data": json.dumps(raw_job)
        }
