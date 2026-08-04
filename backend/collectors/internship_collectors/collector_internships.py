import requests
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class InternshipCollector:
    """
    Collects real internship opportunities by tapping into public ATS JSON APIs 
    (Greenhouse, Lever) for companies known to hire interns in India, and filtering 
    specifically for internship/fresher roles.
    """
    def __init__(self):
        self.source_name = "Real ATS Internship Collector"
        
        # Companies that use Greenhouse
        self.greenhouse_companies = [
            # Top Startups & Product
            "razorpay", "swiggy", "zomato", "browserstack", 
            "freshworks", "postman", "cred", "meesho",
            "zepto", "phonepe", "groww", "urbancompany",
            "sharechat", "darwinbox", "porter", "apna",
            # Global Product
            "mongodb", "airbnb", "pinterest", "stripe", "figma",
            "coinbase", "plaid", "canva", "reddit", "discord",
            "dropbox", "twitch", "github"
        ]
        
        # Companies that use Lever
        self.lever_companies = [
            "atlassian", "kpmg", "nielsen", "coursera", "palantir",
            "netflix", "yelp", "shopify", "okta"
        ]
        
        # Keywords to identify internships
        self.intern_keywords = [
            "intern", "internship", "fresher", "graduate", 
            "trainee", "apprenticeship", "campus", "get", 
            "early career", "new grad"
        ]

    def _is_internship(self, title: str) -> bool:
        import re
        title_lower = title.lower()
        return any(re.search(r'\b' + keyword + r'\b', title_lower) for keyword in self.intern_keywords)

    def _fetch_greenhouse(self) -> List[Dict[str, Any]]:
        internships = []
        for company in self.greenhouse_companies:
            try:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get("jobs", [])
                    for job in jobs:
                        title = job.get("title", "")
                        if self._is_internship(title):
                            loc = job.get("location", {}).get("name", "")
                            
                            internships.append({
                                "title": title,
                                "company": company.capitalize(),
                                "location": loc,
                                "duration": "Summer/Winter",
                                "stipend": "As per company standards",
                                "description": job.get("content", title),
                                "apply_url": job.get("absolute_url", ""),
                                "source": "Greenhouse",
                                "source_url": f"https://boards.greenhouse.io/{company}",
                                "raw_data": job
                            })
            except Exception as e:
                logger.error(f"Error fetching Greenhouse for {company}: {e}")
            time.sleep(1) # Be polite to the API
        return internships
        
    def _fetch_lever(self) -> List[Dict[str, Any]]:
        internships = []
        for company in self.lever_companies:
            try:
                url = f"https://api.lever.co/v0/postings/{company}?mode=json"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    jobs = response.json()
                    for job in jobs:
                        title = job.get("text", "")
                        if self._is_internship(title):
                            loc = job.get("categories", {}).get("location", "")
                            
                            internships.append({
                                "title": title,
                                "company": company.capitalize(),
                                "location": loc,
                                "duration": "Summer/Winter",
                                "stipend": "As per company standards",
                                "description": job.get("descriptionPlain", title),
                                "apply_url": job.get("applyUrl", ""),
                                "source": "Lever",
                                "source_url": job.get("hostedUrl", ""),
                                "raw_data": job
                            })
            except Exception as e:
                logger.error(f"Error fetching Lever for {company}: {e}")
            time.sleep(1)
        return internships

class UnstopCollector:
    def __init__(self):
        self.source_name = "Unstop API"
        self.health_status = "Healthy"
        
    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting Unstop Internship Collection...")
        internships = []
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            url = "https://unstop.com/api/public/opportunity/search-result?opportunity=internships"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                items = data.get("data", {}).get("data", [])
                
                for item in items:
                    title = item.get("title", "")
                    company = item.get("organization", {}).get("name", "Unknown")
                    if not company or company == "Unknown":
                        company = item.get("seo_url", "").split("-")[0].capitalize()
                        
                    # Extract location
                    locs = [loc.get("city", "") for loc in item.get("locations", []) if loc.get("city")]
                    location = ", ".join(locs) if locs else "India"
                    
                    # Extract skills
                    skills = [skill.get("skill_name", "") for skill in item.get("required_skills", [])]
                    
                    # Extract stipends
                    job_detail = item.get("jobDetail", {})
                    min_salary = job_detail.get("min_salary")
                    max_salary = job_detail.get("max_salary")
                    stipend_str = ""
                    if min_salary or max_salary:
                        stipend_str = f"₹{min_salary or 0} - ₹{max_salary or min_salary or 0}"
                    
                    seo_url = item.get("seo_url", "")
                    apply_url = f"https://unstop.com/{seo_url}" if seo_url else ""
                    
                    internships.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "job_type": "Internship",
                        "duration": "Duration specified on Unstop",
                        "stipend": stipend_str or "Unpaid / Not Disclosed",
                        "description": item.get("public_url", "") or "Apply on Unstop.",
                        "required_skills": ", ".join(skills),
                        "apply_url": apply_url,
                        "source": self.source_name,
                        "source_url": apply_url,
                        "raw_data": item
                    })
        except Exception as e:
            self.health_status = "Failed"
            logger.error(f"Unstop Collector failed: {e}")
            
        return internships

    def collect(self) -> List[Dict[str, Any]]:
        logger.info(f"Starting {self.source_name}...")
        jobs = []
        jobs.extend(self._fetch_greenhouse())
        jobs.extend(self._fetch_lever())
        # Let's not call unstop from here if it has a separate collector or if _fetch_unstop exists, we call it.
        # It looks like _fetch_unstop was at the end of the class. Let's call it.
        if hasattr(self, '_fetch_unstop'):
            jobs.extend(self._fetch_unstop())
        return jobs

class AICTECollector:
    def __init__(self):
        self.source_name = "AICTE Internships"
        
    def collect(self) -> List[Dict[str, Any]]:
        return []
