import json
import time
from typing import Dict, Any, List
from .base_ats import ATSParserBase
import xml.etree.ElementTree as ET

class ICIMSCollector(ATSParserBase):
    @property
    def ats_type(self) -> str:
        return "iCIMS"

    def fetch_jobs(self) -> Any:
        url = f"https://{self.ats_identifier}.icims.com/jobs/rss"
        
        attempt = 0
        while attempt < self.retries:
            try:
                response = requests.get(url, timeout=self.timeout)
                if response.status_code == 429:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                
                response.raise_for_status()
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                jobs = []
                for item in items:
                    job_data = {
                        "title": item.findtext("title", "Unknown Role"),
                        "link": item.findtext("link", ""),
                        "description": item.findtext("description", ""),
                        "pubDate": item.findtext("pubDate", "")
                    }
                    jobs.append(job_data)
                return jobs
            except requests.exceptions.RequestException as e:
                attempt += 1
                self.health_score -= 10
                self.errors.append(f"Network error: {str(e)[:50]}")
            except ET.ParseError as e:
                self.errors.append(f"XML Parsing error: {e}")
                self.health_score -= 20
                return []
        
        return []

    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        return {
            "title": raw_job.get("title", "Unknown Role"),
            "company": self.company_name,
            "location": "Remote", # Usually embedded in description or title
            "job_type": "Full-time",
            "description": raw_job.get("description", ""),
            "apply_url": raw_job.get("link", ""),
            "source_url": f"https://{self.ats_identifier}/jobs",
            "raw_data": json.dumps(raw_job)
        }
