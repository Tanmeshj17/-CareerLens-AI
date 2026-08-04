import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class FreshersworldCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Freshersworld"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        
        # Categories to scrape
        urls = [
            "https://www.freshersworld.com/it-jobs",
            "https://www.freshersworld.com/engineering-jobs"
        ]
        
        for url in urls:
            logger.info(f"[Freshersworld] Scraping {url}")
            consecutive_dupes = 0
            stop_url = False
            
            for page in range(1, max_pages + 1): # Fetch based on max_pages
                page_url = f"{url}?limit=20&offset={(page-1)*20}"
                
                try:
                    response = requests.get(page_url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='job-container')
                    
                    if not job_cards:
                        break
                        
                    for card in job_cards:
                        title_elem = card.find('h3', class_='seo_title')
                        company_elem = card.find('h3', class_='latest-jobs-title')
                        loc_elem = card.find('span', class_='job-location')
                        
                        if not title_elem or not company_elem:
                            continue
                            
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        location = loc_elem.text.strip() if loc_elem else "India"
                        
                        a_tag = card.find('a', id=lambda x: x and 'job_title' in x)
                        apply_url = a_tag.get('href') if a_tag else ""
                        if apply_url and not apply_url.startswith("http"):
                            apply_url = "https://www.freshersworld.com" + apply_url
                            
                        if not apply_url:
                            continue
                        
                        # Phase 8.45: Circuit Breaker
                        if apply_url in known_urls:
                            consecutive_dupes += 1
                        else:
                            consecutive_dupes = 0
                            
                        if consecutive_dupes >= 20:
                            logger.info(f"[Freshersworld] Circuit breaker triggered on {url}, page {page}")
                            stop_url = True
                            break
                            
                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_type": "Job",
                            "description": f"{title} at {company} via Freshersworld.",
                            "apply_url": apply_url,
                            "source_url": "https://www.freshersworld.com",
                            "source": self.source_name,
                            "ats_type": "Freshersworld",
                            "raw_data": {}
                        })
                        
                    if stop_url:
                        break
                        
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"[Freshersworld] Error on page {page}: {e}")
                    break
                    
        return all_jobs
