import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class NaukriCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Naukri"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {
            "User-Agent": "Mozilla/5.0",
            "AppId": "109",
            "SystemId": "109"
        }
        
        # Phase 8.45: Graduate & Internship Explosion Queries
        queries = [
            "software-engineer", "data-analyst", "fresher", 
            "graduate-engineer-trainee", "get", "analyst-program",
            "associate-software-engineer", "trainee-engineer", 
            "campus-hiring", "intern", "internship", "summer-intern"
        ]
        
        for q in queries:
            logger.info(f"[Naukri] Searching for {q}")
            consecutive_dupes = 0
            
            for page in range(1, max_pages + 1):
                url = f"https://www.naukri.com/{q}-jobs-{page}"
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_=lambda x: x and 'jobTuple' in x)
                    
                    if not job_cards:
                        break
                        
                    for card in job_cards:
                        title_elem = card.find('a', class_='title')
                        company_elem = card.find('a', class_='subTitle')
                        loc_elem = card.find('li', class_='location')
                        
                        if not title_elem or not company_elem:
                            continue
                            
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        location = loc_elem.text.strip() if loc_elem else "India"
                        apply_url = title_elem.get('href')
                        
                        # Phase 8.45: Circuit Breaker
                        if apply_url in known_urls:
                            consecutive_dupes += 1
                        else:
                            consecutive_dupes = 0
                            
                        if consecutive_dupes >= 20:
                            logger.info(f"[Naukri] Circuit breaker triggered on {q}, page {page}")
                            break
                        
                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_type": "Internship" if "intern" in q.lower() else "Job",
                            "description": f"{title} at {company} via Naukri.",
                            "apply_url": apply_url,
                            "source_url": "https://www.naukri.com",
                            "source": self.source_name,
                            "ats_type": "Naukri",
                            "raw_data": {}
                        })
                        
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"[Naukri] Error on {q} page {page}: {e}")
                    break
                    
        return all_jobs
