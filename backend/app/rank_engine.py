import datetime
from app.models import Opportunity, CollectorHealth

def compute_rank_score(opp) -> int:
    """
    Phase 11.3.8: Weighted Ranking Logic
    Authoritative freshness and quality scoring.
    """
    score = 0
    now = datetime.datetime.utcnow()
    
    # 1. Freshness (based on first_seen/published_at for true age, last_seen for fallback)
    age_date = getattr(opp, 'first_seen', None) or getattr(opp, 'last_seen', now)
    delta_days = (now - age_date).days

    if delta_days <= 0: score += 120
    elif delta_days <= 1: score += 110
    elif delta_days <= 2: score += 100
    elif delta_days <= 3: score += 90
    elif delta_days <= 7: score += 70
    elif delta_days <= 14: score += 40
    elif delta_days <= 30: score += 10

    # 2. Quality & Verified Link Boosts
    link_status = getattr(opp, 'apply_url_status', '') or ''
    if "VERIFIED" in link_status:
        score += 80

    # 3. Source Origin Boosts
    data_origin = getattr(opp, 'data_origin', '') or ''
    source_type = getattr(opp, 'source_type', '') or ''
    
    if source_type == "DIRECT_EMPLOYER":
        score += 70
    elif source_type == "RECRUITMENT_AGENCY":
        score += 40
        
    if data_origin == "CURATED_FALLBACK":
        score += 20

    # 4. Status Penalties
    status = getattr(opp, 'status', 'ACTIVE')
    lifecycle = getattr(opp, 'lifecycle_status', 'ACTIVE')
    
    if status == "CLOSED" or lifecycle == "CLOSED":
        score -= 500
    elif status == "INVALID" or link_status == "BROKEN":
        score -= 300
    elif status == "STALE" or lifecycle == "STALE":
        score -= 50

    # 5. Geography
    is_india = getattr(opp, 'is_india_job', False)
    if is_india:
        score += 100
    else:
        score += 20

    # Keep older experiential penalties for relevance
    exp = getattr(opp, 'experience_min', 0) or 0
    if exp >= 8: score -= 250
    elif exp >= 5: score -= 150
    elif exp >= 2: score -= 30

    return score

def compute_personalized_rank(opp: Opportunity, match_score: int, freshness_score: int, company_score: int, collector_health_score: float = 50.0) -> float:
    """
    Phase 8.7 Wave 4: Data-Driven Opportunity Quality Intelligence
    Formula:
        Match Score          × 0.35 (Resume/Profile Fit)
        Confidence Score     × 0.25 (Trust, Link Quality, Freshness, Health)
        Completeness Score   × 0.20 (Job Description, Salary, Skills)
        Collector Health     × 0.10 (Data Pipeline Reliability)
        India Relevance      × 0.05
        Company Priority     × 0.05
    """
    india_relevance = opp.india_relevance_score or 0
    scaled_company = company_score * 20

    confidence = getattr(opp, 'confidence_score', 0) or 0
    completeness = getattr(opp, 'completeness_score', 0) or 0

    # Fallback to Phase 8.55 metrics if confidence is 0 (e.g. before engine runs)
    if confidence == 0:
        trust_score = opp.trust_score or 50
        scaled_freshness = freshness_score * 10
        link_quality = getattr(opp, 'link_quality_score', 25) or 25
        confidence = (trust_score * 0.4) + (scaled_freshness * 0.3) + (link_quality * 0.3)

    # Phase 9.0 Wave 1: Quality Enforcement Engine
    # Hard floor: BROKEN, EXPIRED, STALE
    lifecycle = getattr(opp, 'lifecycle_status', 'NEW')
    penalty = 0.0
    
    if lifecycle == "EXPIRED":
        return 0.0 # Strict exclusion
    elif lifecycle == "BROKEN":
        penalty += 200.0 # Heavy demotion
    elif lifecycle == "STALE":
        penalty += 50.0
        
    if confidence < 40:
        penalty += 150.0 # Demote low confidence heavily
        
    # Exclude if quality score (Wave 2) is too low
    quality_metrics = getattr(opp, 'quality_metrics', None)
    if quality_metrics and quality_metrics.quality_score < 60:
        penalty += 100.0

    apply_status = getattr(opp, 'apply_url_status', 'UNKNOWN') or 'UNKNOWN'
    if apply_status == 'HOMEPAGE_ONLY':
        penalty += 60.0

    final_score = (
        (match_score             * 0.35) +
        (confidence              * 0.25) +
        (completeness            * 0.20) +
        (collector_health_score  * 0.10) +
        (india_relevance         * 0.05) +
        (scaled_company          * 0.05)
    ) - penalty

    # Entry-level / Fresher / Internship priority boost (+150 pts)
    title_lower = (getattr(opp, 'title', '') or '').lower()
    job_type_lower = (getattr(opp, 'job_type', '') or '').lower()
    if any(k in title_lower or k in job_type_lower for k in ['intern', 'internship', 'trainee', 'fresher', 'associate', 'graduate', 'junior', 'entry', 'gte', 'sde-1', 'sde 1']):
        final_score += 150.0

    # Strict exclusion if score drops below 0
    return round(max(final_score, 0.0), 2)

