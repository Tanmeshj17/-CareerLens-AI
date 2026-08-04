import requests
from bs4 import BeautifulSoup
import time
import logging
import urllib.parse
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class LinkedInCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "LinkedIn"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Phase 8.45: Graduate & Internship Explosion Queries
        keywords = [
            "fresher", "entry level software engineer", "graduate engineer trainee", 
            "get", "analyst program", "associate software engineer", "trainee engineer", 
            "campus hiring", "intern", "internship", "summer intern"
        ]
        
        for keyword in keywords:
            logger.info(f"[LinkedIn] Searching for {keyword}")
            consecutive_dupes = 0
            
            # max_pages * 25 jobs per page
            max_start = max_pages * 25
            for start in range(0, max_start, 25): 
                url = f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote(keyword)}&location=India&f_TPR=r86400&start={start}"
                
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    if not job_cards:
                        break
                        
                    for card in job_cards:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        loc_elem = card.find('span', class_='job-search-card__location')
                        a_tag = card.find('a', class_='base-card__full-link')
                        
                        if not title_elem or not company_elem or not a_tag:
                            continue
                            
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        location = loc_elem.text.strip() if loc_elem else "India"
                        apply_url = a_tag.get('href')
                        
                        # Phase 8.45: Circuit Breaker
                        if apply_url in known_urls:
                            consecutive_dupes += 1
                        else:
                            consecutive_dupes = 0
                            
                        if consecutive_dupes >= 20:
                            logger.info(f"[LinkedIn] Circuit breaker triggered on {keyword}, start={start}")
                            break
                        
                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_type": "Internship" if "intern" in keyword.lower() else "Job",
                            "description": f"{title} at {company} via LinkedIn India.",
                            "apply_url": apply_url,
                            "source_url": "https://www.linkedin.com/jobs",
                            "source": self.source_name,
                            "ats_type": "LinkedIn",
                            "raw_data": {}
                        })
                        
                    time.sleep(2) # LinkedIn blocks heavily, need longer sleep
                except Exception as e:
                    logger.error(f"[LinkedIn] Error on {keyword} start {start}: {e}")
                    break
                    
        return all_jobs
