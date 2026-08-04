import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from app.models import DiscoveredCompanyATS
from sqlalchemy.orm import Session
from datetime import datetime

logger = logging.getLogger(__name__)

class ATSDiscoveryEngine:
    def __init__(self, db: Session):
        self.db = db
        
    def _detect_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        if "myworkdayjobs.com" in domain:
            return {"ats_type": "workday", "confidence": 100, "method": "URL Pattern"}
        if "greenhouse.io" in domain or "boards.greenhouse.io" in domain:
            return {"ats_type": "greenhouse", "confidence": 100, "method": "URL Pattern"}
        if "jobs.lever.co" in domain:
            return {"ats_type": "lever", "confidence": 100, "method": "URL Pattern"}
        if "darwinbox.in" in domain:
            return {"ats_type": "darwinbox", "confidence": 100, "method": "URL Pattern"}
        if "teamtailor.com" in domain:
            return {"ats_type": "teamtailor", "confidence": 100, "method": "URL Pattern"}
        if "recruitee.com" in domain:
            return {"ats_type": "recruitee", "confidence": 100, "method": "URL Pattern"}
        if "bamboohr.com" in domain:
            return {"ats_type": "bamboohr", "confidence": 100, "method": "URL Pattern"}
        if "smartrecruiters.com" in domain:
            return {"ats_type": "smartrecruiters", "confidence": 100, "method": "URL Pattern"}
        if "oraclecloud.com" in domain:
            return {"ats_type": "oracle", "confidence": 90, "method": "URL Pattern"}
        if "avature.net" in domain:
            return {"ats_type": "avature", "confidence": 100, "method": "URL Pattern"}
        if "icims.com" in domain:
            return {"ats_type": "icims", "confidence": 100, "method": "URL Pattern"}
        
        return None
        
    def _detect_from_html(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        # Fingerprint via meta tags, common JS files, or specific class names
        text = soup.get_text().lower()
        
        if "powered by greenhouse" in text or soup.find("meta", {"content": "Greenhouse"}):
            return {"ats_type": "greenhouse", "confidence": 85, "method": "HTML Content"}
        
        if "powered by lever" in text:
            return {"ats_type": "lever", "confidence": 85, "method": "HTML Content"}
            
        if "powered by darwinbox" in text or soup.find("link", href=lambda href: href and "darwinbox" in href):
            return {"ats_type": "darwinbox", "confidence": 85, "method": "HTML Content"}
            
        if soup.find("script", src=lambda src: src and "workday" in src.lower()):
            return {"ats_type": "workday", "confidence": 75, "method": "HTML Content"}
            
        return None

    def discover_ats(self, company_name: str, career_url: str) -> Dict[str, Any]:
        """Runs the full discovery pipeline."""
        logger.info(f"Discovering ATS for {company_name} at {career_url}")
        
        # 1. Quick URL pattern check
        detection = self._detect_from_url(career_url)
        redirect_url = career_url
        
        if not detection:
            try:
                # 2. HTTP Probing
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(career_url, headers=headers, timeout=10, allow_redirects=True)
                redirect_url = response.url
                
                # Check URL again after redirect
                detection = self._detect_from_url(redirect_url)
                
                if not detection:
                    # 3. HTML Fingerprinting
                    soup = BeautifulSoup(response.content, "html.parser")
                    detection = self._detect_from_html(soup)
                    
            except Exception as e:
                logger.error(f"Discovery HTTP Error for {company_name}: {e}")
                
        result = detection or {"ats_type": "unknown", "confidence": 0, "method": "Failed"}
        result["redirect_url"] = redirect_url
        
        self._store_result(company_name, career_url, result)
        return result

    def _store_result(self, company_name: str, original_url: str, result: Dict[str, Any]):
        record = self.db.query(DiscoveredCompanyATS).filter(DiscoveredCompanyATS.company_name == company_name).first()
        if not record:
            record = DiscoveredCompanyATS(company_name=company_name)
            self.db.add(record)
            
        record.career_url = original_url
        record.redirect_url = result.get("redirect_url")
        record.ats_type = result.get("ats_type")
        record.detection_method = result.get("method")
        record.confidence = result.get("confidence", 0)
        record.last_checked = datetime.utcnow()
        
        if record.confidence > 80:
            record.last_success = datetime.utcnow()
            record.collector_assigned = record.ats_type
        else:
            record.last_failure = datetime.utcnow()
            
        self.db.commit()
