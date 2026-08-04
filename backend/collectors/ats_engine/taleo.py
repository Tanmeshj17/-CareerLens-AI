import logging
import requests
from typing import List, Dict, Any
from .base_ats import ATSParserBase
import time

logger = logging.getLogger(__name__)

class TaleoCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Taleo"

    def fetch_jobs(self) -> List[Dict]:
        """
        Taleo commonly uses an ajax endpoint for job search.
        Format: https://{company}.taleo.net/careersection/ex/jobsearch.ajax
        We'll attempt a standard payload to fetch jobs.
        """
        # Taleo can be hosted on different domains, we'll try the standard one.
        # Sometimes ats_identifier is just the company name.
        url = f"https://{self.ats_identifier}.taleo.net/careersection/ex/jobsearch.ajax"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # A common payload to get the first 50 jobs
        payload = {
            "multilineEnabled": False,
            "sortingSelection": {"sortBySelectionParam": "3", "ascendingSortingOrder": "false"},
            "fieldData": {"fields": {"ITEM_RN": "", "MANDATORY": ""}, "filterName": ""},
            "filterSelectionParam": {"searchFilterSelections": [{"id": "POSTING_DATE", "selectedValues": []}]},
            "advancedSearchFiltersSelectionParam": {"searchFilterSelections": [{"id": "LOCATION", "selectedValues": []}]},
            "pageNo": 1
        }
        
        jobs = []
        try:
            # We'll just do a single page for now to test validity
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                # Extremely simplified parsing, Taleo JSON structure is complex
                if "requisitionList" in data:
                    jobs = data["requisitionList"]
            else:
                self.health_score -= 10
                logger.warning(f"[Taleo] {self.company_name} returned {response.status_code}")
                
        except Exception as e:
            self.errors.append(str(e))
            self.health_score -= 20
            logger.debug(f"[Taleo] {self.company_name} fetch failed: {e}")

        self.jobs_collected = len(jobs)
        return jobs

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        """Parses the Taleo job node into our standard schema."""
        try:
            # Taleo's JSON fields can vary by implementation. We'll use common keys.
            title = raw_job.get("column", [])[0] if raw_job.get("column") else "Unknown Title"
            location = "India" # We will rely on our India filter later
            
            # Find location in columns if possible
            for col in raw_job.get("column", []):
                if isinstance(col, str) and ("India" in col or "IN" in col):
                    location = col
                    break
                    
            job_id = raw_job.get("contestNo", "")
            apply_url = f"https://{self.ats_identifier}.taleo.net/careersection/ex/jobdetail.ftl?job={job_id}"
            
            job_data = {
                "title": title,
                "company": self.company_name,
                "location": location,
                "job_type": "Job",
                "description": f"Role at {self.company_name} via Taleo.",
                "apply_url": apply_url,
                "source_url": f"https://{self.ats_identifier}.taleo.net",
                "ats_type": self.ats_type,
                "raw_data": raw_job
            }
            return self.normalize(job_data)
        except Exception as e:
            self.errors.append(f"Parse error: {e}")
            return {}
