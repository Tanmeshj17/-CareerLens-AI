from typing import List, Dict, Any
from ..base_collector import BaseCollector

class CourseCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Free Courses Directory"

    def collect(self) -> List[Dict[str, Any]]:
        courses = [
            {
                "title": "CS50: Introduction to Computer Science",
                "provider": "Harvard University (edX)",
                "category": "Course",
                "description": "An introduction to the intellectual enterprises of computer science and the art of programming. Learn C, Python, SQL, HTML, CSS, JavaScript, and algorithmic thinking.",
                "url": "https://www.edx.org/learn/computer-science/harvard-university-cs50-s-introduction-to-computer-science",
                "difficulty": "Beginner",
                "duration": "12 Weeks",
                "is_free": True,
                "skills_covered": ["C", "Python", "SQL", "HTML", "CSS", "JavaScript", "Algorithms"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "Google Machine Learning Crash Course",
                "provider": "Google",
                "category": "Course",
                "description": "Google's fast-paced, practical introduction to machine learning, featuring a series of lessons with video lectures, real-world case studies, and hands-on practice exercises.",
                "url": "https://developers.google.com/machine-learning/crash-course",
                "difficulty": "Intermediate",
                "duration": "15 Hours",
                "is_free": True,
                "skills_covered": ["Machine Learning", "Python", "TensorFlow", "Scikit-learn", "Data Science"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "Introduction to Databases and SQL",
                "provider": "Stanford University (Lagunita)",
                "category": "Course",
                "description": "Learn the basics of relational databases, relational algebra, SQL, database design, XML, JSON, and schema structure.",
                "url": "https://online.stanford.ed/courses/soe-ydatabases-databases",
                "difficulty": "Beginner",
                "duration": "6 Weeks",
                "is_free": True,
                "skills_covered": ["SQL", "Databases", "Database Design", "JSON", "PostgreSQL"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "React Basics",
                "provider": "Meta (Coursera)",
                "category": "Course",
                "description": "Learn the foundational concepts of React, components, JSX, hooks, state, and properties. Build simple single page applications.",
                "url": "https://www.coursera.org/learn/react-basics",
                "difficulty": "Beginner",
                "duration": "20 Hours",
                "is_free": True,
                "skills_covered": ["React", "JavaScript", "HTML", "CSS", "UI/UX"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "Python for Everybody Specialization",
                "provider": "University of Michigan (Coursera)",
                "category": "Course",
                "description": "Learn to program and analyze data with Python. Covers variables, data structures, databases, API integration, and web scraping.",
                "url": "https://www.coursera.org/specializations/python-everybody",
                "difficulty": "Beginner",
                "duration": "3 Months",
                "is_free": True,
                "skills_covered": ["Python", "Data Structures", "Web Scraping", "SQL", "APIs"],
                "source": self.source_name,
                "is_processed": False
            },
            {
                "title": "Kubernetes for Developers",
                "provider": "CNCF (edX)",
                "category": "Course",
                "description": "Learn how to containerize, host, deploy, and scale applications on Kubernetes clusters using GitOps workflows.",
                "url": "https://www.edx.org/learn/kubernetes/linuxfoundation-kubernetes-for-developers",
                "difficulty": "Advanced",
                "duration": "4 Weeks",
                "is_free": True,
                "skills_covered": ["Kubernetes", "Docker", "DevOps", "Cloud Computing", "Linux"],
                "source": self.source_name,
                "is_processed": False
            }
        ]
        return courses
