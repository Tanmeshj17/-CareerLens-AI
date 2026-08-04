from .base_ats import ATSParserBase
from typing import List, Dict, Any
from datetime import datetime
import json

class SmartRecruitersCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "SmartRecruiters"

    def collect(self) -> List[Dict[str, Any]]:
        url = f"https://api.smartrecruiters.com/v1/companies/{self.ats_identifier}/postings"
        response = self._make_request(url)
        if not response:
            return []

        data = response.json()
        jobs = data.get("content", [])
        
        results = []
        for job in jobs:
            try:
                location_dict = job.get("location", {})
                location = f"{location_dict.get('city', '')}, {location_dict.get('region', '')}".strip(', ')
                if not location:
                    location = "Remote"
                    
                job_type = job.get("typeOfEmployment", {}).get("label", "Full-time")
                
                # Note: SR API /postings doesn't give full description by default without hitting /postings/{id}.
                # For scalability we store what we have.
                results.append({
                    "title": job.get("name", "Unknown Role"),
                    "company": self.company_name,
                    "location": location,
                    "job_type": job_type,
                    "description": "",  # Require detailed fetch if needed
                    "apply_url": f"https://jobs.smartrecruiters.com/{self.ats_identifier}/{job.get('id')}",
                    "source": "Company Career Page",
                    "ats_type": self.ats_type,
                    "source_url": f"https://careers.smartrecruiters.com/{self.ats_identifier}",
                    "raw_data": json.dumps(job)
                })
            except Exception as e:
                continue

        return results
