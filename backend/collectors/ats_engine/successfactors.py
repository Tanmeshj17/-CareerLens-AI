import logging
import requests
from typing import List, Dict, Any
from .base_ats import ATSParserBase

logger = logging.getLogger(__name__)

class SuccessFactorsCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "SuccessFactors"

    def fetch_jobs(self) -> List[Dict]:
        """
        SuccessFactors usually exposes an OData API or a standard careers page.
        Endpoint: https://{host}/career?company={company_id}
        For programmatic access, many use: https://{host}/career/jobReqUI?jobId=...
        We'll use a mocked JSON API endpoint approach often seen in career sites.
        """
        # ats_identifier is usually the company ID for SAP SF
        # SuccessFactors instances are hosted on domains like jobs.sap.com or specific datacenters
        # For simplicity, we'll try a generic known SF API pattern or scrape.
        # Since this is an engine template, we mock the request structure.
        url = f"https://jobs.successfactors.com/api/v2/jobs?company={self.ats_identifier}"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        
        jobs = []
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if "jobs" in data:
                    jobs = data["jobs"]
            else:
                self.health_score -= 10
                logger.warning(f"[SuccessFactors] {self.company_name} returned {response.status_code}")
                
        except Exception as e:
            self.errors.append(str(e))
            self.health_score -= 20
            logger.debug(f"[SuccessFactors] {self.company_name} fetch failed: {e}")

        self.jobs_collected = len(jobs)
        return jobs

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        try:
            title = raw_job.get("title", "Unknown Title")
            location = raw_job.get("location", "India")
            job_id = raw_job.get("id", "")
            
            # The apply URL for SF usually requires the company ID
            apply_url = f"https://careers.successfactors.com/career?company={self.ats_identifier}&jobId={job_id}"
            
            job_data = {
                "title": title,
                "company": self.company_name,
                "location": location,
                "job_type": "Job",
                "description": raw_job.get("description", f"Role at {self.company_name} via SuccessFactors."),
                "apply_url": apply_url,
                "source_url": f"https://careers.successfactors.com/career?company={self.ats_identifier}",
                "ats_type": self.ats_type,
                "raw_data": raw_job
            }
            return self.normalize(job_data)
        except Exception as e:
            self.errors.append(f"Parse error: {e}")
            return {}
