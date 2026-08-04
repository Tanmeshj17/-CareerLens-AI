import json
from typing import Dict, Any, List
from .base_ats import ATSParserBase

class OracleCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Oracle Recruiting"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.ats_identifier}.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=all&limit=200"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        response = self._make_request(url, headers=headers)
        if not response:
            return []
        
        try:
            return response.json().get("items", [])
        except ValueError:
            return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("Title", "Unknown Role"),
            "company": self.company_name,
            "location": raw_job.get("PrimaryLocation", "Remote"),
            "job_type": raw_job.get("JobFamily", "Full-time"),
            "description": raw_job.get("ShortDescription", ""),
            "apply_url": raw_job.get("ExternalApplyUrl", ""),
            "source_url": f"https://{self.ats_identifier}.fa.em2.oraclecloud.com",
            "raw_data": json.dumps(raw_job)
        }
