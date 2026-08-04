import logging
import requests
from typing import List, Dict, Any
from .base_ats import ATSParserBase

logger = logging.getLogger(__name__)

class EightfoldCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Eightfold"

    def fetch_jobs(self) -> List[Dict]:
        """
        Eightfold.ai standard API:
        https://{identifier}.eightfold.ai/api/apply/v2/jobs
        """
        url = f"https://{self.ats_identifier}.eightfold.ai/api/apply/v2/jobs"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        
        # Eightfold allows query params like domain
        params = {
            "domain": f"{self.ats_identifier}.com",
            "start": 0,
            "num": 100,
            "location": "India"
        }
        
        jobs = []
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if "positions" in data:
                    jobs = data["positions"]
            else:
                self.health_score -= 10
                logger.warning(f"[Eightfold] {self.company_name} returned {response.status_code}")
                
        except Exception as e:
            self.errors.append(str(e))
            self.health_score -= 20
            logger.debug(f"[Eightfold] {self.company_name} fetch failed: {e}")

        self.jobs_collected = len(jobs)
        return jobs

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        try:
            title = raw_job.get("name", "Unknown Title")
            locations = raw_job.get("locations", ["India"])
            location = locations[0] if isinstance(locations, list) and len(locations) > 0 else "India"
            job_id = raw_job.get("id", "")
            
            apply_url = raw_job.get("url")
            if not apply_url:
                apply_url = f"https://{self.ats_identifier}.eightfold.ai/careers?job_id={job_id}"
                
            job_data = {
                "title": title,
                "company": self.company_name,
                "location": location,
                "job_type": "Job",
                "description": raw_job.get("job_description", f"Role at {self.company_name} via Eightfold."),
                "apply_url": apply_url,
                "source_url": f"https://{self.ats_identifier}.eightfold.ai/careers",
                "ats_type": self.ats_type,
                "raw_data": raw_job
            }
            return self.normalize(job_data)
        except Exception as e:
            self.errors.append(f"Parse error: {e}")
            return {}
