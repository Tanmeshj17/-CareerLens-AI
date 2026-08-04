from datetime import datetime, timedelta

def calculate_completeness_score(opp) -> int:
    """
    Phase 8.6: Opportunity Completeness Score
    Title 10, Company 10, Location 10, Description 15, Skills 15, 
    Salary 10, Apply Link 20, Freshness 10, Employment Type 10.
    Total 100.
    """
    score = 0
    
    if opp.title and len(opp.title) > 3: score += 10
    if opp.company and len(opp.company) > 1: score += 10
    if opp.location and len(opp.location) > 2: score += 10
    if opp.description and len(opp.description) > 100: score += 15
    if opp.required_skills and len(opp.required_skills) > 5: score += 15
    if opp.salary_range or (opp.salary_min and opp.salary_max): score += 10
    if opp.apply_url and len(opp.apply_url) > 10: score += 20
    if opp.job_type and opp.job_type.lower() != "unknown": score += 10
    
    # Freshness: 10 if seen in last 7 days, else scaled down
    if opp.last_seen:
        age_days = (datetime.utcnow() - opp.last_seen).days
        if age_days <= 3:
            score += 10
        elif age_days <= 7:
            score += 5
            
    return min(100, max(0, score))

def calculate_confidence_score(opp, company_health: int, collector_trust: int) -> int:
    """
    Phase 8.6: Opportunity Confidence Score
    30% Link Quality
    20% Freshness
    15% Company Health
    15% Collector Trust
    10% Description Quality
    10% Salary Availability
    """
    score = 0.0
    
    # Link Quality (30%)
    link_q = opp.link_quality_score if opp.link_quality_score is not None else 25
    score += (link_q / 100.0) * 30.0
    
    # Freshness (20%)
    freshness = 100
    if opp.last_seen:
        age_days = (datetime.utcnow() - opp.last_seen).days
        if age_days > 30: freshness = 0
        elif age_days > 14: freshness = 30
        elif age_days > 7: freshness = 60
        elif age_days > 3: freshness = 80
    score += (freshness / 100.0) * 20.0
    
    # Company Health (15%)
    score += (company_health / 100.0) * 15.0
    
    # Collector Trust (15%)
    score += (collector_trust / 100.0) * 15.0
    
    # Description Quality (10%)
    desc_quality = 100 if (opp.description and len(opp.description) > 200) else (50 if opp.description else 0)
    score += (desc_quality / 100.0) * 10.0
    
    # Salary Availability (10%)
    salary_avail = 100 if (opp.salary_range or opp.salary_min) else 0
    score += (salary_avail / 100.0) * 10.0
    
    return int(min(100, max(0, score)))
