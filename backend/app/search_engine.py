from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text
from typing import List, Dict, Any, Tuple, Optional
from app import models
from app.role_taxonomy import expand_role
from app.skill_taxonomy import get_roles_for_skill, get_skills_for_role

def detect_search_intent(query: str) -> dict:
    """
    Detects whether a query is a skill or a role, and extracts associated roles and skills.
    """
    q = query.lower().strip()
    
    skill_roles = get_roles_for_skill(q)
    if skill_roles:
        return {
            "type": "skill",
            "roles": skill_roles,
            "skills": [q],
            "original": q
        }
        
    # Check if query is a role or role family
    associated_skills = get_skills_for_role(q)
    return {
        "type": "role",
        "roles": [q],
        "skills": associated_skills,
        "original": q
    }

def get_base_active_query(db: Session, job_type: Optional[str] = None, location: Optional[str] = None):
    q = db.query(models.Opportunity).filter(
        models.Opportunity.data_origin == "LIVE_API",
        models.Opportunity.primary_source.notlike("%Careers%"),
        models.Opportunity.apply_url.notlike("%linkedin.com%"),
        models.Opportunity.apply_url.notlike("%?req_id=%"),
        models.Opportunity.apply_url.notlike("%?q=%"),
        models.Opportunity.apply_url.notlike("%?keyword=%"),
        or_(
            models.Opportunity.status == "Active",
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status.is_(None)
        ),
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.lifecycle_status.in_(["NEW", "ACTIVE"]),
            models.Opportunity.lifecycle_status.is_(None)
        ),
        or_(
            models.Opportunity.apply_url_status != "INVALID_LINK",
            models.Opportunity.apply_url_status.is_(None)
        )
    )

    if job_type and job_type != "All":
        q = q.filter(models.Opportunity.job_type.ilike(f"%{job_type.strip()}%"))

    if location and location != "All" and location.strip():
        loc = location.strip()
        q = q.filter(models.Opportunity.location.ilike(f"%{loc}%"))

    return q

def _search_by_roles_and_skills(
    db: Session,
    roles: List[str],
    skills: List[str],
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 100
) -> List[models.Opportunity]:
    """
    Intelligent helper: searches for jobs matching role names, companies, OR core role skills.
    """
    filters = []
    
    # 1. Role / Title / Company filter
    for role in (roles or []):
        r = role.strip()
        if r:
            filters.append(models.Opportunity.title.ilike(f"%{r}%"))
            filters.append(models.Opportunity.company.ilike(f"%{r}%"))
            
    # 2. Role Skills filter (matches required_skills and description)
    for skill in (skills or []):
        s = skill.strip()
        if s and len(s) >= 2:
            filters.append(models.Opportunity.required_skills.ilike(f"%{s}%"))
            filters.append(models.Opportunity.description.ilike(f"%{s}%"))
            
    if not filters:
        return []
    
    return get_base_active_query(db, job_type=job_type, location=location).filter(or_(*filters)).order_by(
        models.Opportunity.posted_date.desc().nulls_last(),
        models.Opportunity.id.desc()
    ).limit(limit).all()

def search_opportunities(
    db: Session,
    query: Optional[str] = None,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 500
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes a Multi-Level Smart Search:
    Level 1 (Exact): Exact role/company/synonym matches + primary role skills matching.
    Level 2 (Related): Expanded family roles and secondary associated skills.
    Level 3 (Fallback): Keyword match across description/skills.
    
    Returns a list of dicts: {"opportunity": Opp, "search_level": 1|2|3}
    and metadata about the search.
    """
    base_q = get_base_active_query(db, job_type=job_type, location=location)
    total_db_active = base_q.count()

    clean_query = (query or "").strip()

    if not clean_query:
        jobs = base_q.order_by(
            models.Opportunity.posted_date.desc().nulls_last(),
            models.Opportunity.id.desc()
        ).limit(limit).all()
        return [{"opportunity": j, "search_level": 1} for j in jobs], {
            "exact": len(jobs),
            "related": 0,
            "total_db_active": total_db_active,
            "query": ""
        }
        
    intent = detect_search_intent(clean_query)
    results = []
    seen_ids = set()
    
    # ---------------- LEVEL 1 (Exact Role + Skills) ----------------
    level_1_roles = intent["roles"]
    level_1_skills = intent.get("skills", [])
    
    l1_jobs = _search_by_roles_and_skills(
        db,
        roles=level_1_roles,
        skills=level_1_skills,
        job_type=job_type,
        location=location,
        limit=limit
    )
    
    for j in l1_jobs:
        if j.id not in seen_ids:
            results.append({"opportunity": j, "search_level": 1})
            seen_ids.add(j.id)
            
    exact_count = len(results)
    
    # ---------------- LEVEL 2 (Related Role Family & Skill Expansion) ----------------
    if len(results) < limit:
        level_2_roles = set()
        level_2_skills = set()
        
        for r in level_1_roles:
            expanded = expand_role(r)
            level_2_roles.update(expanded)
            for exp_r in expanded:
                level_2_skills.update(get_skills_for_role(exp_r))
            
        level_2_roles = list(level_2_roles - set(level_1_roles))
        level_2_skills = list(level_2_skills - set(level_1_skills))
        
        l2_jobs = _search_by_roles_and_skills(
            db,
            roles=level_2_roles,
            skills=level_2_skills,
            job_type=job_type,
            location=location,
            limit=(limit - len(results))
        )
        for j in l2_jobs:
            if j.id not in seen_ids:
                results.append({"opportunity": j, "search_level": 2})
                seen_ids.add(j.id)
                
    related_count = len(results) - exact_count
                
    # ---------------- LEVEL 3 (Fallback) ----------------
    if len(results) < limit:
        fallback_query = base_q.filter(
            or_(
                models.Opportunity.description.ilike(f"%{clean_query}%"),
                models.Opportunity.required_skills.ilike(f"%{clean_query}%"),
                models.Opportunity.title.ilike(f"%{clean_query}%"),
                models.Opportunity.company.ilike(f"%{clean_query}%")
            ),
            ~models.Opportunity.id.in_([id for id in seen_ids] if seen_ids else [0])
        ).order_by(
            models.Opportunity.posted_date.desc().nulls_last(),
            models.Opportunity.id.desc()
        ).limit(limit - len(results))
        
        l3_jobs = fallback_query.all()
        for j in l3_jobs:
            if j.id not in seen_ids:
                results.append({"opportunity": j, "search_level": 3})
                seen_ids.add(j.id)
                
    metadata = {
        "intent_type": intent["type"],
        "exact_matches": exact_count,
        "related_matches": related_count,
        "query": clean_query,
        "role_skills_checked": level_1_skills[:5],
        "total_db_active": total_db_active
    }
    
    return results, metadata
