from typing import List, Dict, Any
from ..base_collector import BaseCollector

class YoutubeCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "YouTube Learning Portal"

    def collect(self) -> List[Dict[str, Any]]:
        resources = [
            {
                "title": "Fireship",
                "provider": "Jeff Delaney (Fireship)",
                "category": "YouTube",
                "description": "Code tutorials in 100 seconds. High-speed coding tutorials, technology reviews, framework breakdowns, and dev news.",
                "url": "https://www.youtube.com/@Fireship",
                "difficulty": "Beginner",
                "duration": "N/A",
                "is_free": True,
                "skills_covered": ["JavaScript", "Python", "React", "Next.js", "Docker", "DevOps", "AI"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "ThePrimeagen",
                "provider": "ThePrimeagen",
                "category": "YouTube",
                "description": "Insightful coding streams, backend architecture analyses, software engineering rants, and Neovim/Vim setups.",
                "url": "https://www.youtube.com/@ThePrimeTimeagen",
                "difficulty": "Advanced",
                "duration": "N/A",
                "is_free": True,
                "skills_covered": ["Rust", "Go", "TypeScript", "Vim", "Neovim", "Backend Architecture", "Docker"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "freeCodeCamp.org",
                "provider": "freeCodeCamp",
                "category": "YouTube",
                "description": "Comprehensive, multi-hour video courses on python, web development, cloud certifications, machine learning, data analyst, and DevOps.",
                "url": "https://www.youtube.com/@freecodecamp",
                "difficulty": "Beginner",
                "duration": "4-10 Hours per Course",
                "is_free": True,
                "skills_covered": ["Python", "JavaScript", "HTML", "CSS", "SQL", "React", "Docker", "Machine Learning"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "NetworkChuck",
                "provider": "NetworkChuck",
                "category": "YouTube",
                "description": "Energetic and hands-on IT, networking, Linux, CCNA, hacking, docker, and smart home networking tutorials.",
                "url": "https://www.youtube.com/@NetworkChuck",
                "difficulty": "Beginner",
                "duration": "N/A",
                "is_free": True,
                "skills_covered": ["Linux", "Docker", "Networking", "Python", "Cybersecurity", "Bash"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "Hussein Nasser",
                "provider": "Hussein Nasser",
                "category": "YouTube",
                "description": "Deep-dives into backend engineering, web protocols, database engineering, system design, proxy configurations (Nginx/HAProxy), and networking models.",
                "url": "https://www.youtube.com/@hnasr",
                "difficulty": "Advanced",
                "duration": "N/A",
                "is_free": True,
                "skills_covered": ["Backend Architecture", "Databases", "Nginx", "gRPC", "WebSockets", "HTTP", "Redis"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "ArjanCodes",
                "provider": "Arjan Egges",
                "category": "YouTube",
                "description": "Deep discussions on software design patterns, clean code principles, refactoring strategies, object-oriented design, and type hints in Python.",
                "url": "https://www.youtube.com/@ArjanCodes",
                "difficulty": "Intermediate",
                "duration": "N/A",
                "is_free": True,
                "skills_covered": ["Python", "Design Patterns", "Clean Code", "OOP", "Refactoring", "Testing"],
                "source": self.source_name,
                "is_processed": False
            }
        ]
        return resources
