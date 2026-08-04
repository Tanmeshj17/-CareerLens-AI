import json
from typing import Dict, Any
from .base_ats import ATSParserBase

class RipplingCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Rippling"

    def fetch_jobs(self) -> Any:
        # Rippling ATS public API endpoint
        url = f"https://api.rippling.com/ats/api/v1/board/{self.ats_identifier}/jobs"
        response = self._make_request(url)
        if not response:
            return []
        
        try:
            return response.json().get("jobs", [])
        except ValueError:
            return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("name", "Unknown Role"),
            "company": self.company_name,
            "location": raw_job.get("location", "Remote"),
            "job_type": raw_job.get("type", "Full-time"),
            "description": raw_job.get("description", ""),
            "apply_url": raw_job.get("url", ""),
            "source_url": f"https://app.rippling.com/ats/board/{self.ats_identifier}",
            "raw_data": json.dumps(raw_job)
        }
