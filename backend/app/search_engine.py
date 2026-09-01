from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, not_, func, text
from typing import List, Dict, Any, Tuple, Optional
from app import models
from app.role_taxonomy import expand_role
from app.skill_taxonomy import get_roles_for_skill, get_skills_for_role

# ─── Location Synonyms Map ──────────────────────────────────────────────────
LOCATION_SYNONYMS = {
    "bangalore": ["bangalore", "bengaluru", "bengalore", "blr", "karnataka"],
    "bengaluru": ["bengaluru", "bangalore", "bengalore", "blr", "karnataka"],
    "delhi": ["delhi", "new delhi", "ncr", "noida", "gurgaon", "gurugram", "ghaziabad", "faridabad"],
    "new delhi": ["new delhi", "delhi", "ncr", "noida", "gurgaon", "gurugram"],
    "ncr": ["ncr", "delhi", "new delhi", "noida", "gurgaon", "gurugram"],
    "noida": ["noida", "greater noida", "delhi", "ncr", "uttar pradesh", "up"],
    "gurgaon": ["gurgaon", "gurugram", "haryana", "ncr", "delhi"],
    "gurugram": ["gurugram", "gurgaon", "haryana", "ncr", "delhi"],
    "mumbai": ["mumbai", "bombay", "navi mumbai", "thane", "maharashtra"],
    "bombay": ["mumbai", "bombay", "navi mumbai", "thane"],
    "pune": ["pune", "hinjewadi", "magarpatta", "maharashtra"],
    "hyderabad": ["hyderabad", "secunderabad", "cyberabad", "telangana", "hyd"],
    "chennai": ["chennai", "madras", "tamil nadu", "tn"],
    "kolkata": ["kolkata", "calcutta", "west bengal", "wb"],
    "ahmedabad": ["ahmedabad", "gandhinagar", "gujarat"],
    "jaipur": ["jaipur", "rajasthan"],
    "chandigarh": ["chandigarh", "mohali", "panchkula", "punjab"],
    "remote": ["remote", "work from home", "wfh", "anywhere", "telecommute", "virtual", "flexible"],
    "wfh": ["remote", "work from home", "wfh", "anywhere", "telecommute"],
    "india": ["india", "in", "bengaluru", "bangalore", "hyderabad", "delhi", "mumbai", "pune", "chennai", "noida", "gurgaon"],
    "usa": ["united states", "usa", "us", "san francisco", "new york", "seattle", "austin", "california", "texas", "chicago"],
    "united states": ["united states", "usa", "us", "san francisco", "new york", "seattle", "austin"],
    "uk": ["united kingdom", "uk", "london", "manchester", "england"],
    "canada": ["canada", "toronto", "vancouver", "waterloo", "ontario", "montreal"],
    "germany": ["germany", "berlin", "munich", "frankfurt", "deutschland"]
}

def build_job_type_filter(job_type_str: Optional[str]):
    """
    Builds a flexible SQLAlchemy filter for job types, covering all common terminology variants.
    """
    if not job_type_str or job_type_str.strip().lower() in ["all", "all types", "any"]:
        return None
    
    jt = job_type_str.strip().lower()
    
    if any(k in jt for k in ["full-time", "full time", "fulltime", "full_time", "permanent", "regular"]):
        return or_(
            models.Opportunity.job_type.ilike("%full%"),
            models.Opportunity.job_type.ilike("%permanent%"),
            models.Opportunity.job_type.ilike("%regular%"),
            models.Opportunity.job_type.ilike("%experienced%"),
            models.Opportunity.job_type.ilike("%direct%"),
            and_(
                models.Opportunity.job_type.isnot(None),
                ~models.Opportunity.job_type.ilike("%intern%"),
                ~models.Opportunity.job_type.ilike("%part%"),
                ~models.Opportunity.job_type.ilike("%contract%"),
                ~models.Opportunity.job_type.ilike("%apprentice%"),
                ~models.Opportunity.job_type.ilike("%trainee%")
            )
        )
    elif any(k in jt for k in ["intern", "internship", "summer", "co-op", "apprentice", "trainee"]):
        return or_(
            models.Opportunity.job_type.ilike("%intern%"),
            models.Opportunity.job_type.ilike("%trainee%"),
            models.Opportunity.job_type.ilike("%apprentice%"),
            models.Opportunity.job_type.ilike("%co-op%"),
            models.Opportunity.job_type.ilike("%fellow%"),
            models.Opportunity.title.ilike("%intern%"),
            models.Opportunity.title.ilike("%trainee%"),
            models.Opportunity.title.ilike("%apprentice%")
        )
    elif any(k in jt for k in ["part-time", "part time", "parttime", "hourly"]):
        return or_(
            models.Opportunity.job_type.ilike("%part%"),
            models.Opportunity.job_type.ilike("%hourly%")
        )
    elif any(k in jt for k in ["contract", "contractor", "freelance", "temp", "temporary"]):
        return or_(
            models.Opportunity.job_type.ilike("%contract%"),
            models.Opportunity.job_type.ilike("%freelance%"),
            models.Opportunity.job_type.ilike("%temp%")
        )
    else:
        return models.Opportunity.job_type.ilike(f"%{jt}%")

def build_location_filter(location_str: Optional[str]):
    """
    Builds a flexible location filter expanding city and country synonyms.
    """
    if not location_str or location_str.strip().lower() in ["all", "any"]:
        return None
        
    loc = location_str.strip().lower()
    
    # Check for synonyms
    synonyms = LOCATION_SYNONYMS.get(loc, [loc])
    
    loc_conditions = [models.Opportunity.location.ilike(f"%{s}%") for s in synonyms]
    
    if loc in ["remote", "wfh", "work from home", "anywhere"]:
        loc_conditions.append(models.Opportunity.is_remote == True)
        loc_conditions.append(models.Opportunity.location.ilike("%remote%"))
        loc_conditions.append(models.Opportunity.location.ilike("%wfh%"))
        
    return or_(*loc_conditions)

def get_base_active_query(db: Session, job_type: Optional[str] = None, location: Optional[str] = None):
    """
    Returns base query of active, valid opportunities with direct application links.
    """
    q = db.query(models.Opportunity).filter(
        or_(
            models.Opportunity.data_origin == "LIVE_API",
            models.Opportunity.data_origin == "LIVE_SCRAPE",
            models.Opportunity.data_origin == "CURATED_FALLBACK",
            models.Opportunity.data_origin.is_(None)
        ),
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "Active",
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status.is_(None)
        ),
        or_(
            models.Opportunity.apply_url_status != "INVALID_LINK",
            models.Opportunity.apply_url_status.is_(None)
        )
    )

    # Job Type Filter
    jt_filter = build_job_type_filter(job_type)
    if jt_filter is not None:
        q = q.filter(jt_filter)

    # Location Filter
    loc_filter = build_location_filter(location)
    if loc_filter is not None:
        q = q.filter(loc_filter)

    return q

def detect_search_intent(query: str) -> dict:
    """
    Detects whether a query contains a skill, a role, or a company.
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

def _build_multi_token_filter(clean_query: str):
    """
    Handles multi-word searches (e.g. 'Google SDE', 'Amazon Frontend', 'Python Intern').
    Every distinct word must match at least one relevant column.
    """
    words = [w.strip() for w in clean_query.split() if len(w.strip()) >= 2]
    if not words:
        return or_(
            models.Opportunity.title.ilike(f"%{clean_query}%"),
            models.Opportunity.company.ilike(f"%{clean_query}%")
        )
        
    # For each word, require it to match title OR company OR skills OR location OR description
    word_filters = []
    for word in words:
        # Check location synonym expansion for the word if applicable
        loc_syns = LOCATION_SYNONYMS.get(word.lower(), [])
        word_loc_cond = [models.Opportunity.location.ilike(f"%{s}%") for s in loc_syns] if loc_syns else []
        
        # Check if word is 'intern' or 'internship'
        type_cond = []
        if word.lower() in ["intern", "internship"]:
            type_cond.append(models.Opportunity.job_type.ilike("%intern%"))
        elif word.lower() in ["remote", "wfh"]:
            type_cond.append(models.Opportunity.is_remote == True)
            type_cond.append(models.Opportunity.location.ilike("%remote%"))

        field_matches = [
            models.Opportunity.title.ilike(f"%{word}%"),
            models.Opportunity.company.ilike(f"%{word}%"),
            models.Opportunity.required_skills.ilike(f"%{word}%"),
            models.Opportunity.location.ilike(f"%{word}%"),
            models.Opportunity.description.ilike(f"%{word}%"),
            *word_loc_cond,
            *type_cond
        ]
        word_filters.append(or_(*field_matches))
        
    # All words must be satisfied (AND of ORs)
    return and_(*word_filters)

def search_opportunities(
    db: Session,
    query: Optional[str] = None,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 500
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes a Multi-Level Smart Search:
    Level 1 (Exact):
      - Multi-token matching (Company + Role + Location)
      - Exact role title / company / role-skill match
    Level 2 (Related):
      - Expanded role family synonyms and associated domain skills
    Level 3 (Fallback):
      - Substring / keyword match across descriptions & required skills
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
    
    # ---------------- LEVEL 1 (Exact / Multi-Token / Role + Company) ----------------
    # 1. Multi-token / Phrase match
    multi_token_filter = _build_multi_token_filter(clean_query)
    l1_token_jobs = base_q.filter(multi_token_filter).order_by(
        models.Opportunity.posted_date.desc().nulls_last(),
        models.Opportunity.id.desc()
    ).limit(limit).all()
    
    for j in l1_token_jobs:
        if j.id not in seen_ids:
            results.append({"opportunity": j, "search_level": 1})
            seen_ids.add(j.id)

    # 2. Add role / skill matches from taxonomy
    level_1_roles = intent.get("roles", [])
    level_1_skills = intent.get("skills", [])
    
    role_skill_filters = []
    for r in level_1_roles:
        if r and len(r) >= 2:
            role_skill_filters.append(models.Opportunity.title.ilike(f"%{r}%"))
            role_skill_filters.append(models.Opportunity.company.ilike(f"%{r}%"))
    for s in level_1_skills:
        if s and len(s) >= 2:
            role_skill_filters.append(models.Opportunity.required_skills.ilike(f"%{s}%"))
            
    if role_skill_filters and len(results) < limit:
        l1_role_jobs = base_q.filter(
            or_(*role_skill_filters),
            ~models.Opportunity.id.in_(list(seen_ids) if seen_ids else [0])
        ).order_by(
            models.Opportunity.posted_date.desc().nulls_last(),
            models.Opportunity.id.desc()
        ).limit(limit - len(results)).all()
        
        for j in l1_role_jobs:
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
        
        l2_filters = []
        for r in level_2_roles:
            if r and len(r) >= 2:
                l2_filters.append(models.Opportunity.title.ilike(f"%{r}%"))
        for s in level_2_skills:
            if s and len(s) >= 2:
                l2_filters.append(models.Opportunity.required_skills.ilike(f"%{s}%"))
                
        if l2_filters:
            l2_jobs = base_q.filter(
                or_(*l2_filters),
                ~models.Opportunity.id.in_(list(seen_ids) if seen_ids else [0])
            ).order_by(
                models.Opportunity.posted_date.desc().nulls_last(),
                models.Opportunity.id.desc()
            ).limit(limit - len(results)).all()
            
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
            ~models.Opportunity.id.in_(list(seen_ids) if seen_ids else [0])
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

