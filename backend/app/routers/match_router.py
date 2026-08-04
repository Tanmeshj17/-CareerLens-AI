from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app import models, schemas, auth, database, match_engine, rank_engine, search_engine

router = APIRouter(prefix="/api", tags=["Personalization & Matching"])

@router.get("/opportunities/recommended")
def get_recommended_opportunities(
    search: Optional[str] = None,
    type: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0, 
    limit: int = 20, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Returns personalized opportunity feed sorted by Final Score, with search filtering.
    """
    user_profile = db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == current_user.id).first()
    prefs = db.query(models.UserPreference).filter(models.UserPreference.user_id == current_user.id).first()
    
    # Use cache to avoid N+1 and repeated scoring
    from app.cache import get_or_compute
    
    def _compute():
        # Fetch Collector Health map for Wave 4
        collector_health_map = {
            h.collector_name: (h.collector_score or 50.0) 
            for h in db.query(models.CollectorHealth).all()
        }

        # Phase 8.65: Multi-level Search Filtering
        search_results, search_metadata = search_engine.search_opportunities(db, search, limit=100)
        
        scored = []
        for result in search_results:
            opp = result["opportunity"]
            search_level = result["search_level"]
            
            match_data = match_engine.generate_match_score(user_profile, prefs, opp)
            
            health_score = collector_health_map.get(opp.collected_by, 50.0) if opp.collected_by else 50.0

            final_score = rank_engine.compute_personalized_rank(
                opp=opp,
                match_score=match_data["scores"]["total_score"],
                freshness_score=0,  # V2: freshness folded into confidence_score
                company_score=match_data["scores"]["company_score"],
                collector_health_score=health_score
            )
            
            # Phase 8.65: Boost exact matches (Level 1) over fallback
            if search_level == 1:
                final_score += 1000
            elif search_level == 2:
                final_score += 500
                
            scored.append({
                "opportunity": {
                    "id": opp.id,
                    "title": opp.title,
                    "company": opp.company,
                    "location": opp.location,
                    "job_type": opp.job_type,
                    "salary_range": opp.salary_range,
                    "apply_url": opp.apply_url,
                    "primary_source": opp.primary_source,
                    "trust_score": opp.trust_score,
                    "confidence_score": opp.confidence_score,
                    "completeness_score": opp.completeness_score,
                    "lifecycle_status": opp.lifecycle_status,
                    "apply_url_status": opp.apply_url_status,
                    "posted_date": opp.posted_date.isoformat() if opp.posted_date else None,
                    "required_skills": opp.required_skills
                },
                "final_score": final_score,
                "match_data": match_data,
                "search_level": search_level
            })
            
        scored.sort(key=lambda x: x["final_score"], reverse=True)
        return scored, search_metadata

    safe_search = (search or "").lower().strip()
    cache_key = f"user_recs_{current_user.id}_{safe_search}_{type}_{location}"
    
    # get_or_compute doesn't support returning tuples directly if we expect just the list, 
    # but we can cache the combined dict.
    def wrapper():
        s, m = _compute()
        return {"items": s, "metadata": m}
        
    cached_data = get_or_compute(cache_key, wrapper, ttl_seconds=1800)
    scored_opportunities = cached_data["items"]
    search_metadata = cached_data["metadata"]
    
    # Paginate
    paginated = scored_opportunities[skip : skip + limit]
    
    # Optimize N+1 queries by fetching existing scores in one go
    opp_ids = [item["opportunity"]["id"] if isinstance(item["opportunity"], dict) else item["opportunity"].id for item in paginated]
    existing_scores = db.query(models.JobMatchScore).filter(
        models.JobMatchScore.user_id == current_user.id,
        models.JobMatchScore.opportunity_id.in_(opp_ids)
    ).all()
    score_map = {s.opportunity_id: s for s in existing_scores}

    for item in paginated:
        opp = item["opportunity"]
        md = item["match_data"]
        scores = md["scores"]
        
        opp_id = opp["id"] if isinstance(opp, dict) else opp.id
        
        db_score = score_map.get(opp_id)
        
        if not db_score:
            db_score = models.JobMatchScore(
                user_id=current_user.id,
                opportunity_id=opp_id
            )
            db.add(db_score)
            
        db_score.match_score = scores["total_score"]
        db_score.skill_score = scores["skill_score"]
        db_score.role_score = scores["role_score"]
        db_score.location_score = scores["location_score"]
        db_score.freshness_score = 0  # V2: removed from match engine
        db_score.company_score = scores["company_score"]
        db_score.salary_score = scores["salary_score"]
        db_score.matching_skills = md["matched_skills"]
        db_score.missing_skills = md["missing_skills"]
        db_score.match_level = md.get("probability", "Low Match")
        db_score.explanation = md["breakdown"]
        db_score.created_at = datetime.utcnow()
        
    db.commit()
    
    return {
        "total": len(scored_opportunities),
        "items": paginated,
        "search_metadata": search_metadata
    }

from pydantic import BaseModel
class SearchAnalyticsCreate(BaseModel):
    query: str
    clicked_job_id: Optional[int] = None
    result_count: int
    click_position: Optional[int] = None
    response_time_ms: Optional[float] = None

@router.post("/search/analytics")
def log_search_analytics(
    data: SearchAnalyticsCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Records search behavior for Search Intelligence phase."""
    record = models.SearchAnalytics(
        user_id=current_user.id,
        query=data.query,
        clicked_job_id=data.clicked_job_id,
        result_count=data.result_count,
        click_position=data.click_position,
        is_zero_results=(data.result_count == 0),
        response_time_ms=data.response_time_ms
    )
    db.add(record)
    db.commit()
    return {"status": "recorded"}

@router.get("/search/suggestions")
def get_search_suggestions(q: str = ""):
    """Rich autocomplete suggestions."""
    q = q.lower().strip()
    if len(q) < 2:
        return {"suggestions": {"roles": [], "skills": [], "companies": []}}
        
    # Mocking rich autocomplete as requested
    roles = []
    from app.role_taxonomy import ROLE_TAXONOMY
    for family, items in ROLE_TAXONOMY.items():
        for item in items:
            if q in item.lower():
                roles.append(item.title())
                
    skills = []
    from app.skill_taxonomy import SKILL_TO_ROLE_MAPPING
    for skill in SKILL_TO_ROLE_MAPPING.keys():
        if q in skill.lower():
            skills.append(skill.title())
            
    return {
        "suggestions": {
            "roles": list(set(roles))[:5],
            "skills": list(set(skills))[:5],
            "companies": ["TCS", "Infosys", "Deloitte"] if "data" not in q else ["Google", "Amazon", "Meta"]
        }
    }

@router.get("/match/job/{opportunity_id}")
def get_job_match(
    opportunity_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Gets explanation and match score for a specific job."""
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    user_profile = db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == current_user.id).first()
    prefs = db.query(models.UserPreference).filter(models.UserPreference.user_id == current_user.id).first()
    
    match_data = match_engine.generate_match_score(user_profile, prefs, opp)
    
    return {
        "opportunity_id": opp.id,
        "match_score": match_data["scores"]["total_score"],
        "probability": match_data["probability"],
        "explanation": match_data["explanation"],
        "missing_skills": match_data["missing_skills"]
    }

@router.get("/readiness")
def get_all_readiness(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Gets career readiness dashboard cards."""
    # Phase 10.2.5: Deterministic Career Readiness Snapshot
    career_profile = db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == current_user.id).first()
    target_role = career_profile.target_role if career_profile and career_profile.target_role else "Software Engineer"
    
    # 1. Skill Coverage Score
    role_skills = db.query(models.RoleSkillMap).filter(models.RoleSkillMap.role.ilike(target_role)).all()
    required_skills = [rs.skill.lower() for rs in role_skills if rs.importance == "Required"]
    if not required_skills and role_skills:
        required_skills = [rs.skill.lower() for rs in role_skills]
        
    user_skills = db.query(models.UserSkillProfile).filter(models.UserSkillProfile.user_id == current_user.id).all()
    user_skill_names = {s.skill_name.lower(): s.proficiency_level for s in user_skills}
    
    matched = []
    missing = []
    partial = []
    for req in required_skills:
        if req in user_skill_names:
            prof = user_skill_names[req]
            if prof == "BEGINNER":
                partial.append(req)
            else:
                matched.append(req)
        else:
            missing.append(req)
            
    if not required_skills:
        skill_coverage_score = 0
    else:
        skill_coverage_score = int(((len(matched) + 0.5 * len(partial)) / len(required_skills)) * 100)
        
    # 2. Resume Score
    resume = db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == current_user.id).order_by(models.ResumeProfile.created_at.desc()).first()
    resume_score = resume.ats_score if resume and resume.ats_score else 0
    
    # 3. Experience Score (just based on having it filled out for now)
    experience_score = 100 if career_profile and career_profile.experience_level else 0
    
    # Calculate total readiness deterministically
    readiness_score = int((skill_coverage_score * 0.5) + (resume_score * 0.4) + (experience_score * 0.1))
    
    # Snapshot to DB (1 per day to prevent duplicate state, historical immutable)
    import datetime
    today = datetime.datetime.utcnow().date()
    # Check for existing snapshot today
    existing_snapshot = db.query(models.CareerReadinessSnapshot).filter(
        models.CareerReadinessSnapshot.user_id == current_user.id
    ).order_by(models.CareerReadinessSnapshot.calculated_at.desc()).first()
    
    if existing_snapshot and existing_snapshot.calculated_at.date() == today:
        existing_snapshot.target_role = target_role
        existing_snapshot.readiness_score = readiness_score
        existing_snapshot.skill_coverage_score = skill_coverage_score
        existing_snapshot.experience_score = experience_score
        existing_snapshot.resume_score = resume_score
    else:
        snapshot = models.CareerReadinessSnapshot(
            user_id=current_user.id,
            target_role=target_role,
            readiness_score=readiness_score,
            skill_coverage_score=skill_coverage_score,
            experience_score=experience_score,
            resume_score=resume_score
        )
        db.add(snapshot)
    
    db.commit()
    
    # Format for the UI
    res = [{
        "target_role": target_role,
        "readiness_score": readiness_score,
        "recommended_skills": [s.title() for s in missing[:5]],
        "components": {
            "skill_coverage": skill_coverage_score,
            "resume_score": resume_score,
            "experience_score": experience_score
        }
    }]
    
    return {"readiness_cards": res}



@router.post("/profile/preferences")
def update_preferences(
    prefs_data: dict,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Updates user preferences (used for match scoring)."""
    prefs = db.query(models.UserPreference).filter(models.UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = models.UserPreference(user_id=current_user.id)
        db.add(prefs)
        
    if "preferred_roles" in prefs_data: prefs.preferred_roles = prefs_data["preferred_roles"]
    if "preferred_locations" in prefs_data: prefs.preferred_locations = prefs_data["preferred_locations"]
    if "preferred_job_type" in prefs_data: prefs.preferred_job_type = prefs_data["preferred_job_type"]
    if "remote_preference" in prefs_data: prefs.remote_preference = prefs_data["remote_preference"]
    if "minimum_salary" in prefs_data: prefs.minimum_salary = prefs_data["minimum_salary"]
    if "preferred_companies" in prefs_data: prefs.preferred_companies = prefs_data["preferred_companies"]
    
    db.commit()
    return {"status": "success", "message": "Preferences updated"}
