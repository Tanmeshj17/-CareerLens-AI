import logging
import requests
from typing import List, Dict, Any
from .base_ats import ATSParserBase

logger = logging.getLogger(__name__)

class PhenomCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Phenom"

    def fetch_jobs(self) -> List[Dict]:
        """
        Phenom People sites often have a standard API endpoint at:
        https://{identifier}.phenompeople.com/api/jobs/v1/search
        """
        # Phenom sites usually use the company name in the subdomain or a specific endpoint
        url = f"https://{self.ats_identifier}.phenompro.com/api/jobs/v1/search"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "keyword": "",
            "location": "India", # Target India specifically
            "from": 0,
            "size": 100
        }
        
        jobs = []
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "jobs" in data["data"]:
                    jobs = data["data"]["jobs"]
            else:
                self.health_score -= 10
                logger.warning(f"[Phenom] {self.company_name} returned {response.status_code}")
                
        except Exception as e:
            self.errors.append(str(e))
            self.health_score -= 20
            logger.debug(f"[Phenom] {self.company_name} fetch failed: {e}")

        self.jobs_collected = len(jobs)
        return jobs

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        try:
            title = raw_job.get("title", "Unknown Title")
            location = raw_job.get("location", "India")
            apply_url = raw_job.get("applyUrl")
            
            if not apply_url:
                job_id = raw_job.get("jobId", "")
                apply_url = f"https://careers.{self.ats_identifier}.com/job/{job_id}"
                
            job_data = {
                "title": title,
                "company": self.company_name,
                "location": location,
                "job_type": raw_job.get("jobType", "Job"),
                "description": raw_job.get("description", f"Role at {self.company_name} via Phenom."),
                "apply_url": apply_url,
                "source_url": f"https://careers.{self.ats_identifier}.com",
                "ats_type": self.ats_type,
                "raw_data": raw_job
            }
            return self.normalize(job_data)
        except Exception as e:
            self.errors.append(f"Parse error: {e}")
            return {}
