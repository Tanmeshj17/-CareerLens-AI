from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/api/skills", tags=["Skills"])

@router.get("/gap-analysis", response_model=schemas.SkillGapAnalysisResponse)
def get_skill_gap_analysis(
    target_role: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Fetch Role Requirements
    role_skills = db.query(models.RoleSkillMap).filter(
        models.RoleSkillMap.role.ilike(target_role)
    ).all()
    
    if not role_skills:
        # Unknown roles gracefully handled: zero requirements, zero matches
        return {
            "target_role": target_role,
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "partial_skills": [],
            "coverage_percentage": 0.0,
            "skill_gap_count": 0
        }
        
    required_skills_db = [rs for rs in role_skills if rs.importance == "Required"]
    if not required_skills_db:
        # Fallback if no 'Required' specifically, use all
        required_skills_db = role_skills
        
    required_names = [rs.skill.lower() for rs in required_skills_db]
    original_names = {rs.skill.lower(): rs.skill for rs in required_skills_db}
    
    # 2. Fetch User Skills
    user_skills_db = db.query(models.UserSkillProfile).filter(
        models.UserSkillProfile.user_id == current_user.id
    ).all()
    
    # Map user skills to their proficiency, case insensitive
    user_skill_map = {us.skill_name.lower(): us.proficiency_level for us in user_skills_db}
    
    matched = []
    missing = []
    partial = []
    
    for req_skill_lower in required_names:
        orig_name = original_names[req_skill_lower]
        if req_skill_lower in user_skill_map:
            prof = user_skill_map[req_skill_lower]
            # Logic: If role requires this (it's in required_names), and proficiency is BEGINNER, it's partial.
            if prof == "BEGINNER":
                partial.append(orig_name)
            else:
                matched.append(orig_name)
        else:
            missing.append(orig_name)
            
    total_required = len(required_names)
    coverage = 0.0
    if total_required > 0:
        # Let's say matched = 1.0, partial = 0.5
        coverage = ((len(matched) * 1.0) + (len(partial) * 0.5)) / total_required * 100.0
        
    return {
        "target_role": target_role,
        "required_skills": list(original_names.values()),
        "matched_skills": matched,
        "missing_skills": missing,
        "partial_skills": partial,
        "coverage_percentage": round(coverage, 2),
        "skill_gap_count": len(missing) + len(partial)
    }
