"""
Capgemini Careers Collector — v2
Uses SmartRecruiters API (Capgemini's actual ATS) + curated fresher programs.
Note: Capgemini does NOT use Greenhouse — they use SmartRecruiters.
"""
import logging
import requests
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_capgemini")

CAPGEMINI_PROGRAMS = [
    ("Capgemini GCAP – Graduate Campus Hiring", "Multiple Cities, India",
     "Capgemini's flagship campus hiring program. Roles: Analyst, Senior Analyst. Open to B.E/B.Tech/M.Tech/MCA graduates. CTC: 3.8-7.5 LPA based on test performance.",
     "https://www.capgemini.com/in-en/careers/students-graduates/"),
    ("Capgemini Fresher Hiring – B.Tech 2024", "Bangalore, Chennai, Pune, Hyderabad, India",
     "Capgemini fresher hiring for B.Tech/BE 2024 batch graduates. Roles in Java, Python, SAP, Testing, and Cloud technologies.",
     "https://www.capgemini.com/in-en/careers/"),
    ("Capgemini Perform Program", "India",
     "Capgemini Perform is a structured career development program for campus hires. 12-week technical training followed by project placement.",
     "https://www.capgemini.com/in-en/careers/students-graduates/"),
    ("Capgemini Business Analyst Fresher", "Mumbai, Pune, Bangalore, India",
     "Capgemini fresher business analyst roles for MBA graduates and high-performing engineering graduates.",
     "https://www.capgemini.com/in-en/careers/"),
]


class CapgeminiCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Capgemini Careers"

    def _fetch_smartrecruiters(self) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # Try Capgemini's SmartRecruiters company ID
            for company_id in ["CapgeminiGroup", "Capgemini"]:
                url = f"https://api.smartrecruiters.com/v1/companies/{company_id}/postings?country=IN&limit=20"
                headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
                resp = requests.get(url, headers=headers, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    for posting in data.get("content", []):
                        title = posting.get("name", "")
                        location = posting.get("location", {})
                        city = location.get("city", "")
                        loc_str = f"{city}, India" if city else "India"
                        apply_url = f"https://jobs.smartrecruiters.com/{company_id}/{posting.get('id', '')}"
                        jobs.append({
                            "title": title,
                            "company": "Capgemini",
                            "location": loc_str,
                            "job_type": "Full-time",
                            "description": f"{title} at Capgemini in {loc_str}.",
                            "apply_url": apply_url,
                            "source": self.source_name,
                            "source_url": apply_url,
                            "ats_type": "SmartRecruiters",
                            "raw_data": {"source_type": "SmartRecruiters API"},
                        })
                    if jobs:
                        break
        except Exception as e:
            logger.debug(f"Capgemini SmartRecruiters fetch failed: {e}")
        return jobs

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting Capgemini collection...")
        jobs = self._fetch_smartrecruiters()

        for (title, location, description, apply_url) in CAPGEMINI_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "Capgemini",
                "location": location,
                "job_type": "Full-time",
                "description": description,
                "apply_url": apply_url,
                "source": self.source_name,
                "source_url": apply_url,
                "raw_data": {"source_type": "Capgemini Curated Programs"},
            })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"Capgemini Collector: {len(jobs)} jobs.")
        return jobs
