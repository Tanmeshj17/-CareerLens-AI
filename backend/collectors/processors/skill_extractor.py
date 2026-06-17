from typing import List
from app.match_engine import extract_skills_from_text

def extract_required_skills(description: str) -> str:
    """Extract skills from description and return as a comma-separated string."""
    skills = extract_skills_from_text(description)
    return ", ".join(skills)
