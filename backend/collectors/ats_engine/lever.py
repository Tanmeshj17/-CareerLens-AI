import json
from typing import Dict, Any, List
from .base_ats import ATSParserBase

class LeverCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Lever"

    def fetch_jobs(self) -> Any:
        url = f"https://api.lever.co/v0/postings/{self.ats_identifier}?mode=json"
        response = self._make_request(url)
        if not response:
            return []
        return response.json()

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        categories = raw_job.get("categories", {})
        location = categories.get("location", "Remote")
        job_type = categories.get("commitment", "Full-time")
        
        return {
            "title": raw_job.get("text", "Unknown Role"),
            "company": self.company_name,
            "location": location,
            "job_type": job_type,
            "description": raw_job.get("descriptionPlain", "") or raw_job.get("description", ""),
            "apply_url": raw_job.get("applyUrl", raw_job.get("hostedUrl", "")),
            "source_url": f"https://jobs.lever.co/{self.ats_identifier}",
            "raw_data": json.dumps(raw_job)
        }
