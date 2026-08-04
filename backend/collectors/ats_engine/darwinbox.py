import json
import logging
from typing import Dict, Any, List
from .base_ats import ATSParserBase

logger = logging.getLogger(__name__)

class DarwinboxCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Darwinbox"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.ats_identifier}.darwinbox.in/ms/candidaterecruitment/api/getjobs"
        payload = {"limit": 100, "offset": 0}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = self._make_request(url, headers=headers)
        if not response:
            return []
            
        try:
            data = response.json()
            if isinstance(data, dict) and "data" in data and "jobs" in data["data"]:
                return data["data"]["jobs"]
            return []
        except ValueError:
            return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        job_id = raw_job.get("id", "")
        url_title = str(raw_job.get("title", "")).lower().replace(" ", "-")
        apply_url = f"https://{self.ats_identifier}.darwinbox.in/jobs/d/{job_id}/{url_title}"
        
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": raw_job.get("location", "Remote"),
            "job_type": raw_job.get("employment_type", "Full-time"),
            "description": raw_job.get("description", ""),
            "apply_url": apply_url,
            "source_url": f"https://{self.ats_identifier}.darwinbox.in/",
            "raw_data": json.dumps(raw_job)
        }
