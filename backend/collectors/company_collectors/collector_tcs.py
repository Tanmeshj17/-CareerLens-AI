import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_tcs")

TCS_PROGRAMS = [
    ("TCS NQT (National Qualifier Test)", "Multiple Cities, India",
     "TCS NQT is the primary entry point for freshers across India to get hired at TCS as a Ninja or Digital profile.",
     "https://www.tcs.com/careers/india"),
    ("TCS Ninja Fresher Hiring", "PAN India",
     "Entry-level software engineer roles for B.Tech/BE/MCA/M.Sc graduates. CTC: 3.36 LPA.",
     "https://www.tcs.com/careers/india"),
    ("TCS Digital Fresher Hiring", "PAN India",
     "Advanced engineering roles for top performers in NQT. Focus on AI, IoT, Cloud, and Data. CTC: 7.0 LPA.",
     "https://www.tcs.com/careers/india"),
    ("TCS Prime Fresher Hiring", "PAN India",
     "Premium hiring track for software development and complex engineering roles. CTC: 9.0 LPA.",
     "https://www.tcs.com/careers/india"),
    ("TCS Smart Hiring", "India",
     "TCS Smart Hiring for BCA, B.Sc (Maths, Statistics, Physics, Chemistry, Electronics, Biochemistry, Computer Science, IT).",
     "https://www.tcs.com/careers/india"),
]

class TCSCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"
        
    @property
    def source_name(self) -> str:
        return "TCS Careers"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting collection for TCS Careers (Curated Programs)...")
        jobs = []
        
        for title, location, desc, url in TCS_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "Tata Consultancy Services (TCS)",
                "location": location,
                "job_type": "Full-time",
                "description": desc,
                "apply_url": url,
                "source": self.source_name,
                "source_url": url,
                "raw_data": {"source_type": "Curated India Programs"},
            })
            
        return jobs
