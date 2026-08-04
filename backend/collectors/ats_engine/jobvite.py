from typing import List, Dict, Any
import json
from bs4 import BeautifulSoup
from .base_ats import ATSParserBase

class JobviteCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "Jobvite"

    def collect(self) -> List[Dict[str, Any]]:
        # Using typical Jobvite iframe / search endpoint pattern
        url = f"https://jobs.jobvite.com/{self.ats_identifier}/search"
        response = self._make_request(url)
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        job_links = soup.select(".jv-job-list-name a")
        
        results = []
        for link in job_links:
            try:
                title = link.text.strip()
                href = link.get("href", "")
                full_url = f"https://jobs.jobvite.com{href}" if href.startswith("/") else href
                
                row = link.find_parent("tr")
                location = row.select_one(".jv-job-list-location") if row else None
                loc_text = location.text.strip() if location else "Remote"
                
                results.append({
                    "title": title,
                    "company": self.company_name,
                    "location": loc_text,
                    "job_type": "Full-time",
                    "description": "",
                    "apply_url": full_url,
                    "source": "Company Career Page",
                    "ats_type": self.ats_type,
                    "source_url": f"https://jobs.jobvite.com/{self.ats_identifier}",
                    "raw_data": json.dumps({"title": title, "url": full_url})
                })
            except Exception as e:
                continue

        return results
