import json
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import requests

from .ats_engine.base_ats import ATSParserBase

logger = logging.getLogger(__name__)

class GenericGovtCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Government"

    def fetch_jobs(self) -> Any:
        # Fallback to standard web scraping since Gov sites rarely have APIs
        url = self.ats_identifier # For Govt, ats_identifier holds the career_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Very generic parser: look for links that contain "job", "career", "vacancy", "advt"
            jobs = []
            for link in soup.find_all('a', href=True):
                text = link.get_text(strip=True).lower()
                href = link['href']
                if any(keyword in text or keyword in href.lower() for keyword in ["job", "vacancy", "advt", "recruitment"]):
                    
                    full_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                    
                    jobs.append({
                        "title": link.get_text(strip=True)[:100],
                        "url": full_url,
                        "raw_html": str(link)
                    })
            
            # Deduplicate by URL
            unique_jobs = {job["url"]: job for job in jobs}.values()
            return list(unique_jobs)
        except Exception as e:
            logger.error(f"Failed to fetch govt jobs from {url}: {e}")
            return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("title", "Government Opportunity"),
            "company": self.company_name,
            "location": "India",
            "job_type": "Full-time",
            "description": "Please check the official notification for details.",
            "apply_url": raw_job.get("url", ""),
            "source_url": self.ats_identifier,
            "raw_data": raw_job.get("raw_html", "")
        }
