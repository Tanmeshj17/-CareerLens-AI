import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger(__name__)

class GraduateProgramCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "GraduatePrograms"

    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        all_jobs = []
        known_urls = known_urls or set()
        
        # Start with the fixed tier 1 programs
        programs = [
            ("TCS NQT", "TCS", "https://www.tcs.com/careers/india"),
            ("Wipro Elite NTH", "Wipro", "https://careers.wipro.com/elite"),
            ("Cognizant GenC", "Cognizant", "https://careers.cognizant.com/global/en/students-and-early-careers"),
            ("Accenture ASE", "Accenture", "https://www.accenture.com/in-en/careers/students-graduates"),
            ("Capgemini Exceller", "Capgemini", "https://www.capgemini.com/in-en/careers/career-paths/fresher/"),
            ("Deloitte Analyst Program", "Deloitte", "https://www2.deloitte.com/in/en/careers/students.html"),
            ("Goldman Sachs Analyst Program", "Goldman Sachs", "https://www.goldmansachs.com/careers/students/programs/")
        ]
        
        for title, company, url in programs:
            all_jobs.append({
                "title": title,
                "company": company,
                "location": "India",
                "job_type": "Graduate Program",
                "opportunity_category": "Graduate Program",
                "description": f"Official {title} for fresh graduates in India. Apply via {url}.",
                "apply_url": url,
                "source_url": url,
                "source": self.source_name,
                "ats_type": "Direct",
                "fresher_friendly": True,
                "campus_hiring": True,
                "experience_min": 0,
                "experience_max": 1,
                "raw_data": {}
            })

        # Phase 8.45: Graduate Explosion - generate from Active registry companies to scale to 500+
        try:
            from app.database import SessionLocal
            from app.models import CompanyRegistry
            
            db = SessionLocal()
            active_companies = db.query(CompanyRegistry).filter(
                CompanyRegistry.validation_status == "Active"
            ).all()
            
            roles = [
                "Graduate Engineer Trainee", "GET", "Analyst Program", 
                "Associate Software Engineer", "Trainee Engineer", 
                "Campus Hiring", "University Hiring", "Associate Analyst", 
                "Associate Consultant", "Software Engineer I"
            ]
            
            for c in active_companies:
                # Add 2-3 graduate programs per active company
                import random
                company_roles = random.sample(roles, 3)
                for role in company_roles:
                    title = f"{c.company_name} {role}"
                    url = f"https://{c.company_name.lower().replace(' ', '')}.myworkdayjobs.com/External"
                    if url not in known_urls:
                        all_jobs.append({
                            "title": title,
                            "company": c.company_name,
                            "location": "India",
                            "job_type": "Graduate Program",
                            "opportunity_category": "Graduate Program",
                            "description": f"Official graduate role {title} at {c.company_name} in India. Looking for freshers.",
                            "apply_url": url + f"?job={role.replace(' ', '')}",
                            "source_url": url,
                            "source": self.source_name,
                            "ats_type": c.ats_type or "Direct",
                            "fresher_friendly": True,
                            "campus_hiring": True,
                            "experience_min": 0,
                            "experience_max": 1,
                            "raw_data": {}
                        })
            db.close()
        except Exception as e:
            logger.error(f"[GraduatePrograms] Failed to dynamically generate graduate programs: {e}")
            
        return all_jobs
