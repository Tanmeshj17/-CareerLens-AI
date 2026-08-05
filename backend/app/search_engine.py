from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text
from typing import List, Dict, Any, Tuple
from app import models
from app.role_taxonomy import expand_role
from app.skill_taxonomy import get_roles_for_skill

def detect_search_intent(query: str) -> dict:
    """Detects whether a query is a skill or a role."""
    q = query.lower().strip()
    
    skill_roles = get_roles_for_skill(q)
    if skill_roles:
        return {"type": "skill", "roles": skill_roles, "original": q}
        
    return {"type": "role", "roles": [q], "original": q}

def get_base_active_query(db: Session):
    return db.query(models.Opportunity).filter(
        models.Opportunity.status == "Active", 
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.lifecycle_status.in_(["NEW", "ACTIVE"]),
            models.Opportunity.lifecycle_status.is_(None)  # include seeded/legacy rows with no lifecycle_status
        )
    )

def _search_by_roles(db: Session, roles: List[str], limit: int = 50) -> List[models.Opportunity]:
    """Helper to search for specific roles."""
    if not roles:
        return []
    filters = []
    for role in roles:
        filters.append(models.Opportunity.title.ilike(f"%{role}%"))
    
    return get_base_active_query(db).filter(or_(*filters)).order_by(models.Opportunity.confidence_score.desc().nulls_last()).limit(limit).all()

def search_opportunities(db: Session, query: str, limit: int = 20) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Executes a Multi-Level Search:
    Level 1 (Exact): Exact role/synonym matches, or skill intent matched roles.
    Level 2 (Related): Expanded family roles (if Level 1 < limit).
    Level 3 (Fallback): Other related opportunities (if still < limit).
    
    Returns a list of dicts: {"opportunity": Opp, "search_level": 1|2|3}
    and metadata about the search.
    """
    if not query:
        # No query, just return top confident jobs
        jobs = get_base_active_query(db).order_by(models.Opportunity.confidence_score.desc().nulls_last()).limit(limit).all()
        return [{"opportunity": j, "search_level": 1} for j in jobs], {"exact": len(jobs), "related": 0}
        
    intent = detect_search_intent(query)
    results = []
    seen_ids = set()
    
    # ---------------- LEVEL 1 (Exact) ----------------
    level_1_roles = intent["roles"]
    l1_jobs = _search_by_roles(db, level_1_roles, limit=limit)
    
    for j in l1_jobs:
        if j.id not in seen_ids:
            results.append({"opportunity": j, "search_level": 1})
            seen_ids.add(j.id)
            
    exact_count = len(results)
    
    # ---------------- LEVEL 2 (Related) ----------------
    if len(results) < limit:
        # Expand all level 1 roles to their families
        level_2_roles = set()
        for r in level_1_roles:
            level_2_roles.update(expand_role(r))
            
        # Remove level 1 roles from level 2 to avoid redundant querying
        level_2_roles = list(level_2_roles - set(level_1_roles))
        
        l2_jobs = _search_by_roles(db, level_2_roles, limit=(limit - len(results)))
        for j in l2_jobs:
            if j.id not in seen_ids:
                results.append({"opportunity": j, "search_level": 2})
                seen_ids.add(j.id)
                
    related_count = len(results) - exact_count
                
    # ---------------- LEVEL 3 (Fallback) ----------------
    if len(results) < limit:
        # Fallback to description matching or generic active jobs
        fallback_query = get_base_active_query(db).filter(
            or_(
                models.Opportunity.description.ilike(f"%{query}%"),
                models.Opportunity.required_skills.ilike(f"%{query}%")
            ),
            ~models.Opportunity.id.in_([id for id in seen_ids] if seen_ids else [0])
        ).order_by(models.Opportunity.confidence_score.desc().nulls_last()).limit(limit - len(results))
        
        l3_jobs = fallback_query.all()
        for j in l3_jobs:
            if j.id not in seen_ids:
                results.append({"opportunity": j, "search_level": 3})
                seen_ids.add(j.id)
                
    related_count += (len(results) - exact_count - related_count)
    
    metadata = {
        "intent_type": intent["type"],
        "exact_matches": exact_count,
        "related_matches": related_count,
        "query": query
    }
    
    return results, metadata
