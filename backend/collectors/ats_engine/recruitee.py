import json
from typing import Dict, Any
from .base_ats import ATSParserBase

class RecruiteeCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Recruitee"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.ats_identifier}.recruitee.com/api/offers"
        response = self._make_request(url)
        if not response:
            return []
        
        try:
            return response.json().get("offers", [])
        except ValueError:
            return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": raw_job.get("location", "Remote"),
            "job_type": raw_job.get("employment_type", "Full-time"),
            "description": raw_job.get("description", ""),
            "apply_url": raw_job.get("careers_url", ""),
            "source_url": f"https://{self.ats_identifier}.recruitee.com",
            "raw_data": json.dumps(raw_job)
        }
