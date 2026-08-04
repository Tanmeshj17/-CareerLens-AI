import json
from typing import Dict, Any, List
from .base_ats import ATSParserBase

class AshbyCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Ashby"

    def fetch_jobs(self) -> Any:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{self.ats_identifier}"
        response = self._make_request(url)
        if not response:
            return []
        data = response.json()
        return data.get("jobs", [])

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        location = raw_job.get("location", "Remote")
        job_type = raw_job.get("employmentType", "Full-time")
        
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": location,
            "job_type": job_type,
            "description": "", # Requires individual API call usually
            "apply_url": raw_job.get("jobUrl", f"https://jobs.ashbyhq.com/{self.ats_identifier}/{raw_job.get('id')}"),
            "source_url": f"https://jobs.ashbyhq.com/{self.ats_identifier}",
            "raw_data": json.dumps(raw_job)
        }
