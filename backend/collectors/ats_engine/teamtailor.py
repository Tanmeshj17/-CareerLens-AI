import json
from typing import Dict, Any
from .base_ats import ATSParserBase

class TeamtailorCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Teamtailor"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.ats_identifier}.teamtailor.com/jobs.json"
        response = self._make_request(url)
        if not response:
            return []
        
        try:
            return response.json().get("jobs", [])
        except ValueError:
            return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": raw_job.get("location", {}).get("name", "Remote"),
            "job_type": raw_job.get("job_type", "Full-time"),
            "description": raw_job.get("body", ""),
            "apply_url": raw_job.get("url", ""),
            "source_url": f"https://{self.ats_identifier}.teamtailor.com",
            "raw_data": json.dumps(raw_job)
        }
