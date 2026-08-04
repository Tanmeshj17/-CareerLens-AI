import json
import xml.etree.ElementTree as ET
from typing import Dict, Any
from .base_ats import ATSParserBase

class BambooHRCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "BambooHR"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.ats_identifier}.bamboohr.com/jobs/embed2.php"
        response = self._make_request(url)
        if not response:
            return []
        
        # BambooHR embed is often HTML or JSON depending on the endpoint.
        # Another common endpoint is https://{ats_identifier}.bamboohr.com/careers/list
        url_json = f"https://{self.ats_identifier}.bamboohr.com/careers/list"
        resp2 = self._make_request(url_json)
        if resp2:
            try:
                return resp2.json().get("result", [])
            except ValueError:
                pass
        return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("jobOpeningName", "Unknown Role"),
            "company": self.company_name,
            "location": raw_job.get("location", {}).get("city", "Remote"),
            "job_type": raw_job.get("employmentStatus", "Full-time"),
            "description": raw_job.get("description", ""),
            "apply_url": f"https://{self.ats_identifier}.bamboohr.com/careers/{raw_job.get('id')}",
            "source_url": f"https://{self.ats_identifier}.bamboohr.com/careers",
            "raw_data": json.dumps(raw_job)
        }
