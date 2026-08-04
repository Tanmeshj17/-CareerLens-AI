"""
Tech Mahindra Careers Collector — v2
Tech Mahindra uses iCIMS for their careers portal.
Falls back to curated fresher programs.
"""
import logging
import requests
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_techmahindra")

TECHMAHINDRA_PROGRAMS = [
    ("Tech Mahindra Smart Hire – Fresher Program", "Multiple Cities, India",
     "Tech Mahindra Smart Hire program for B.Tech/BE/MCA freshers. Roles: Software Engineer, Associate Software Engineer. 3-month training + project allocation.",
     "https://careers.techmahindra.com/"),
    ("Tech Mahindra Campus Connect", "PAN India",
     "Tech Mahindra campus placement program for engineering colleges. Eligible: B.Tech/BE (CS/IT/ECE) with 60%+ aggregate. CTC: 3.5-5 LPA.",
     "https://careers.techmahindra.com/campus"),
    ("Tech Mahindra Maker's Lab Internship", "Hyderabad, Bangalore, India",
     "Innovation internship at Tech Mahindra's Maker's Lab. Work on AI, IoT, AR/VR, and blockchain projects. For pre-final year engineering students.",
     "https://careers.techmahindra.com/internship"),
    ("Tech Mahindra Mahacademy Training Program", "India",
     "6-month intensive training program for fresh graduates. Training in Java, Python, DevOps, and Cloud technologies before project allocation.",
     "https://careers.techmahindra.com/"),
]


class TechMahindraCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Tech Mahindra Careers"

    def _fetch_icims(self) -> List[Dict[str, Any]]:
        """Tech Mahindra uses iCIMS — try their public API."""
        jobs = []
        try:
            # iCIMS public job feed for Tech Mahindra
            url = "https://careers.techmahindra.com/api/jobs?location=India&limit=20"
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                for job in (data.get("jobs") or data.get("results") or []):
                    title = job.get("title") or job.get("name", "")
                    location = job.get("location") or job.get("city", "India")
                    apply_url = job.get("url") or job.get("apply_url", "https://careers.techmahindra.com/")
                    jobs.append({
                        "title": title,
                        "company": "Tech Mahindra",
                        "location": location,
                        "job_type": "Full-time",
                        "description": f"{title} at Tech Mahindra in {location}.",
                        "apply_url": apply_url,
                        "source": self.source_name,
                        "source_url": apply_url,
                        "ats_type": "iCIMS",
                        "raw_data": {"source_type": "Tech Mahindra API"},
                    })
        except Exception as e:
            logger.debug(f"Tech Mahindra API fetch failed: {e}")
        return jobs

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting Tech Mahindra collection...")
        jobs = self._fetch_icims()

        for (title, location, description, apply_url) in TECHMAHINDRA_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "Tech Mahindra",
                "location": location,
                "job_type": "Full-time",
                "description": description,
                "apply_url": apply_url,
                "source": self.source_name,
                "source_url": apply_url,
                "raw_data": {"source_type": "Tech Mahindra Curated Programs"},
            })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"Tech Mahindra Collector: {len(jobs)} jobs.")
        return jobs
