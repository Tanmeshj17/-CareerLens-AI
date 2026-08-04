import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class InstahyreCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Instahyre"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        # Instahyre usually uses categories in URL
        categories = ["software-engineering", "data-science", "product-management"]
        
        for cat in categories:
            logger.info(f"[Instahyre] Scraping category: {cat}")
            consecutive_dupes = 0
            stop_cat = False
            
            for page in range(1, max_pages + 1):
                url = f"https://www.instahyre.com/search-jobs/?category={cat}&page={page}"
                
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        logger.warning(f"[Instahyre] HTTP {response.status_code} for {cat} page {page}")
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='employer-block')
                    if not job_cards:
                        break # End of pagination
                
                    for card in job_cards:
                        title_elem = card.find('div', class_='job-title') or card.find('h2')
                        company_elem = card.find('div', class_='company-name') or card.find('div', class_='employer-details-company')
                        location_elem = card.find('span', class_='location')
                        
                        if not title_elem or not company_elem:
                            continue
                            
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        location = location_elem.text.strip() if location_elem else "India"
                        
                        a_tag = card.find('a', id=lambda x: x and x.startswith('apply-url-'))
                        if not a_tag and card.find('a'):
                            a_tag = card.find('a')
                            
                        if not a_tag or not a_tag.get('href'):
                            continue
                            
                        apply_url = a_tag['href']
                        if apply_url.startswith('/'):
                            apply_url = 'https://www.instahyre.com' + apply_url
                            
                        # Phase 8.45: Circuit Breaker
                        if apply_url in known_urls:
                            consecutive_dupes += 1
                        else:
                            consecutive_dupes = 0
                            
                        if consecutive_dupes >= 20:
                            logger.info(f"[Instahyre] Circuit breaker triggered on category {cat}, page {page}")
                            stop_cat = True
                            break
                            
                        all_jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "job_type": "Job",
                            "description": f"{title} at {company} via Instahyre.",
                            "apply_url": apply_url,
                            "source_url": "https://www.instahyre.com",
                            "source": self.source_name,
                            "ats_type": "Instahyre",
                            "raw_data": {}
                        })
                        
                    if stop_cat:
                        break
                        
                    time.sleep(1) # Be polite between pages
                        
                except Exception as e:
                    logger.error(f"[Instahyre] Error scraping: {e}")
                    break
 
        return all_jobs
