import logging
import requests
from typing import List, Dict, Any
from ..base_collector import BaseCollector

logger = logging.getLogger("collector_devto")

class DevToCollector(BaseCollector):
    def __init__(self):
        self.health_status = "Healthy"

    @property
    def source_name(self) -> str:
        return "Dev.to Articles API"

    def collect(self) -> List[Dict[str, Any]]:
        logger.info("Starting real data collection for Learning Resources (Dev.to)...")
        resources = []
        
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get("https://dev.to/api/articles?tag=tutorial&top=1", headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            for item in data[:20]:  # Limit to 20 resources
                title = item.get("title", "")
                
                # Try handling unicode title chars gracefully
                try:
                    title = title.encode('ascii', 'ignore').decode('ascii')
                except Exception:
                    pass
                    
                resources.append({
                    "title": title,
                    "provider": item.get("user", {}).get("name", "Unknown Author"),
                    "category": "Article/Tutorial",
                    "description": item.get("description", ""),
                    "url": item.get("url", ""),
                    "difficulty": "All Levels",
                    "duration": f"{item.get('reading_time_minutes', 5)} min read",
                    "is_free": True,
                    "skills_covered": item.get("tag_list", []),
                    "source": self.source_name,
                    "is_processed": False,
                    "raw_data": {"source_type": "Public API", "health": "Healthy"}
                })
                
        except Exception as e:
            self.health_status = "Failed"
            logger.error(f"Dev.to Collector unavailable. Reason: {str(e)}")
            
        return resources
