"""
DRDO & ISRO Government Research Internship Collector
DRDO: Defence Research and Development Organisation
ISRO: Indian Space Research Organisation
Both offer highly competitive internship programs for engineering/science students.
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_govt_research")

# DRDO Curated Internship Programs
DRDO_PROGRAMS = [
    ("DRDO Summer Internship Program (Engineering)", "Delhi, Bangalore, Pune, Hyderabad, India",
     "Engineering students (B.Tech/M.Tech) summer internship at DRDO labs. Work on defense technology projects. Duration: 2 months."),
    ("DRDO Research Internship - Electronics & Radar", "Bangalore, India",
     "Internship at DRDO LRDE (Electronics & Radar Development Establishment). For Electronics/ECE students."),
    ("DRDO Internship - Aeronautics (NAL)", "Bangalore, India",
     "Internship at National Aerospace Laboratories (DRDO). Aeronautical engineering projects. Duration: 1-3 months."),
    ("DRDO Internship - Computer Science (CAIR)", "Bangalore, India",
     "Internship at Centre for Artificial Intelligence & Robotics (DRDO CAIR). AI, ML, and robotics research."),
    ("DRDO Internship - Chemical & Materials", "Pune, India",
     "Internship at DRDO HEMRL. Chemical engineering, energetic materials, and defense applications."),
    ("DRDO Project Internship - Signal Processing", "Delhi, India",
     "DRDO MTRDC internship in signal processing, antenna design, and microwave technology."),
    ("DRDO Internship - Naval Systems (NAVAL)", "Visakhapatnam, India",
     "Naval Science & Technological Laboratory (NSTL) internship. Underwater systems and marine technology."),
    ("DRDO Internship - Missile Technology (DRDL)", "Hyderabad, India",
     "Defence Research & Development Laboratory internship. Missile systems and aerospace propulsion."),
]

# ISRO Curated Internship Programs
ISRO_PROGRAMS = [
    ("ISRO Summer Internship Program (VSSC)", "Thiruvananthapuram, India",
     "ISRO Vikram Sarabhai Space Centre summer internship. Rocket propulsion, avionics, and space technology. For B.Tech/M.Tech students."),
    ("ISRO Internship - Satellite Technology (ISAC)", "Bangalore, India",
     "ISRO Satellite Centre (URSC) internship. Satellite systems, payload, and spacecraft systems engineering."),
    ("ISRO Internship - Space Applications (SAC)", "Ahmedabad, India",
     "Space Applications Centre internship. Remote sensing, GIS, and earth observation applications."),
    ("ISRO Internship - Ground Systems (MCF)", "Hassan, India",
     "Master Control Facility internship. Satellite control, tracking, and ground systems operations."),
    ("ISRO Internship - Propulsion (LPSC)", "Thiruvananthapuram, India",
     "Liquid Propulsion Systems Centre internship. Liquid propulsion, cryogenic engines for space launch vehicles."),
    ("ISRO Research Internship - Data Science & AI", "Bangalore, India",
     "ISRO internship in data science, machine learning for earth observation data analysis."),
    ("ISRO Internship - Electronics (LEOS)", "Bangalore, India",
     "Laboratory for Electro-Optics Systems internship. Electro-optic sensors and payloads for space missions."),
    ("ISRO Young Scientist Programme (YUVIKA)", "India",
     "ISRO YUVIKA program for school students to learn about space science. Special internship for Class 9 students."),
    ("ISRO Internship - Communications (ISTRAC)", "Bangalore, India",
     "ISRO Telemetry, Tracking and Command Network internship. Deep space communications and tracking systems."),
]


class GovtResearchInternshipCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "DRDO / ISRO Internship Programs"

    def _try_scrape_drdo(self) -> List[Dict[str, Any]]:
        """Attempt live scrape of DRDO internship page."""
        jobs = []
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get("https://www.drdo.gov.in/internship-programme", headers=headers, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                cards = soup.find_all(["div", "li"], class_=lambda c: c and any(kw in c.lower() for kw in ["intern", "program", "oppor"]))
                for card in cards[:15]:
                    title_elem = card.find(["h3", "h4", "strong", "a"])
                    if title_elem and len(title_elem.get_text(strip=True)) > 10:
                        title = title_elem.get_text(strip=True)
                        link = card.find("a", href=True)
                        url = link["href"] if link else "https://www.drdo.gov.in/internship-programme"
                        jobs.append({
                            "title": title,
                            "company": "DRDO",
                            "location": "India",
                            "job_type": "Internship",
                            "opportunity_category": "Internship",
                            "description": f"DRDO Internship: {title}. Apply through official DRDO internship portal.",
                            "apply_url": url if url.startswith("http") else f"https://www.drdo.gov.in{url}",
                            "source": self.source_name,
                            "source_url": "https://www.drdo.gov.in/internship-programme",
                            "raw_data": {"source_type": "DRDO Portal HTML"},
                        })
        except Exception as e:
            logger.warning(f"DRDO live scrape failed: {e}")
        return jobs

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        logger.info("Starting DRDO + ISRO internship collection...")
        jobs = []

        # Try live scrape first
        live_drdo = self._try_scrape_drdo()
        jobs.extend(live_drdo)

        # Always add curated DRDO programs
        for (title, location, description) in DRDO_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "DRDO",
                "location": location,
                "job_type": "Internship",
                "opportunity_category": "Internship",
                "description": description,
                "apply_url": "https://www.drdo.gov.in/internship-programme",
                "source": self.source_name,
                "source_url": "https://www.drdo.gov.in/internship-programme",
                "raw_data": {"source_type": "DRDO Curated Programs"},
            })

        # Add curated ISRO programs
        for (title, location, description) in ISRO_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "ISRO",
                "location": location,
                "job_type": "Internship",
                "opportunity_category": "Internship",
                "description": description,
                "apply_url": "https://www.isro.gov.in/Internship.html",
                "source": self.source_name,
                "source_url": "https://www.isro.gov.in/Internship.html",
                "raw_data": {"source_type": "ISRO Curated Programs"},
            })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"Govt Research Internship Collector: {len(jobs)} opportunities.")
        return jobs
