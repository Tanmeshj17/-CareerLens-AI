"""
Cognizant Careers Collector — v2
Uses SmartRecruiters API for Cognizant India jobs + curated fresher programs.
"""
import logging
import requests
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_cognizant")

COGNIZANT_FRESHER_PROGRAMS = [
    ("Cognizant GenC – Graduate Program", "Multiple Cities, India",
     "Cognizant GenC (Generation Cognizant) is a campus hiring program for fresh graduates. Roles: Programmer Analyst Trainee, Process Executive. Eligible: B.E/B.Tech/M.E/M.Tech/MCA/M.Sc.",
     "https://careers.cognizant.com/global/en/fresh-graduates"),
    ("Cognizant GenC Next – Digital Engineering", "Bangalore, Hyderabad, Pune, India",
     "Cognizant GenC Next is a specialized program for top engineering graduates passionate about digital engineering, cloud, and AI/ML.",
     "https://careers.cognizant.com/global/en/fresh-graduates"),
    ("Cognizant GenC Elevate – Premium Graduate Hire", "India",
     "Cognizant GenC Elevate is a premium campus hiring track for graduates from top-tier institutions. Higher compensation and accelerated career path.",
     "https://careers.cognizant.com/global/en/fresh-graduates"),
    ("Cognizant Programmer Analyst Trainee", "Chennai, Pune, Bangalore, India",
     "Entry-level Programmer Analyst Trainee role at Cognizant for B.Tech/BE graduates. 18-month training program.",
     "https://careers.cognizant.com/"),
]


class CognizantCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Cognizant Careers"

    def _fetch_smartrecruiters(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = "https://api.smartrecruiters.com/v1/companies/Cognizant/postings?country=IN&limit=20"
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                for posting in data.get("content", []):
                    title = posting.get("name", "")
                    location = posting.get("location", {})
                    city = location.get("city", "")
                    country = location.get("country", "")
                    loc_str = f"{city}, India" if city else "India"
                    apply_url = f"https://jobs.smartrecruiters.com/Cognizant/{posting.get('id', '')}"
                    jobs.append({
                        "title": title,
                        "company": "Cognizant",
                        "location": loc_str,
                        "job_type": "Full-time",
                        "description": f"{title} at Cognizant in {loc_str}.",
                        "apply_url": apply_url,
                        "source": self.source_name,
                        "source_url": apply_url,
                        "ats_type": "SmartRecruiters",
                        "raw_data": {"source_type": "SmartRecruiters API"},
                    })
        except Exception as e:
            logger.debug(f"Cognizant SmartRecruiters fetch failed: {e}")
        return jobs

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting Cognizant collection...")
        jobs = self._fetch_smartrecruiters()

        for (title, location, description, apply_url) in COGNIZANT_FRESHER_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "Cognizant",
                "location": location,
                "job_type": "Full-time",
                "description": description,
                "apply_url": apply_url,
                "source": self.source_name,
                "source_url": apply_url,
                "raw_data": {"source_type": "Cognizant Curated Programs"},
            })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"Cognizant Collector: {len(jobs)} jobs.")
        return jobs
