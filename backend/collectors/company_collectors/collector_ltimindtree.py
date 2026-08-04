"""
LTIMindtree Careers Collector — v2
LTIMindtree uses their own careers portal + curated fresher programs.
"""
import logging
import requests
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_ltimindtree")

LTIMINDTREE_PROGRAMS = [
    ("LTIMindtree Infinity Program – Fresher Hiring", "Mumbai, Bangalore, Chennai, India",
     "LTIMindtree Infinity is the flagship campus hire program. Roles: Graduate Engineer Trainee (GET). Eligible: B.Tech/BE/MCA with 60%+ from recognized universities.",
     "https://www.ltimindtree.com/careers/campus-placements/"),
    ("LTIMindtree Campus Ambassador Program", "India (Remote)",
     "LTIMindtree Campus Ambassador program for final-year students. Represent LTIMindtree at your campus and earn referral incentives.",
     "https://www.ltimindtree.com/careers/campus-placements/"),
    ("LTIMindtree Tech Scholar Program", "Multiple Cities, India",
     "LTIMindtree Tech Scholar is an exclusive hiring track for students from premier institutions (NITs, IIITs, BITS). Higher CTC and early career acceleration.",
     "https://www.ltimindtree.com/careers/campus-placements/"),
    ("LTIMindtree – Graduate Engineer Trainee (GET)", "Pune, Mumbai, Bangalore, Hyderabad, India",
     "Entry-level GET roles at LTIMindtree. Training in SAP, Salesforce, Java, Python, and data engineering. 6-month training period.",
     "https://www.ltimindtree.com/careers/"),
    ("LTIMindtree Mosaic Internship Program", "Mumbai, Pune, India",
     "LTIMindtree Mosaic summer internship for penultimate-year engineering students. 8-10 week program with real project exposure.",
     "https://www.ltimindtree.com/careers/internships/"),
]


class LTIMindtreeCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "LTIMindtree Careers"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting LTIMindtree collection...")
        jobs = []

        for (title, location, description, apply_url) in LTIMINDTREE_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "LTIMindtree",
                "location": location,
                "job_type": "Full-time",
                "description": description,
                "apply_url": apply_url,
                "source": self.source_name,
                "source_url": apply_url,
                "raw_data": {"source_type": "LTIMindtree Curated Programs"},
            })

        self.health_status = "Healthy"
        logger.info(f"LTIMindtree Collector: {len(jobs)} jobs.")
        return jobs
