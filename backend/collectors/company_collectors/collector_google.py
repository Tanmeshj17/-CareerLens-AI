from typing import List, Dict, Any
from ..base_collector import BaseCollector

class GoogleCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Google Careers"

    def collect(self) -> List[Dict[str, Any]]:
        jobs = [
            {
                "title": "Software Engineer, Google Cloud",
                "company": "Google",
                "location": "Bangalore, India",
                "job_type": "Full-time",
                "description": "Develop next-generation storage and computing services for Google Cloud Platform. Candidates must have excellent coding skills in Go, Java, or C++, experience with distributed systems design, and cloud architecture.",
                "salary_range": "35,00,000 - 55,00,000 INR",
                "apply_url": "https://careers.google.com/jobs/results/G1092837",
                "source": self.source_name,
                "source_url": "https://careers.google.com/jobs",
                "raw_data": '{"jobId": "G1092837", "level": "L4", "domain": "Cloud"}',
                "is_processed": False
            },
            {
                "title": "Site Reliability Engineer (SRE)",
                "company": "Google",
                "location": "Hyderabad, India",
                "job_type": "Full-time",
                "description": "Ensure Google's core services are highly available, reliable, and performant. Strong knowledge of Linux internals, TCP/IP networking, Python, Go or shell scripting, and automation tools.",
                "salary_range": "30,00,000 - 48,00,000 INR",
                "apply_url": "https://careers.google.com/jobs/results/G1092838",
                "source": self.source_name,
                "source_url": "https://careers.google.com/jobs",
                "raw_data": '{"jobId": "G1092838", "level": "L4", "domain": "SRE"}',
                "is_processed": False
            },
            {
                "title": "Research Scientist, Machine Learning",
                "company": "Google",
                "location": "Bangalore, India",
                "job_type": "Full-time",
                "description": "Conduct cutting-edge research in deep learning, natural language processing, and computer vision. Strong publications record at top AI venues (NeurIPS, ICML, CVPR). Expert in Python, TensorFlow, and PyTorch.",
                "salary_range": "45,00,000 - 70,00,000 INR",
                "apply_url": "https://careers.google.com/jobs/results/G1092839",
                "source": self.source_name,
                "source_url": "https://careers.google.com/jobs",
                "raw_data": '{"jobId": "G1092839", "level": "L5", "domain": "Google Research"}',
                "is_processed": False
            },
            {
                "title": "Front End Engineer, YouTube",
                "company": "Google",
                "location": "Bangalore, India",
                "job_type": "Full-time",
                "description": "Build high-performance, accessible, and interactive user interfaces for YouTube. Expert in React, TypeScript, HTML5, CSS3/SASS, and web performance optimization.",
                "salary_range": "28,00,000 - 45,00,000 INR",
                "apply_url": "https://careers.google.com/jobs/results/G1092840",
                "source": self.source_name,
                "source_url": "https://careers.google.com/jobs",
                "raw_data": '{"jobId": "G1092840", "level": "L3", "domain": "YouTube"}',
                "is_processed": False
            },
            {
                "title": "Data Scientist, Product Analytics",
                "company": "Google",
                "location": "Hyderabad, India",
                "job_type": "Full-time",
                "description": "Partner with product teams to design experiments, extract insights, and build ML models. Required: SQL, Python (pandas, NumPy, statsmodels), statistics, and experience with A/B testing methodologies.",
                "salary_range": "25,00,000 - 40,00,000 INR",
                "apply_url": "https://careers.google.com/jobs/results/G1092841",
                "source": self.source_name,
                "source_url": "https://careers.google.com/jobs",
                "raw_data": '{"jobId": "G1092841", "level": "L4", "domain": "Product Analytics"}',
                "is_processed": False
            },
            {
                "title": "Security Engineer, Infrastructure",
                "company": "Google",
                "location": "Bangalore, India",
                "job_type": "Full-time",
                "description": "Perform security reviews, threat modeling, and design secure protocols for core infrastructure. Strong understanding of cryptography, cloud security, network protocols, and secure coding in Go or Python.",
                "salary_range": "32,00,000 - 52,00,000 INR",
                "apply_url": "https://careers.google.com/jobs/results/G1092842",
                "source": self.source_name,
                "source_url": "https://careers.google.com/jobs",
                "raw_data": '{"jobId": "G1092842", "level": "L4", "domain": "Security"}',
                "is_processed": False
            }
        ]
        return jobs
