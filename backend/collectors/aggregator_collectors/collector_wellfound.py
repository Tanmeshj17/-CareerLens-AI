import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class WellfoundCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Wellfound"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        # Wellfound India roles
        roles = [
            "software-engineer", 
            "data-scientist", 
            "product-manager", 
            "frontend-developer", 
            "backend-developer"
        ]
        
        for role in roles:
            logger.info(f"[Wellfound] Scraping role: {role}")
            consecutive_dupes = 0
            stop_role = False
            
            for page in range(1, max_pages + 1):
                url = f"https://wellfound.com/role/l/{role}/india?page={page}"
                
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code != 200:
                        logger.warning(f"[Wellfound] HTTP {response.status_code} for {role} page {page}")
                        break
                        
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_=lambda x: x and 'styles_component' in x and 'JobCard' in x)
                    
                    if not job_cards:
                        # Fallback for old class
                        job_cards = soup.find_all('div', class_='job_listing')
                        
                    if not job_cards:
                        break # End of pagination
                        
                    for a_tag in soup.find_all('a'):
                        href = a_tag.get('href', '')
                        if '/jobs/' in href and not href.startswith('http'):
                            apply_url = f"https://wellfound.com{href}"
                            
                            # Phase 8.45: Circuit Breaker
                            if apply_url in known_urls:
                                consecutive_dupes += 1
                            else:
                                consecutive_dupes = 0
                                
                            if consecutive_dupes >= 20:
                                logger.info(f"[Wellfound] Circuit breaker triggered on role {role}")
                                stop_role = True
                                break

                            # Extract title and company from the card. This varies heavily in React.
                            # We will make best-effort extraction from the parent divs.
                            parent = a_tag.find_parent('div')
                            if not parent:
                                continue
                                
                            # Extremely basic heuristic since classes change daily
                            title = a_tag.text.strip()
                            if not title:
                                continue
                                
                            # Try to find company name near the title
                            company_elem = parent.find_previous_sibling('h2') or parent.find_parent('div').find('h2')
                            company = company_elem.text.strip() if company_elem else "Wellfound Startup"
                            
                            all_jobs.append({
                                "title": title,
                                "company": company,
                                "location": "India", # The search page is explicitly /india
                                "job_type": "Job",
                                "description": f"{title} at {company} via Wellfound India.",
                                "apply_url": apply_url,
                                "source_url": "https://wellfound.com",
                                "source": self.source_name,
                                "ats_type": "Wellfound",
                                "raw_data": {}
                            })
                            
                    if stop_role:
                        break
                    time.sleep(1) # Polite pagination
                except Exception as e:
                    logger.error(f"[Wellfound] Error parsing {role} page {page}: {e}")
                    break

        # Deduplicate within collector (since we extract links directly, some might appear twice)
        unique_jobs = {j["apply_url"]: j for j in all_jobs}.values()
        return list(unique_jobs)
