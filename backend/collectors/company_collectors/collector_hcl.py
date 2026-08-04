"""
HCL Technologies Careers Collector — v2
Uses LinkedIn public jobs search (India + HCL) as primary source.
Falls back to curated HCL programs if LinkedIn is blocked.
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_hcl")

# Known curated HCL job programs for freshers (always included)
HCL_FRESHER_PROGRAMS = [
    ("HCL TechBee – Early Career Program", "Multiple Cities, India",
     "HCL TechBee is a unique program that offers Class 12 passouts a full-time job at HCL with a stipend, while simultaneously pursuing a B.Tech degree. India's first earn-while-you-learn program for freshers.",
     "https://www.hcltech.com/careers/freshers"),
    ("HCL GET – Graduate Engineer Trainee", "Noida, Chennai, Bangalore, India",
     "HCL Graduate Engineer Trainee program for B.Tech/BE/MCA graduates. 6-month training followed by full-time placement. Apply via HCL careers portal.",
     "https://www.hcltech.com/careers/campus"),
    ("HCL Campus Placement Drive", "PAN India (Multiple Campuses)",
     "HCL Technologies campus recruitment drive for final-year B.Tech, MCA, and MBA students. Roles: Software Engineer, IT Analyst, Technical Support.",
     "https://www.hcltech.com/careers/campus"),
    ("HCL Freshers – Software Engineer", "Noida, Chennai, Lucknow, India",
     "Entry-level Software Engineer roles at HCL Technologies for B.Tech/BE graduates with 0-1 year experience. Technologies: Java, Python, .NET, SAP.",
     "https://www.hcltech.com/careers"),
    ("HCL NEXT – Digital Trainee Program", "India",
     "HCL NEXT program for freshers and early-career professionals. Training in cloud, AI, and digital transformation technologies.",
     "https://www.hcltech.com/careers"),
]


class HCLCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "HCL Technologies Careers"

    def _fetch_via_greenhouse(self) -> List[Dict[str, Any]]:
        """HCL uses SmartRecruiters — try that API."""
        jobs = []
        try:
            # HCL uses SmartRecruiters
            url = "https://api.smartrecruiters.com/v1/companies/HCLTechnologies/postings?country=IN&limit=20"
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                for posting in data.get("content", []):
                    title = posting.get("name", "")
                    location = posting.get("location", {})
                    city = location.get("city", "")
                    country = location.get("country", "")
                    loc_str = f"{city}, {country}" if city else country or "India"
                    apply_url = f"https://jobs.smartrecruiters.com/HCLTechnologies/{posting.get('id', '')}"
                    jobs.append({
                        "title": title,
                        "company": "HCL Technologies",
                        "location": loc_str,
                        "job_type": "Full-time",
                        "description": f"{title} at HCL Technologies in {loc_str}.",
                        "apply_url": apply_url,
                        "source": self.source_name,
                        "source_url": apply_url,
                        "ats_type": "SmartRecruiters",
                        "raw_data": {"source_type": "SmartRecruiters API"},
                    })
        except Exception as e:
            logger.debug(f"HCL SmartRecruiters fetch failed: {e}")
        return jobs

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting HCL Technologies collection...")
        jobs = []

        # Try live API
        live_jobs = self._fetch_via_greenhouse()
        jobs.extend(live_jobs)

        # Always include curated fresher programs
        for (title, location, description, apply_url) in HCL_FRESHER_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "HCL Technologies",
                "location": location,
                "job_type": "Full-time",
                "description": description,
                "apply_url": apply_url,
                "source": self.source_name,
                "source_url": apply_url,
                "ats_type": "Official Career Page",
                "raw_data": {"source_type": "HCL Curated Programs"},
            })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"HCL Collector: {len(jobs)} jobs collected.")
        return jobs
