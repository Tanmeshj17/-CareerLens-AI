from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Career Profile"])

@router.get("/career", response_model=schemas.UserCareerProfile)
def get_career_profile(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Career profile not found")
    return profile

@router.post("/career", response_model=schemas.UserCareerProfile)
def create_career_profile(profile_data: schemas.UserCareerProfileCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Career profile already exists. Use PUT to update.")
    
    new_profile = models.UserCareerProfile(**profile_data.dict(), user_id=current_user.id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@router.put("/career", response_model=schemas.UserCareerProfile)
def update_career_profile(profile_data: schemas.UserCareerProfileUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Career profile not found")
    
    update_data = profile_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/skills", response_model=List[schemas.UserSkillProfile])
def get_skills(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.UserSkillProfile).filter(models.UserSkillProfile.user_id == current_user.id).all()

@router.post("/skills", response_model=schemas.UserSkillProfile)
def add_skill(skill_data: schemas.UserSkillProfileCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    valid_levels = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
    if skill_data.proficiency_level and skill_data.proficiency_level.upper() not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid proficiency level. Must be one of {valid_levels}")
        
    existing = db.query(models.UserSkillProfile).filter(
        models.UserSkillProfile.user_id == current_user.id,
        models.UserSkillProfile.skill_name.ilike(skill_data.skill_name)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Skill already exists for this user")
        
    new_skill = models.UserSkillProfile(**skill_data.dict(), user_id=current_user.id)
    new_skill.proficiency_level = new_skill.proficiency_level.upper() if new_skill.proficiency_level else "BEGINNER"
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.put("/skills/{skill_id}", response_model=schemas.UserSkillProfile)
def update_skill(skill_id: int, proficiency_level: str, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    valid_levels = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]
    if proficiency_level.upper() not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid proficiency level. Must be one of {valid_levels}")
        
    skill = db.query(models.UserSkillProfile).filter(models.UserSkillProfile.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    # IDOR Protection
    if skill.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this skill")
        
    skill.proficiency_level = proficiency_level.upper()
    db.commit()
    db.refresh(skill)
    return skill

@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = db.query(models.UserSkillProfile).filter(models.UserSkillProfile.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    # IDOR Protection
    if skill.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this skill")
        
    db.delete(skill)
    db.commit()
    return {"detail": "Skill deleted"}

@router.get("/completeness")
def get_profile_completeness(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    points = 0
    total = 100
    
    # 1. Base User info (name, etc.) = 20 points
    points += 20
    
    # 2. Career Profile = 30 points
    career = db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == current_user.id).first()
    if career:
        if career.target_role: points += 10
        if career.experience_level: points += 10
        if career.location or career.education or career.current_role: points += 10
        
    # 3. Skills = 20 points
    skills_count = db.query(models.UserSkillProfile).filter(models.UserSkillProfile.user_id == current_user.id).count()
    if skills_count > 0:
        points += min(20, skills_count * 4) # 4 points per skill, max 20
        
    # 4. Resume Profile = 30 points
    resume = db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == current_user.id).first()
    if resume:
        points += 15
        if resume.extracted_skills or resume.extracted_experience:
            points += 15
            
    return {
        "completeness_percentage": points,
        "missing_items": _get_missing_items(career, skills_count, resume)
    }

def _get_missing_items(career, skills_count, resume):
    missing = []
    if not career:
        missing.append("Career Profile (Target Role, Experience)")
    else:
        if not career.target_role:
            missing.append("Target Role")
        if not career.experience_level:
            missing.append("Experience Level")
            
    if skills_count == 0:
        missing.append("Skills (Add at least 5 skills)")
    elif skills_count < 5:
        missing.append(f"More Skills (Have {skills_count}, recommend 5+)")
        
    if not resume:
        missing.append("Resume parsing")
        
    return missing
