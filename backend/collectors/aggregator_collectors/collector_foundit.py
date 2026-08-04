import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector
import urllib.parse

logger = logging.getLogger(__name__)

class FounditCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "FoundIt"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        # Search queries for FoundIt India
        queries = ["fresher", "intern", "software engineer", "data analyst", "developer"]
        
        for q in queries:
            logger.info(f"[FoundIt] Searching for {q}")
            consecutive_dupes = 0
            stop_q = False
            for page in range(1, max_pages + 1):
                # foundit.in is the India portal
                # The search URL structure usually: https://www.foundit.in/srp/results?query=keyword&start=X
                start = (page - 1) * 15
                url = f"https://www.foundit.in/srp/results?query={urllib.parse.quote(q)}&start={start}"
                
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        logger.warning(f"[FoundIt] HTTP {response.status_code} for query {q}")
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Typical foundit job card class is 'card-apply-content' or 'job-tittle'
                    # We will look for standard link patterns in search results if classes change
                    job_cards = soup.find_all('div', class_='card-apply-content')
                    
                    if not job_cards:
                        # Sometimes it's inside 'srp-jobtuple-wrapper'
                        job_cards = soup.find_all('div', class_='srp-jobtuple-wrapper')
                        
                    if not job_cards:
                        break # End of results or blocked
                        
                    for card in job_cards:
                        title_elem = card.find('h3') or card.find('div', class_='job-tittle')
                        company_elem = card.find('span', class_='company-name')
                        location_elem = card.find('div', class_='details-panel-item--location') or card.find('span', class_='loc')
                        
                        if not title_elem or not company_elem:
                            continue
                            
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        location = location_elem.text.strip() if location_elem else "India"
                        
                        # Find link
                        a_tag = card.find('a')
                        if not a_tag or not a_tag.get('href'):
                            continue
                            
                        apply_url = a_tag['href']
                        if apply_url.startswith('//'):
                            apply_url = 'https:' + apply_url
                        elif apply_url.startswith('/'):
                            apply_url = 'https://www.foundit.in' + apply_url
                            
                        # Phase 8.45: Circuit Breaker
                        if apply_url in known_urls:
                            consecutive_dupes += 1
                        else:
                            consecutive_dupes = 0
                            
                        if consecutive_dupes >= 20:
                            logger.info(f"[FoundIt] Circuit breaker triggered on query {q}")
                            stop_q = True
                            break

                        # Hard reject global locations (Task 3 requires rejecting US/UK/EMEA/LATAM)
                        loc_lower = location.lower()
                        reject_words = ["usa", "us", "uk", "emea", "latam", "remote - global", "united states", "europe"]
                        if any(rw in loc_lower for rw in reject_words):
                            continue
                            
                        job_type = "Internship" if "intern" in title.lower() or "intern" in q else "Job"
                        
                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_type": job_type,
                            "description": f"{job_type} at {company} found via FoundIt.",
                            "apply_url": apply_url,
                            "source_url": "https://www.foundit.in",
                            "source": self.source_name,
                            "ats_type": "FoundIt",
                            "raw_data": {}
                        })
                        
                    if stop_q:
                        break
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"[FoundIt] Error on page {page} for {q}: {e}")
                    break

        return all_jobs
