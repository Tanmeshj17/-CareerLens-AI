from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCollector(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the source, e.g. LinkedIn, Official, Cutshort"""
        pass

    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """Collects raw opportunities and returns them as a list of dicts"""
        pass
