import json
from typing import Dict, Any, List
from .base_ats import ATSParserBase

class GreenhouseCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Greenhouse"

    def fetch_jobs(self) -> Any:
        url = f"https://boards-api.greenhouse.io/v1/boards/{self.ats_identifier}/jobs?content=true"
        response = self._make_request(url)
        if not response:
            return []
        data = response.json()
        return data.get("jobs", [])

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        location = raw_job.get("location", {}).get("name", "Remote")
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": location,
            "job_type": "Full-time",  # Greenhouse API often lacks standard job_type field without deeper parsing
            "description": raw_job.get("content", ""),
            "apply_url": raw_job.get("absolute_url", ""),
            "source_url": f"https://boards.greenhouse.io/{self.ats_identifier}",
            "raw_data": json.dumps(raw_job)
        }
