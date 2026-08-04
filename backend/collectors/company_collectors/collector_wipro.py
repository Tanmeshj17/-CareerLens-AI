import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_wipro")

WIPRO_PROGRAMS = [
    ("Wipro Elite National Talent Hunt (NTH)", "Multiple Cities, India",
     "Elite NTH is a fresher hiring program by Wipro to attract the best engineering talent in India. Roles: Project Engineer. CTC: 3.5 LPA.",
     "https://careers.wipro.com/careers-home/"),
    ("Wipro Turbo Hiring Program", "PAN India",
     "Wipro Turbo is for top performers who clear advanced coding assessments. Higher CTC and fast-tracked career growth. CTC: 6.5 LPA.",
     "https://careers.wipro.com/careers-home/"),
    ("Wipro Work Integrated Learning Program (WILP)", "India",
     "A unique earn-while-you-learn program for BCA and B.Sc graduates. Wipro sponsors your M.Tech degree at BITS Pilani while you work.",
     "https://careers.wipro.com/wilp"),
    ("Wipro Step Up Program", "India",
     "Early career program for diploma holders in CS, IT, Electronics, Telecommunication, and Computer Engineering.",
     "https://careers.wipro.com/careers-home/"),
]

class WiproCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"
        
    @property
    def source_name(self) -> str:
        return "Wipro Careers"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting collection for Wipro Careers (Curated Programs)...")
        jobs = []
        
        for title, location, desc, url in WIPRO_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "Wipro",
                "location": location,
                "job_type": "Full-time",
                "description": desc,
                "apply_url": url,
                "source": self.source_name,
                "source_url": url,
                "raw_data": {"source_type": "Curated India Programs"},
            })
            
        return jobs
