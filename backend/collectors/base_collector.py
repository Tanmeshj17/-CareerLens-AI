from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CollectorException(Exception):
    """Base exception for all collector errors"""
    pass

class RateLimitException(CollectorException):
    """Raised when collector hits an IP/account rate limit"""
    pass

class StructureChangeException(CollectorException):
    """Raised when target site DOM/API changes drastically"""
    pass

class BlockedException(CollectorException):
    """Raised when collector is blocked by WAF/Cloudflare"""
    pass

class OpportunityData(BaseModel):
    title: str
    company: str
    location: str
    apply_url: str
    description: Optional[str] = None
    job_type: Optional[str] = "Full-time"
    primary_source: str
    is_india_job: bool = False
    source_type: str = "DIRECT_EMPLOYER"
    
class BaseCollector(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the source, e.g. LinkedIn, Official, Cutshort"""
        pass

    @abstractmethod
    def collect(self, max_pages: int = 5, known_urls: set = None) -> List[Dict[str, Any]]:
        """Collects raw opportunities and returns them as a list of dicts. Legacy support."""
        pass
        
    def collect_strict(self, max_pages: int = 5) -> List[OpportunityData]:
        """Strict collection method that returns validated Pydantic models"""
        raise NotImplementedError("This collector has not implemented strict collection yet.")
