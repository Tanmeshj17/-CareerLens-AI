import logging
import requests
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_jobicy")

class JobicyCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Jobicy Remote Jobs"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting real data collection for Jobicy Remote Jobs API...")
        jobs = []
        
        try:
            # Priority 1: Public API
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get("https://jobicy.com/api/v2/remote-jobs?count=20", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            for job in data.get("jobs", []):
                jobs.append({
                    "title": job.get("jobTitle", "Unknown Title"),
                    "company": job.get("companyName", "Unknown Company"),
                    "location": job.get("jobGeo", "Remote"),
                    "job_type": job.get("jobType", "Full-time"),
                    "description": job.get("jobDescription", ""),
                    "salary_range": job.get("annualSalaryMin", ""),
                    "apply_url": job.get("url", ""),
                    "source": self.source_name,
                    "source_url": "https://jobicy.com/",
                    "raw_data": {"source_type": "Public API", "health": "Healthy", "original_id": job.get("id")},
                    "is_processed": False
                })
                
        except Exception as e:
            self.health_status = "Failed"
            logger.error(f"Jobicy Collector unavailable. Reason: {str(e)}")
            
        return jobs
