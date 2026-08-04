import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class InternshalaCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Internshala"

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def _scrape_page(self, base_url: str, page: int, job_type_label: str, known_urls: set = None, state: dict = None) -> List[Dict]:
        url = f"{base_url}/page-{page}/" if page > 1 else base_url
        jobs = []
        known_urls = known_urls or set()
        state = state if state is not None else {"consecutive_dupes": 0, "stop": False}
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=15)
            if response.status_code == 404:
                return [] # Reached end of pagination
            if response.status_code != 200:
                logger.warning(f"[Internshala] Failed to fetch page {page}. Status: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                listings = soup.find_all('div', class_='individual_internship')
                if not listings:
                    return []

                for listing in listings:
                try:
                    title_elem = listing.find('h3', class_='heading_4_5')
                    company_elem = listing.find('div', class_='company_name')
                    location_elem = listing.find('a', class_='location_link')
                    
                    if not title_elem or not company_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    location = location_elem.text.strip() if location_elem else "India"
                    
                    # Detect remote
                    if location.lower() in ["work from home", "remote"]:
                        location = "Remote India"
                        
                    # Extract link
                    link_elem = listing.get('data-href')
                    apply_url = f"https://internshala.com{link_elem}" if link_elem else None
                    if not apply_url:
                        a_tag = listing.find('a', class_='view_detail_button')
                        if a_tag and a_tag.get('href'):
                            apply_url = f"https://internshala.com{a_tag['href']}"

                    if not apply_url:
                        continue

                    # Phase 8.45: Circuit Breaker check
                    if apply_url in known_urls:
                        state["consecutive_dupes"] += 1
                    else:
                        state["consecutive_dupes"] = 0

                    if state["consecutive_dupes"] >= 20:
                        logger.info(f"[Internshala] Circuit breaker triggered at {apply_url} on page {page}")
                        state["stop"] = True
                        break

                    # Details parsing (stipend, duration, etc.)
                    stipend = ""
                    duration = ""
                    details_items = listing.find_all('div', class_='item_body')
                    if len(details_items) >= 2:
                        duration_text = details_items[1].text.strip()
                        if "Months" in duration_text or "Weeks" in duration_text:
                            duration = duration_text
                            
                    stipend_elem = listing.find('span', class_='stipend')
                    if stipend_elem:
                        stipend = stipend_elem.text.strip()

                    job_desc = f"{job_type_label} at {company}."
                    if stipend:
                        job_desc += f" Stipend/Salary: {stipend}."
                    if duration:
                        job_desc += f" Duration: {duration}."

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "job_type": job_type_label,
                        "description": job_desc,
                        "apply_url": apply_url,
                        "source_url": "https://internshala.com",
                        "source": self.source_name,
                        "ats_type": "Internshala",
                        "raw_data": {"stipend": stipend, "duration": duration}
                    })
                except Exception as e:
                    logger.debug(f"[Internshala] Error parsing listing: {e}")
            finally:
                soup.decompose()
                    
        except requests.exceptions.RequestException as e:
            logger.warning(f"[Internshala] Network error on page {page}: {e}")

        return jobs

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        
        # Split budget between internships and fresher jobs
        internship_pages = max(1, max_pages)
        fresher_pages = max(1, max_pages // 2)
        
        targets = [
            ("https://internshala.com/internships", "Internship", internship_pages),
            ("https://internshala.com/fresher-jobs", "Job", fresher_pages)
        ]
        
        for base_url, job_type, limit in targets:
            logger.info(f"[Internshala] Scraping {job_type}s from {base_url} (limit: {limit} pages)")
            state = {"consecutive_dupes": 0, "stop": False}
            for page in range(1, limit + 1):
                page_jobs = self._scrape_page(base_url, page, job_type, known_urls=known_urls, state=state)
                if not page_jobs or state["stop"]:
                    break
                all_jobs.extend(page_jobs)
                # Polite rate limiting
                time.sleep(1)
                
        return all_jobs
