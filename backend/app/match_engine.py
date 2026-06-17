from typing import List, Dict, Any, Tuple
from app.resume_parser import SKILLS_DB
import re

def extract_skills_from_text(text: str) -> List[str]:
    """Helper to extract skills from job description text when no explicit required_skills are set."""
    if not text:
        return []
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if len(skill) <= 2:
            pattern = rf"\b{re.escape(skill)}\b"
        else:
            pattern = rf"\b{re.escape(skill)}\b"
        if re.search(pattern, text_lower):
            if skill in ["aws", "gcp", "azure", "ci/cd", "k8s", "ml", "ai", "db", "sql", "ui", "ux", "sre", "mvc"]:
                found_skills.append(skill.upper())
            elif skill == "spring boot":
                found_skills.append("Spring Boot")
            elif skill == "node.js":
                found_skills.append("Node.js")
            elif skill == "vue.js":
                found_skills.append("Vue.js")
            elif skill == "next.js":
                found_skills.append("Next.js")
            elif skill == "react":
                found_skills.append("React")
            else:
                found_skills.append(skill.title())
    return sorted(list(set(found_skills)))

def calculate_match(resume_skills: List[str], job_required_skills: str, job_description: str) -> Tuple[int, List[str], List[str], str]:
    """
    Compares resume skills with job required skills.
    Returns: (match_score, matching_skills, missing_skills, match_level)
    """
    # Parse required skills from the job
    req_skills_list = []
    if job_required_skills:
        req_skills_list = [s.strip() for s in job_required_skills.split(",") if s.strip()]
    
    # If no required skills are defined, extract them from the description on the fly
    if not req_skills_list:
        req_skills_list = extract_skills_from_text(job_description)
    
    # If still no skills, return a baseline of 60% match with no matching/missing
    if not req_skills_list:
        return 60, [], [], "Moderate"

    # Normalize both lists for matching
    resume_skills_set = {s.lower() for s in resume_skills}
    req_skills_normalized = {s.lower(): s for s in req_skills_list}

    matching_skills = []
    missing_skills = []

    for req_lower, req_original in req_skills_normalized.items():
        if req_lower in resume_skills_set:
            matching_skills.append(req_original)
        else:
            # Try sub-string matching (e.g. "React" in "React.js" or "Postgres" in "PostgreSQL")
            found = False
            for res_skill in resume_skills_set:
                if res_skill in req_lower or req_lower in res_skill:
                    matching_skills.append(req_original)
                    found = True
                    break
            if not found:
                missing_skills.append(req_original)

    # Compute score
    total_req = len(req_skills_normalized)
    num_match = len(matching_skills)
    
    score = int((num_match / total_req) * 100)
    score = max(30, min(score, 100))  # Minimum of 30% for a match

    # Categorize match level
    if score >= 85:
        match_level = "Excellent"
    elif score >= 70:
        match_level = "Good"
    elif score >= 50:
        match_level = "Moderate"
    else:
        match_level = "Low"

    return score, sorted(matching_skills), sorted(missing_skills), match_level
