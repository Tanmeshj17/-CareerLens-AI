import re
import datetime
from typing import List, Dict, Any, Tuple
from app.resume_parser import SKILLS_DB
from app.skill_normalizer import normalize_skills_list, normalize_skill
from app import models

def extract_skills_from_text(text: str) -> List[str]:
    """Helper to extract skills from job description text when no explicit required_skills are set."""
    if not text:
        return []
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        # Use exact boundary match
        pattern = rf"\b{re.escape(skill.lower())}\b"
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return normalize_skills_list(found_skills)

def get_apply_probability(score: int) -> str:
    """Classifies match score into apply probability."""
    if score >= 85:
        return "High Probability"
    elif score >= 70:
        return "Medium Probability"
    elif score >= 55:
        return "Stretch"
    return "Low Match"

def generate_match_score(user_profile: models.ResumeProfile, prefs: models.UserPreference, opp: models.Opportunity) -> Dict[str, Any]:
    """
    Match Engine V2
    Calculates detailed match score (0-100) based on new weights:
    Role: 35, Skills: 25, Experience: 20, Location: 10, Salary: 5, Company: 5
    """
    components = {
        "role_score": 0, "role_pct": 0, "role_desc": "",
        "skill_score": 0, "skill_pct": 0, "skill_desc": "",
        "experience_score": 0, "experience_pct": 0, "experience_desc": "",
        "location_score": 0, "location_pct": 0, "location_desc": "",
        "salary_score": 0, "salary_pct": 0, "salary_desc": "",
        "company_score": 0, "company_pct": 0, "company_desc": "",
        "total_score": 0,
    }
    
    missing_skills = []
    
    # 1. Role Match (35)
    opp_title = (opp.title or "").lower()
    if prefs and prefs.preferred_roles:
        matched_role = False
        for role in prefs.preferred_roles:
            if role.lower() in opp_title:
                components["role_score"] = 35
                components["role_pct"] = 100
                components["role_desc"] = f"✓ Exact match for {role}"
                matched_role = True
                break
        if not matched_role:
            # Check if any taxonomy family matches? Simplified to baseline
            components["role_score"] = 5
            components["role_pct"] = 14
            components["role_desc"] = "Different role family"
    else:
        components["role_score"] = 17 
        components["role_pct"] = 50
        components["role_desc"] = "No role preferences set"
        
    # 2. Skills Match (25)
    user_skills = normalize_skills_list(user_profile.extracted_skills) if user_profile and user_profile.extracted_skills else []
    
    req_skills_raw = []
    if opp.required_skills:
        req_skills_raw = [s.strip() for s in opp.required_skills.split(",")]
    if not req_skills_raw:
        req_skills_raw = extract_skills_from_text(opp.description)
        
    job_skills = normalize_skills_list(req_skills_raw)
    
    matched_skills = []
    
    if job_skills and user_skills:
        user_skills_set = set(user_skills)
        for js in job_skills:
            if js in user_skills_set:
                matched_skills.append(js)
            else:
                missing_skills.append(js)
                
        skill_ratio = len(matched_skills) / len(job_skills) if job_skills else 1
        components["skill_score"] = int(skill_ratio * 25)
        components["skill_pct"] = int(skill_ratio * 100)
        
        if matched_skills:
            components["skill_desc"] = f"✓ {', '.join(matched_skills[:3])}"
        else:
            components["skill_desc"] = "Missing core skills"
    else:
        components["skill_score"] = 10 
        components["skill_pct"] = 40
        components["skill_desc"] = "Not enough skill data"
        
    # 3. Experience Match (20)
    user_exp = 0 # Default to fresher
    req_exp = opp.experience_min or 0
    if req_exp <= 1:
        # Fresher friendly
        if req_exp <= user_exp + 1:
            components["experience_score"] = 20
            components["experience_pct"] = 100
            components["experience_desc"] = "✓ Entry-level / Fresher friendly"
        else:
            components["experience_score"] = 0
            components["experience_pct"] = 0
            components["experience_desc"] = f"Needs {req_exp} years"
    else:
        # If job needs > 1 year and user is fresher (0), penalize heavily
        components["experience_score"] = 0
        components["experience_pct"] = 0
        components["experience_desc"] = f"Needs {req_exp} years"
        
    # 4. Location Match (10)
    opp_loc = (opp.location or "").lower()
    is_remote_opp = "remote" in opp_loc or (opp.work_mode and "remote" in opp.work_mode.lower())
    
    if prefs and prefs.remote_preference == "Only Remote" and not is_remote_opp:
        components["location_score"] = 0
        components["location_pct"] = 0
        components["location_desc"] = "Not a remote role"
    elif prefs and prefs.remote_preference == "Only Remote" and is_remote_opp:
        components["location_score"] = 10
        components["location_pct"] = 100
        components["location_desc"] = "Remote opportunity"
    elif prefs and prefs.preferred_locations:
        matched_loc = False
        for loc in prefs.preferred_locations:
            if loc.lower() in opp_loc:
                components["location_score"] = 10
                components["location_pct"] = 100
                components["location_desc"] = f"✓ {loc}"
                matched_loc = True
                break
        if not matched_loc:
            components["location_score"] = 2
            components["location_pct"] = 20
            components["location_desc"] = "Outside preferred locations"
    else:
        components["location_score"] = 5 
        components["location_pct"] = 50
        components["location_desc"] = "Location preferences open"
        
    # 5. Salary Match (5)
    if prefs and prefs.minimum_salary:
        components["salary_score"] = 5
        components["salary_pct"] = 100
        components["salary_desc"] = "Within preferred range"
    else:
        components["salary_score"] = 5
        components["salary_pct"] = 100
        components["salary_desc"] = "No salary constraints"
        
    # 6. Company Preference (5)
    if prefs and prefs.preferred_companies:
        if any((c.lower() in (opp.company or "").lower()) for c in prefs.preferred_companies):
            components["company_score"] = 5
            components["company_pct"] = 100
            components["company_desc"] = "✓ Target company"
        else:
            components["company_score"] = 0
            components["company_pct"] = 0
            components["company_desc"] = "Not a target company"
    else:
        components["company_score"] = 2
        components["company_pct"] = 40
        components["company_desc"] = "No company preference"

    # Total Score Calculation
    total = sum([
        components["role_score"],
        components["skill_score"],
        components["experience_score"],
        components["location_score"],
        components["salary_score"],
        components["company_score"]
    ])
    
    # Hard Role Penalty
    if components["role_pct"] < 30:
        total = int(total * 0.5) # Penalty for irrelevant role
        
    components["total_score"] = total
    
    # Build detailed breakdown
    breakdown = [
        {
            "category": "Role Match",
            "percent": components["role_pct"],
            "description": components["role_desc"]
        },
        {
            "category": "Skills Match",
            "percent": components["skill_pct"],
            "description": components["skill_desc"]
        },
        {
            "category": "Experience",
            "percent": components["experience_pct"],
            "description": components["experience_desc"]
        },
        {
            "category": "Location",
            "percent": components["location_pct"],
            "description": components["location_desc"]
        },
        {
            "category": "Salary",
            "percent": components["salary_pct"],
            "description": components["salary_desc"]
        }
    ]
    
    # Phase 9.0 Wave 1: Deep Recommendation Diagnostics
    diagnostics = {
        "why_recommended": [],
        "why_not_recommended": []
    }
    
    if components["role_pct"] >= 80: diagnostics["why_recommended"].append("Strong role match")
    elif components["role_pct"] < 30: diagnostics["why_not_recommended"].append("Role misalignment")
    
    if components["skill_pct"] >= 75: diagnostics["why_recommended"].append("High skill overlap")
    elif components["skill_pct"] < 30: diagnostics["why_not_recommended"].append(f"Missing core skills ({len(missing_skills)})")
        
    if components["experience_pct"] == 100: diagnostics["why_recommended"].append("Perfect experience fit")
    elif components["experience_pct"] == 0: diagnostics["why_not_recommended"].append(components["experience_desc"])
        
    if components["location_pct"] == 100: diagnostics["why_recommended"].append("Location match")
    
    # Generate overall explanations if empty
    if not diagnostics["why_recommended"] and total >= 60:
        diagnostics["why_recommended"].append("Good overall profile match")
    if not diagnostics["why_not_recommended"] and total < 50:
        diagnostics["why_not_recommended"].append("Does not strongly match your preferences")
        
    return {
        "scores": components,
        "breakdown": breakdown,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills, # Return all missing skills for UI
        "probability": get_apply_probability(components["total_score"]),
        "diagnostics": diagnostics
    }

def resume_job_match(user_skills_raw: List[str], job_skills_raw: List[str]) -> Dict[str, Any]:
    """Matches resume skills to job skills directly."""
    user_skills = set(normalize_skills_list(user_skills_raw))
    job_skills = normalize_skills_list(job_skills_raw)
    
    if not job_skills:
        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": [],
            "recommended_skills": []
        }
        
    matched = [s for s in job_skills if s in user_skills]
    missing = [s for s in job_skills if s not in user_skills]
    
    pct = int((len(matched) / len(job_skills)) * 100)
    
    return {
        "match_percentage": pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommended_skills": missing[:3] # recommend the top 3 missing skills
    }

def get_skill_gap(target_role: str, user_skills_raw: List[str]) -> Dict[str, Any]:
    """Calculates career readiness for a target role."""
    # Mocking standard role requirements. In production, this might come from RoleSkillMap.
    ROLE_BENCHMARKS = {
        "data analyst": ["sql", "power_bi", "python", "excel", "tableau"],
        "data engineer": ["python", "sql", "spark", "airflow", "aws", "docker"],
        "business analyst": ["sql", "excel", "jira", "agile", "power_bi", "communication"],
        "software engineer": ["java", "python", "javascript", "react", "nodejs", "sql", "git"],
        "frontend developer": ["javascript", "react", "html", "css", "vue", "nextjs"],
        "backend developer": ["python", "nodejs", "java", "postgresql", "docker", "aws"]
    }
    
    req_skills = ROLE_BENCHMARKS.get(target_role.lower(), ["python", "sql", "javascript"]) # fallback
    req_skills = normalize_skills_list(req_skills)
    user_skills = set(normalize_skills_list(user_skills_raw))
    
    matched = [s for s in req_skills if s in user_skills]
    missing = [s for s in req_skills if s not in user_skills]
    
    readiness = int((len(matched) / len(req_skills)) * 100)
    
    # Estimate time: roughly 1 month per missing core skill
    estimated_months = len(missing) * 1
    
    return {
        "target_role": target_role.title(),
        "readiness_score": readiness,
        "missing_skills": missing,
        "recommended_skills": missing[:3],
        "estimated_months": estimated_months
    }

def get_profile_completeness(user_profile: models.ResumeProfile, prefs: models.UserPreference) -> Dict[str, Any]:
    """Calculates profile completeness percentage and missing items."""
    points = 0
    total_points = 5
    missing = []
    
    if user_profile and user_profile.uploaded_file:
        points += 1
    else:
        missing.append("Resume upload")
        
    if user_profile and user_profile.extracted_skills:
        points += 1
    else:
        missing.append("Add skills to profile")
        
    if prefs and prefs.preferred_roles:
        points += 1
    else:
        missing.append("Set preferred roles")
        
    if prefs and prefs.preferred_locations:
        points += 1
    else:
        missing.append("Set preferred locations")
        
    if prefs and prefs.remote_preference:
        points += 1
    else:
        missing.append("Set remote preference")
        
    return {
        "completeness_score": int((points / total_points) * 100),
        "missing_items": missing
    }
