from typing import List, Dict, Any

class IBMCollector:
    def __init__(self):
        self.source_name = 'IBMCollector'
        self.company_name = 'IBM'

    def collect(self) -> List[Dict[str, Any]]:
        return []
