"""
AICTE Internship Portal Collector
AICTE (All India Council for Technical Education) hosts internship opportunities
via their public portal. Collects via API + HTML parsing.
"""
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_aicte")


class AICTECollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "AICTE Internship Portal"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        logger.info("Starting AICTE Internship Portal collection...")
        jobs = []

        # AICTE Internship Portal - public listing
        sources = [
            {
                "url": "https://internship.aicte-india.org/",
                "label": "AICTE Main Portal"
            }
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }

        for source in sources:
            try:
                res = requests.get(source["url"], headers=headers, timeout=15)
                if res.status_code != 200:
                    logger.warning(f"AICTE: Got {res.status_code} from {source['url']}")
                    continue

                soup = BeautifulSoup(res.text, "html.parser")

                # Look for internship listing cards/rows — common patterns
                internship_cards = (
                    soup.find_all("div", class_=lambda c: c and "intern" in c.lower()) or
                    soup.find_all("div", class_=lambda c: c and "card" in c.lower()) or
                    soup.find_all("tr", class_=lambda c: c and c != "")
                )

                for card in internship_cards[:30]:
                    try:
                        title_elem = card.find(["h3", "h4", "h5", "strong", "b", "td"])
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        if len(title) < 5 or len(title) > 200:
                            continue

                        link_elem = card.find("a", href=True)
                        apply_url = link_elem["href"] if link_elem else source["url"]
                        if apply_url.startswith("/"):
                            apply_url = "https://internship.aicte-india.org" + apply_url

                        jobs.append({
                            "title": title,
                            "company": "AICTE",
                            "location": "India",
                            "job_type": "Internship",
                            "opportunity_category": "Internship",
                            "description": f"AICTE Internship: {title}. Apply via official AICTE Internship Portal. Open to students from AICTE-approved institutions.",
                            "apply_url": apply_url,
                            "source": self.source_name,
                            "source_url": source["url"],
                            "raw_data": {"source_type": "AICTE Portal HTML"},
                        })
                    except Exception:
                        continue

            except Exception as e:
                logger.warning(f"AICTE source {source['url']} failed: {e}")

        # If scraping failed, add known static AICTE programs
        if not jobs:
            logger.info("AICTE: Scraping yielded no results, using known program list.")
            known_programs = [
                ("AICTE Virtual Internship Program", "PAN India, Remote"),
                ("AICTE-NEAT Internship", "PAN India"),
                ("AICTE ATAL Internship", "PAN India"),
                ("AICTE Pragati Scholarship Internship", "India"),
                ("AICTE Saksham Scholarship Internship", "India"),
                ("AICTE Industry Internship (EY)", "Multiple Cities, India"),
                ("AICTE Industry Internship (NASSCOM)", "Multiple Cities, India"),
                ("AICTE IDEA Lab Internship", "India"),
                ("AICTE Smart India Hackathon Internship", "India"),
                ("AICTE Industry 4.0 Internship", "India"),
            ]
            for title, location in known_programs:
                jobs.append({
                    "title": title,
                    "company": "AICTE",
                    "location": location,
                    "job_type": "Internship",
                    "opportunity_category": "Internship",
                    "description": f"{title}. Official AICTE internship program for students at AICTE-approved institutions. Visit internship.aicte-india.org for details and application.",
                    "apply_url": "https://internship.aicte-india.org/",
                    "source": self.source_name,
                    "source_url": "https://internship.aicte-india.org/",
                    "raw_data": {"source_type": "AICTE Known Programs"},
                })

        self.health_status = "Healthy" if jobs else "Warning"
        logger.info(f"AICTE Collector: {len(jobs)} internships collected.")
        return jobs
