"""
Apprenticeship India + NCS (National Career Service) Collector
Apprenticeship India: https://www.apprenticeshipindia.gov.in/
NCS Portal: https://www.ncs.gov.in/
Both are government portals for apprenticeship and internship opportunities.
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_apprenticeship")

APPRENTICESHIP_PROGRAMS = [
    # Apprenticeship India Programs
    ("Apprenticeship India - Engineering Graduate", "India", "Full-time", "Apprenticeship",
     "National Apprenticeship Training Scheme (NATS) for engineering graduates. Stipend-based 1-year apprenticeship with government-recognized industries across India.",
     "https://www.apprenticeshipindia.gov.in/"),
    ("Apprenticeship India - ITI Trades", "India", "Full-time", "Apprenticeship",
     "Trade apprenticeship under the Apprentices Act. Practical training in ITI trades with stipend. Available at manufacturing, service, and PSU establishments.",
     "https://www.apprenticeshipindia.gov.in/"),
    ("NATS - Diploma Apprenticeship", "India", "Full-time", "Apprenticeship",
     "National Apprenticeship Training Scheme for diploma holders. 1-year practical training with monthly stipend as per Apprentices Act.",
     "https://nats.education.gov.in/"),
    ("NATS - Graduate Apprenticeship (B.Tech/BE)", "Multiple Cities, India", "Full-time", "Apprenticeship",
     "NATS apprenticeship for B.Tech/BE graduates. 1-year program with leading PSUs and private companies. Monthly stipend provided.",
     "https://nats.education.gov.in/"),
    ("NAPS - National Apprenticeship Promotion Scheme", "India", "Full-time", "Apprenticeship",
     "Government-supported apprenticeship with 25% stipend reimbursement to employers. Available across all sectors.",
     "https://www.apprenticeshipindia.gov.in/national-apprenticeship-promotion-scheme"),
    # Sector-specific apprenticeships
    ("BHEL Apprenticeship (Boiler Plant)", "Bhopal, Hyderabad, Haridwar, India", "Full-time", "Apprenticeship",
     "BHEL Trade Apprenticeship under the Apprentices Act. Open to ITI holders in electrical, mechanical, instrumentation trades.",
     "https://careers.bhel.in/bhel/apprenticeship"),
    ("BEL Apprenticeship (Defense Electronics)", "Bangalore, India", "Full-time", "Apprenticeship",
     "Bharat Electronics Limited Apprenticeship Program. Engineering and diploma apprentices in electronics, IT, and related fields.",
     "https://www.bel-india.in/careers/apprenticeship"),
    ("IOCL Apprenticeship (Oil & Gas)", "Multiple States, India", "Full-time", "Apprenticeship",
     "Indian Oil Corporation apprenticeship for ITI/Diploma holders. Trade apprenticeship across refineries and marketing divisions.",
     "https://iocl.com/apprenticeship"),
    ("ONGC Graduate Trainee Apprenticeship", "Multiple Cities, India", "Full-time", "Apprenticeship",
     "ONGC apprenticeship for engineering and science graduates. Practical exposure in oil & gas exploration.",
     "https://www.ongcindia.com/"),
    # NCS Portal listings
    ("NCS Portal - IT Apprenticeship", "India", "Full-time", "Apprenticeship",
     "IT sector apprenticeships listed on National Career Service portal. Companies include TCS, Infosys, Wipro, and others.",
     "https://www.ncs.gov.in/"),
    ("NCS Portal - Retail Apprenticeship", "India", "Full-time", "Apprenticeship",
     "Retail sector apprenticeships via NCS portal. Positions at Future Group, Reliance Retail, DMart, and other retail chains.",
     "https://www.ncs.gov.in/"),
    ("NCS Portal - Banking Apprenticeship", "India", "Full-time", "Apprenticeship",
     "Banking sector apprenticeships via National Career Service. Positions at public sector banks including SBI, PNB, BOB.",
     "https://www.ncs.gov.in/"),
    ("NCS Portal - Healthcare Apprenticeship", "India", "Full-time", "Apprenticeship",
     "Healthcare sector apprenticeships via NCS. Para-medical and administrative positions at hospitals and clinics.",
     "https://www.ncs.gov.in/"),
    ("NCS Portal - Manufacturing Apprenticeship", "India", "Full-time", "Apprenticeship",
     "Manufacturing sector apprenticeships listed on NCS portal. Auto, FMCG, and industrial manufacturing companies.",
     "https://www.ncs.gov.in/"),
]


class ApprenticeshipCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Apprenticeship India / NCS Portal"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting Apprenticeship India / NCS collection...")
        jobs = []

        # Try to fetch live data from Apprenticeship India
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get("https://www.apprenticeshipindia.gov.in/establishment-search", headers=headers, timeout=12)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                cards = soup.find_all("div", class_=lambda c: c and any(kw in c for kw in ["card", "listing", "result"]))
                for card in cards[:20]:
                    text = card.get_text(strip=True)
                    if len(text) > 20:
                        link = card.find("a", href=True)
                        url = link["href"] if link else "https://www.apprenticeshipindia.gov.in/"
                        if url.startswith("/"):
                            url = "https://www.apprenticeshipindia.gov.in" + url
                        # Extract title
                        title_elem = card.find(["h3", "h4", "strong"])
                        title = title_elem.get_text(strip=True) if title_elem else "Apprenticeship Opportunity"
                        if len(title) > 10:
                            jobs.append({
                                "title": title,
                                "company": "Apprenticeship India",
                                "location": "India",
                                "job_type": "Full-time",
                                "opportunity_category": "Apprenticeship",
                                "description": f"{title} - Government apprenticeship opportunity. Registered under the Apprentices Act.",
                                "apply_url": url,
                                "source": self.source_name,
                                "source_url": "https://www.apprenticeshipindia.gov.in/",
                                "raw_data": {"source_type": "Apprenticeship India HTML"},
                            })
        except Exception as e:
            logger.warning(f"Apprenticeship India live fetch failed: {e}")

        # Always add the curated known programs
        for (title, location, job_type, category, description, apply_url) in APPRENTICESHIP_PROGRAMS:
            jobs.append({
                "title": title,
                "company": "Government of India" if "NATS" in title or "NAPS" in title else title.split(" ")[0],
                "location": location,
                "job_type": job_type,
                "opportunity_category": category,
                "description": description,
                "apply_url": apply_url,
                "source": self.source_name,
                "source_url": apply_url,
                "raw_data": {"source_type": "Curated Government Programs"},
            })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"Apprenticeship Collector: {len(jobs)} opportunities collected.")
        return jobs
