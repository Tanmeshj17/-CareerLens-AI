import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_accenture")

class AccentureCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Accenture Careers"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting real data collection for Accenture Careers...")
        jobs = []
        
        try:
            # Priority 3: Requests + BeautifulSoup HTML Parsing
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get("https://www.accenture.com/in-en/careers/jobsearch", headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("div", class_=lambda x: x and "job" in x.lower())
            
            for card in job_cards:
                title_elem = card.find("h2") or card.find("h3") or card.find("a")
                if not title_elem:
                    continue
                
                # Try to extract actual title text instead of just random nodes
                title_text = title_elem.get_text(strip=True)
                if len(title_text) < 5:
                    continue
                    
                jobs.append({
                    "title": title_text,
                    "company": "Accenture",
                    "location": "India",
                    "job_type": "Full-time",
                    "description": "Collected from Accenture career page.",
                    "apply_url": "https://www.accenture.com/in-en/careers/jobsearch",
                    "source": self.source_name,
                    "source_url": "https://www.accenture.com/in-en/careers/jobsearch",
                    "raw_data": {"source_type": "Career Page HTML", "health": "Healthy"},
                    "is_processed": False
                })
                
            if not jobs:
                self.health_status = "Warning"
                logger.warning(f"Accenture Collector: Page fetched (len {len(response.text)}) but no job cards successfully mapped. JS requirement suspected.")
                
        except Exception as e:
            self.health_status = "Failed"
            logger.error(f"Accenture Collector unavailable. Reason: {str(e)}")
            
        return jobs
