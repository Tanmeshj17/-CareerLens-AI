from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Index, func
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="user")  # 'user' or 'admin'
    
    # Phase 9.8: Email Verification & Password Reset
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True, index=True)
    verification_expires = Column(DateTime, nullable=True)
    reset_token = Column(String, nullable=True, index=True)
    reset_expires = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    applications = relationship("Application", back_populates="user")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    job_type = Column(String) # 'Full-time', 'Part-time', 'Internship', 'Contract'
    opportunity_category = Column(String, index=True, default="Job") # 'Job', 'Internship', 'Apprenticeship', 'Graduate Program', 'Walk-in Drive', 'Hackathon Hiring', 'Off-campus Drive', 'Mass Hiring'
    description = Column(Text)
    trust_score = Column(Integer)
    salary_range = Column(String, nullable=True)
    apply_url = Column(String, nullable=True)  # Direct apply link
    posted_date = Column(DateTime, default=datetime.utcnow)
    computed_rank_score = Column(Integer, index=True, default=0)
    
    # Core Pipeline Metadata
    opportunity_hash = Column(String, index=True, nullable=True)
    primary_source = Column(String, nullable=True)
    source_trust_score = Column(Integer, nullable=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    ats_type = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")
    is_active = Column(Boolean, default=True)

    # Phase 11.3.8: Lifecycle & Origin Metadata
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    data_origin = Column(String, nullable=True) # LIVE_API, LIVE_SCRAPE, CURATED_FALLBACK, MANUAL
    source_type = Column(String, default="DIRECT_EMPLOYER") # DIRECT_EMPLOYER, RECRUITMENT_AGENCY, JOB_AGGREGATOR, etc.

    # Phase 8.55: Direct Apply Link Integrity & Analytics
    apply_url_status = Column(String, default="UNKNOWN", index=True) # VERIFIED_DIRECT, VERIFIED_POSTING, BROWSER_VERIFICATION_REQUIRED, CAREER_BOARD, HOMEPAGE_ONLY, BROKEN, UNKNOWN
    link_classification = Column(String, nullable=True) # e.g., "Tier A - Lever"
    link_quality_score = Column(Integer, default=25, index=True) # 0 to 100
    verified_apply_url = Column(String, nullable=True)
    source_job_id = Column(String, nullable=True)
    last_url_verified_at = Column(DateTime, nullable=True)
    
    apply_attempts = Column(Integer, default=0)
    apply_success = Column(Integer, default=0)
    apply_failure = Column(Integer, default=0)
    homepage_redirects = Column(Integer, default=0)
    expired_clicks = Column(Integer, default=0)
    is_india_job = Column(Boolean, default=False, index=True)
    india_relevance_score = Column(Integer, default=0, index=True)
    india_confidence_score = Column(Integer, default=0, index=True)  # Phase 7.9: gate-validated 0-100
    required_skills = Column(Text, nullable=True)
    collected_by = Column(String, nullable=True)

    # Smart Validation Tracking (Phase 11.8)
    last_validated_at = Column(DateTime, nullable=True, index=True)
    validation_status = Column(String, default="PENDING", index=True) # PENDING, VALID, STALE, CLOSED
    validation_attempts = Column(Integer, default=0)
    validation_reason = Column(String, nullable=True)

    # Phase 8.6: Opportunity Quality Intelligence Engine
    legacy_hash = Column(String, index=True, nullable=True)
    lifecycle_status = Column(String, default="NEW", index=True)
    verification_count = Column(Integer, default=0)
    expired_reason = Column(String, nullable=True)
    last_verified_at = Column(DateTime, nullable=True, index=True)
    confidence_score = Column(Integer, default=0, index=True)
    completeness_score = Column(Integer, default=0, index=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String, default="INR", nullable=True)
    salary_period = Column(String, nullable=True) # Hourly, Monthly, Yearly

    # Fresher & Internship Intelligence Layer
    experience_min = Column(Integer, nullable=True)
    experience_max = Column(Integer, nullable=True)
    fresher_friendly = Column(Boolean, default=False)
    campus_hiring = Column(Boolean, default=False)
    walk_in_drive = Column(Boolean, default=False)
    mass_hiring = Column(Boolean, default=False)
    
    internship_type = Column(String, nullable=True) # Summer, Winter, Off-cycle
    work_mode = Column(String, nullable=True) # Remote, Hybrid, Onsite
    duration_months = Column(Integer, nullable=True)
    stipend_min = Column(String, nullable=True)
    stipend_max = Column(String, nullable=True)
    ppo_available = Column(Boolean, nullable=True)
    eligibility_batch = Column(String, nullable=True)
    application_deadline = Column(DateTime, nullable=True)
    
    # Eligibility Filters
    minimum_cgpa = Column(Float, nullable=True)
    allowed_degrees = Column(String, nullable=True)
    allowed_branches = Column(String, nullable=True)
    backlogs_allowed = Column(Boolean, nullable=True)
    year_of_passing = Column(String, nullable=True) # "2024, 2025"
    bond_period = Column(String, nullable=True)
    relocation_required = Column(Boolean, nullable=True)
    service_agreement = Column(Boolean, nullable=True)
    
    # Hiring Pattern Intelligence
    selection_rounds = Column(JSON, nullable=True) # ["Online Assessment", "Technical Interview"]
    expected_round_count = Column(Integer, nullable=True)
    difficulty_level = Column(String, nullable=True)

    # Phase 8.7: Lifecycle Tracking
    times_verified = Column(Integer, default=0)
    times_updated = Column(Integer, default=0)
    times_reactivated = Column(Integer, default=0)
    change_score = Column(Integer, default=0, index=True)  # 0-100 activity signal
    description_hash = Column(String, nullable=True)  # MD5 for change detection
    skills_hash = Column(String, nullable=True)  # MD5 for skills change detection

    applications = relationship("Application", back_populates="opportunity")
    quality_metrics = relationship("JobQualityMetrics", back_populates="opportunity", uselist=False)
    lineage = relationship("CollectionLineage", back_populates="opportunity", uselist=False)
    history = relationship("OpportunityHistory", back_populates="opportunity")

class JobQualityMetrics(Base):
    """Extracted from Opportunity to keep the main table clean. Tracks data quality."""
    __tablename__ = "job_quality_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    quality_score = Column(Integer, default=0)
    trust_score = Column(Integer, default=0)
    verification_status = Column(String, default="Pending") # Pending, Verified, Rejected
    is_duplicate = Column(Boolean, default=False)
    is_official = Column(Boolean, default=False)
    salary_confidence = Column(Integer, nullable=True) # 0-100%
    last_verified = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    opportunity = relationship("Opportunity", back_populates="quality_metrics")

class CollectionLineage(Base):
    """Tracks exactly where a job came from for debugging."""
    __tablename__ = "collection_lineage"
    
    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    source_type = Column(String) # Official, ATS, Aggregator
    source_url = Column(String, nullable=True)
    collector_name = Column(String)
    collector_version = Column(String)
    collection_time = Column(DateTime, default=datetime.utcnow)
    parser_version = Column(String)
    verification_time = Column(DateTime, nullable=True)
    
    opportunity = relationship("Opportunity", back_populates="lineage")

class JobSource(Base):
    """Replaces/Extends generic source metadata for better source tracking."""
    __tablename__ = "job_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, unique=True, index=True)
    source_type = Column(String) # Official, ATS, Aggregator
    priority = Column(Integer, default=5)
    country = Column(String, default="India")
    is_official = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    health_score = Column(Integer, default=100, index=True)
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0, index=True)
    average_response_time = Column(Float, nullable=True)

class CollectorHealth(Base):
    """
    Phase 8.7 V2: Full Collector Intelligence — 18 metrics, stability score,
    adaptive tier, and opportunity attribution support.
    """
    __tablename__ = "collector_health"

    id = Column(Integer, primary_key=True, index=True)
    collector_name = Column(String, unique=True, index=True)
    ats_type = Column(String, nullable=True, index=True)
    status = Column(String, default="Active")  # Active | Paused | Degraded | Retired

    # --- Tier & Score ---
    collector_score = Column(Float, default=0.0, index=True)   # 0-100 composite
    collector_stability = Column(Float, default=0.0)           # 0-100 long-term reliability
    roi_tier = Column(String, default="Tier C", index=True)    # Tier A | B | C | D
    adaptive_interval_hours = Column(Float, default=12.0)      # Current dynamic schedule

    # --- Yield metrics ---
    jobs_collected_today = Column(Integer, default=0)
    jobs_collected_total = Column(Integer, default=0)
    jobs_inserted = Column(Integer, default=0)
    active_jobs = Column(Integer, default=0)
    new_jobs_pct = Column(Float, nullable=True)       # % genuinely new each run
    update_rate = Column(Float, nullable=True)         # % existing jobs updated

    # --- Quality metrics ---
    duplicates_removed = Column(Integer, default=0)
    duplicate_pct = Column(Float, nullable=True)
    broken_links_pct = Column(Float, nullable=True)
    expired_pct = Column(Float, nullable=True)
    avg_confidence = Column(Float, nullable=True)
    avg_completeness = Column(Float, nullable=True)
    avg_freshness_days = Column(Float, nullable=True)
    avg_verification_success = Column(Float, nullable=True)
    apply_ctr = Column(Float, nullable=True)           # Future: SearchAnalytics
    salary_change_rate = Column(Float, nullable=True)  # Salary changes per 100 jobs
    history_events_generated = Column(Integer, default=0)

    # --- Reliability metrics ---
    success_rate = Column(Float, default=100.0)
    average_runtime_ms = Column(Float, nullable=True)
    avg_response_ms = Column(Float, nullable=True)
    crawler_uptime_pct = Column(Float, default=100.0)
    timeout_rate = Column(Float, nullable=True)
    retry_success_rate = Column(Float, nullable=True)
    yield_percent = Column(Float, nullable=True)       # jobs_inserted / jobs_collected

    # --- Run tracking ---
    last_run = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    last_error = Column(String, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CollectorHealthHistory(Base):
    """
    Daily snapshots of collector performance — enables trend detection.
    'Oracle score dropped from 90 to 74 over 2 weeks' becomes visible.
    """
    __tablename__ = "collector_health_history"

    id = Column(Integer, primary_key=True, index=True)
    collector_name = Column(String, index=True)
    ats_type = Column(String, nullable=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)

    collector_score = Column(Float, nullable=True)
    collector_stability = Column(Float, nullable=True)
    roi_tier = Column(String, nullable=True)
    jobs_collected = Column(Integer, default=0)
    active_jobs = Column(Integer, default=0)
    duplicate_pct = Column(Float, nullable=True)
    broken_links_pct = Column(Float, nullable=True)
    avg_confidence = Column(Float, nullable=True)
    avg_freshness_days = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    crawler_uptime_pct = Column(Float, nullable=True)
    avg_response_ms = Column(Float, nullable=True)


class CollectorAlert(Base):
    """
    Auto-generated alerts when collectors degrade below thresholds.
    'Greenhouse broken_links_pct > 20%' → alert fires automatically.
    """
    __tablename__ = "collector_alerts"

    id = Column(Integer, primary_key=True, index=True)
    collector_name = Column(String, index=True)
    ats_type = Column(String, nullable=True)
    alert_type = Column(String, index=True)
    # LOW_SCORE | HIGH_BROKEN_LINKS | NO_JOBS_48H | CONFIDENCE_DROP
    # HIGH_DUPLICATES | TIMEOUT_SPIKE | UPTIME_DROP | STABILITY_DEGRADED
    severity = Column(String, default="WARNING")  # INFO | WARNING | ALERT | CRITICAL
    message = Column(Text)
    metric_name = Column(String, nullable=True)
    metric_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# ─────────────────────────────────────────────────────────────
# Phase 9.0 Wave 1: Search Intelligence & Learning
# ─────────────────────────────────────────────────────────────
class SearchEvent(Base):
    """Tracks individual user searches and clicks for continuous learning."""
    __tablename__ = "search_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    query_text = Column(String, index=True)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    result_count = Column(Integer, default=0)
    
    # Interaction metrics
    clicked_job_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True)
    click_position = Column(Integer, nullable=True)
    ignored_job_ids = Column(JSON, nullable=True)  # List of IDs shown but not clicked
    session_duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SearchAggregate(Base):
    """Aggregated search metrics (CTR, zero-results) for analytics and auto-correction."""
    __tablename__ = "search_aggregates"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, unique=True, index=True)
    total_searches = Column(Integer, default=0)
    zero_result_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    avg_click_position = Column(Float, nullable=True)
    avg_session_duration = Column(Float, nullable=True)
    last_searched_at = Column(DateTime, default=datetime.utcnow, index=True)

class CollectorFailure(Base):
    """Opportunity Fetch Failure Queue"""
    __tablename__ = "collector_failures"

    id = Column(Integer, primary_key=True, index=True)
    collector_name = Column(String, index=True)
    company = Column(String, nullable=True)
    error_message = Column(String)
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    last_attempt = Column(DateTime, default=datetime.utcnow)

class SearchAnalytics(Base):
    __tablename__ = "search_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(String, index=True)
    clicked_job_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True)
    result_count = Column(Integer, default=0)
    click_position = Column(Integer, nullable=True)
    is_zero_results = Column(Boolean, default=False)
    response_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class OpportunityHistory(Base):
    """
    Phase 8.7: Full lifecycle audit trail for every opportunity.
    Every change is recorded permanently and can power notifications,
    trending, analytics, and the job detail timeline view.
    """
    __tablename__ = "opportunity_history"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), index=True)

    # Event classification
    event_type = Column(String, index=True)
    # Supported events:
    # FIRST_SEEN, VERIFIED, REVERIFIED, UPDATED, SALARY_CHANGED, DESCRIPTION_CHANGED,
    # LOCATION_CHANGED, SKILLS_CHANGED, EXPERIENCE_CHANGED, LINK_CHANGED, LINK_FIXED,
    # LINK_BROKEN, STATUS_CHANGED, CONFIDENCE_CHANGED, COMPLETENESS_CHANGED,
    # COMPANY_CHANGED, REACTIVATED, EXPIRED, REMOVED, DUPLICATE_MERGED, MANUAL_EDIT

    changed_field = Column(String, nullable=True, index=True)  # e.g. 'salary_min', 'apply_url'
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    change_summary = Column(String, nullable=True)  # Human-readable e.g. "₹8L → ₹10L"

    # Severity: LOW | MEDIUM | HIGH | CRITICAL
    severity = Column(String, default="LOW", index=True)

    # Snapshot at time of event
    confidence_before = Column(Integer, nullable=True)
    confidence_after = Column(Integer, nullable=True)
    completeness_before = Column(Integer, nullable=True)
    completeness_after = Column(Integer, nullable=True)
    link_quality_before = Column(Integer, nullable=True)
    link_quality_after = Column(Integer, nullable=True)
    lifecycle_before = Column(String, nullable=True)
    lifecycle_after = Column(String, nullable=True)

    # Source attribution
    collector_name = Column(String, nullable=True)
    source = Column(String, nullable=True)
    detected_by = Column(String, default="system")  # system | manual | scheduler

    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    opportunity = relationship("Opportunity", back_populates="history")

class DiscoveredCompanyATS(Base):
    """Auto-discovered ATS configurations."""
    __tablename__ = "discovered_company_ats"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    career_url = Column(String, nullable=True)
    redirect_url = Column(String, nullable=True)
    ats_type = Column(String, nullable=True)
    ats_version = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    detection_method = Column(String, nullable=True) # Fingerprint, HTTP, Manual, API, Browser, Hybrid
    confidence = Column(Integer, default=0)
    auto_discovered = Column(Boolean, default=True)
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    collector_assigned = Column(String, nullable=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class DashboardStatsCache(Base):
    """Caches expensive COUNT(*) queries for the dashboard."""
    __tablename__ = "dashboard_stats_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    total_jobs = Column(Integer, default=0)
    active_jobs = Column(Integer, default=0)
    verified_jobs = Column(Integer, default=0)
    remote_jobs = Column(Integer, default=0)
    freshers_jobs = Column(Integer, default=0)
    internships = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    status = Column(String, default="Saved") # 'Saved', 'Not Applied', 'Applied', 'Assessment', 'Interview', 'Offer', 'Rejected', 'Joined'
    applied_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)
    
    user = relationship("User", back_populates="applications")
    opportunity = relationship("Opportunity", back_populates="applications")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    ats_score = Column(Integer)
    skills_score = Column(Integer)
    missing_skills = Column(String)
    posted_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

# Phase 2 Tables

class ResumeProfile(Base):
    __tablename__ = "resume_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    uploaded_file = Column(String)
    extracted_skills = Column(JSON, nullable=True)
    extracted_projects = Column(JSON, nullable=True)
    extracted_education = Column(JSON, nullable=True)
    extracted_certifications = Column(JSON, nullable=True)
    extracted_experience = Column(JSON, nullable=True)
    ats_score = Column(Integer)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferred_roles = Column(JSON, nullable=True)  # e.g. ["Data Analyst", "Data Engineer"]
    preferred_locations = Column(JSON, nullable=True)
    preferred_job_type = Column(JSON, nullable=True) # e.g. ["Full-time", "Internship"]
    remote_preference = Column(String, default="Open") # 'Only Remote', 'Open', 'On-site'
    minimum_salary = Column(Integer, nullable=True)
    preferred_companies = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

class JobMatchScore(Base):
    __tablename__ = "job_match_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    
    # Granular scoring
    match_score = Column(Integer)
    skill_score = Column(Integer)
    role_score = Column(Integer)
    location_score = Column(Integer)
    freshness_score = Column(Integer)
    company_score = Column(Integer)
    salary_score = Column(Integer)
    
    # Matching details
    matching_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    match_level = Column(String)  # High Probability, Medium Probability, Stretch, Low Match
    explanation = Column(JSON, nullable=True) # Why this was recommended
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    opportunity = relationship("Opportunity")

class ResumeMatchResult(Base):
    __tablename__ = "resume_match_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), index=True)
    match_percentage = Column(Integer)
    missing_skills = Column(JSON, nullable=True)
    matched_skills = Column(JSON, nullable=True)
    recommended_skills = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    opportunity = relationship("Opportunity")

class CareerReadiness(Base):
    __tablename__ = "career_readiness"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    target_role = Column(String, index=True)
    readiness_score = Column(Integer)
    missing_skills = Column(JSON, nullable=True)
    recommended_skills = Column(JSON, nullable=True)
    estimated_months = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

class RawJob(Base):
    __tablename__ = "raw_jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    job_type = Column(String)
    description = Column(Text)
    salary_range = Column(String, nullable=True)
    apply_url = Column(String, nullable=True)
    source = Column(String)
    ats_type = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    raw_data = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

class CompanyRegistry(Base):
    """
    Phase 7.7: 4-Stage India Hiring Discovery Engine
    Stages: 1. Discover -> 2. Detect -> 3. Validate -> 4. Promote
    """
    __tablename__ = "company_registry"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    
    # 1. Discover
    company_category = Column(String, nullable=True) # Startup, Service, MNC, Big4, BFSI, Analytics, PSU, Product
    hiring_in_india = Column(Boolean, default=True)
    india_hiring_priority = Column(Integer, default=50) # 0-100
    
    # 2. Detect
    source_type = Column(String, nullable=True) # ATS, Direct
    ats_type = Column(String, nullable=True) # Greenhouse, Lever, Workday, SmartRecruiters, iCIMS, Ashby, etc.
    ats_identifier = Column(String, nullable=True) # e.g. 'postman' for greenhouse
    workday_tenant = Column(String, nullable=True) # e.g. 'google' for Workday
    workday_site_url = Column(String, nullable=True) # e.g. 'googlecareers'
    source_url = Column(String, nullable=True)
    
    # 3. Validate
    validation_status = Column(String, default="Unknown") # Active, Broken, Unknown, Rate_Limited, Manual_Review
    last_checked = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Integer, default=50) # 0-100 reliability
    active_jobs = Column(Integer, default=0)
    india_jobs_found = Column(Integer, default=0)
    
    # 4. Promote
    collector_enabled = Column(Boolean, default=False)
    
    # Phase 8.7: Core Registry fields
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    country = Column(String, default="India")
    city = Column(String, nullable=True)
    priority = Column(String, default="medium")
    verified = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    collector = Column(String, nullable=True)
    crawl_frequency = Column(String, default="12h")
    total_jobs_ever = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Legacy / Operational
    failure_count = Column(Integer, default=0)
    retry_interval_minutes = Column(Integer, default=60)
    last_success = Column(DateTime, nullable=True)
    
    # Phase 8.6: Company Health Engine
    health_score = Column(Integer, default=100) # 0-100 overall health


class ATSHealthLog(Base):
    __tablename__ = "ats_health_log"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    ats_type = Column(String)
    is_success = Column(Boolean, default=True)
    jobs_collected = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    run_time = Column(DateTime, default=datetime.utcnow)

class OpportunitySource(Base):
    __tablename__ = "opportunity_sources"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    source_name = Column(String)
    source_url = Column(String, nullable=True)
    trust_score = Column(Integer)
    last_checked = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Active")

    opportunity = relationship("Opportunity")

class CareerInsight(Base):
    __tablename__ = "career_insights"

    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String)
    data = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)


# Phase 3 Tables

class RawInternship(Base):
    __tablename__ = "raw_internships"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    duration = Column(String, nullable=True)
    stipend = Column(String, nullable=True)
    description = Column(Text)
    apply_url = Column(String, nullable=True)
    source = Column(String)
    source_url = Column(String, nullable=True)
    raw_data = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    provider = Column(String)  # 'freeCodeCamp', 'YouTube', 'Microsoft Learn', etc.
    category = Column(String)  # 'Course', 'YouTube Playlist', 'Documentation', 'Practice Platform'
    description = Column(Text)
    url = Column(String)
    difficulty = Column(String, nullable=True)  # 'Beginner', 'Intermediate', 'Advanced'
    duration = Column(String, nullable=True)  # '8 Hours', '32 Hours'
    is_free = Column(Boolean, default=True)
    skills_covered = Column(JSON, nullable=True)
    source = Column(String)
    language = Column(String, default="English")  # 'English', 'Hindi', etc.
    channel = Column(String, nullable=True)  # YouTube channel name
    rating = Column(Float, nullable=True)
    last_verified = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)
    
    # Phase 9.7.1.5 Extension
    availability_status = Column(String, default="VERIFIED")
    status = Column(String, default="VERIFIED") # Phase 11.3.8 status (VERIFIED, INVALID_RESOURCE)
    affordability = Column(String, default="FREE")
    price = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    roles = Column(JSON, nullable=True)
    verification_source = Column(String, nullable=True)
    country = Column(String, default="Global")

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String)  # 'Running', 'Success', 'Failed', 'Partial'
    records_collected = Column(Integer, default=0)
    records_cleaned = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_deduplicated = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    duration_seconds = Column(Float, nullable=True)


# ══════════════════════════════════════════════════════════════
# Phase 7.2 Tables — Search Intelligence & Learning Engine
# ══════════════════════════════════════════════════════════════

class SearchLog(Base):
    """Logs every user search for analytics and zero-result detection."""
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query = Column(String, index=True)
    results_count = Column(Integer, default=0)
    clicked_job_id = Column(Integer, nullable=True)
    click_position = Column(Integer, nullable=True)
    filters_used = Column(JSON, nullable=True)  # {"job_type": "Full-time", "location": "Pune"}
    created_at = Column(DateTime, default=datetime.utcnow)

class NormalizedLocation(Base):
    """Structured location normalization table for India-first ranking."""
    __tablename__ = "normalized_locations"

    id = Column(Integer, primary_key=True, index=True)
    raw_value = Column(String, unique=True, index=True)  # "Pune, Maharashtra"
    city = Column(String, index=True)       # "Pune"
    state = Column(String, nullable=True)   # "Maharashtra"
    country = Column(String, default="India")  # "India"
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String, nullable=True)
    
    # Phase 7.3 Extensions
    is_tier1_city = Column(Boolean, default=False)
    is_tier2_city = Column(Boolean, default=False)
    is_metro = Column(Boolean, default=False)
    cost_of_living_index = Column(Float, nullable=True)

class RoleSkillMap(Base):
    """Data-driven mapping of roles to their required skills."""
    __tablename__ = "role_skill_maps"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)  # "Data Engineer"
    skill = Column(String, index=True)  # "Python"
    importance = Column(String, default="Required")  # 'Required', 'Preferred', 'Nice-to-have'
    category = Column(String, nullable=True)  # 'Programming', 'Cloud', 'Database', 'Framework'

class Certification(Base):
    """Rich certification metadata for career recommendations."""
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    provider = Column(String)  # 'Google', 'Microsoft', 'AWS', 'Databricks'
    url = Column(String, nullable=True)
    is_free = Column(Boolean, default=False)
    cost = Column(String, nullable=True)  # "$150" or "Free"
    difficulty = Column(String, nullable=True)  # 'Beginner', 'Intermediate', 'Advanced'
    estimated_hours = Column(Integer, nullable=True)
    validity_years = Column(Integer, nullable=True)
    exam_required = Column(Boolean, default=True)
    skills_covered = Column(JSON, nullable=True)
    roles = Column(JSON, nullable=True)  # ["Data Engineer", "Data Analyst"]
    created_at = Column(DateTime, default=datetime.utcnow)

    # Phase 9.7.1.5 Extension
    availability_status = Column(String, default="VERIFIED")
    last_verified_at = Column(DateTime, nullable=True)
    currency = Column(String, nullable=True)
    price_inr = Column(Integer, nullable=True)
    affordability = Column(String, nullable=True)
    free_learning_available = Column(Boolean, default=False)
    financial_aid_available = Column(Boolean, default=False)
    student_discount_available = Column(Boolean, default=False)
    certification_type = Column(String, nullable=True)
    verification_source = Column(String, nullable=True)

class HiringIntelligenceGlobalSnapshot(Base):
    """Phase 8.6: Daily global metrics for the entire platform."""
    __tablename__ = "hiring_intelligence_global_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True) 
    jobs_today = Column(Integer, default=0)
    jobs_this_week = Column(Integer, default=0)
    jobs_this_month = Column(Integer, default=0)
    expired_today = Column(Integer, default=0)
    broken_today = Column(Integer, default=0)
    recovered_today = Column(Integer, default=0)
    average_confidence = Column(Integer, default=0)
    average_freshness = Column(Integer, default=0)

class HiringIntelligenceCompanySnapshot(Base):
    """Phase 8.6: Daily hiring metrics per company."""
    __tablename__ = "hiring_intelligence_company_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    jobs_today = Column(Integer, default=0)
    jobs_this_week = Column(Integer, default=0)
    hiring_velocity = Column(String, default="Stable") # High, Low, Stable
    hiring_trend = Column(String, default="Flat") # Up, Down, Flat
    company_hiring_score = Column(Integer, default=0)


# Phase 10.2 Career Intelligence Models
class UserCareerProfile(Base):
    __tablename__ = "user_career_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    target_role = Column(String)
    experience_level = Column(String, nullable=True)
    current_role = Column(String, nullable=True)
    education = Column(String, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Phase 10.2 Career Intelligence Models
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSkillProfile(Base):
    __tablename__ = "user_skill_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    skill_name = Column(String, index=True)
    proficiency_level = Column(String, default="BEGINNER")
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CareerReadinessSnapshot(Base):
    __tablename__ = "career_readiness_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    target_role = Column(String, index=True)
    readiness_score = Column(Integer)
    skill_coverage_score = Column(Integer)
    experience_score = Column(Integer)
    resume_score = Column(Integer)
    calculated_at = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# Phase 11.4: Data Quality & Collector Reliability Models
# ─────────────────────────────────────────────────────────────

class PipelineRunMetrics(Base):
    """
    Phase 11.4 T12: Per-run pipeline observability metrics.
    Records duration, throughput, error rates for every scheduled run.
    """
    __tablename__ = "pipeline_run_metrics"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String, index=True)
    run_id = Column(String, index=True, nullable=True)          # UUID for this run
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Collector counts
    collectors_run = Column(Integer, default=0)
    collectors_ok = Column(Integer, default=0)
    collectors_failed = Column(Integer, default=0)
    collectors_zero_result = Column(Integer, default=0)
    collectors_slow = Column(Integer, default=0)               # >30s threshold

    # Volume metrics
    total_collected = Column(Integer, default=0)
    total_inserted = Column(Integer, default=0)
    total_updated = Column(Integer, default=0)
    total_duplicates = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    total_broken_links = Column(Integer, default=0)

    # Throughput
    rows_per_second = Column(Float, nullable=True)
    insert_speed_ms = Column(Float, nullable=True)             # avg ms per insert
    update_speed_ms = Column(Float, nullable=True)             # avg ms per update

    # Resource usage
    peak_memory_mb = Column(Float, nullable=True)

    # Status
    status = Column(String, default="RUNNING")                 # RUNNING | SUCCESS | PARTIAL | FAILED
    error_summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class CompanyAlias(Base):
    """
    Phase 11.4 T5: Company name normalization lookup table.
    Maps raw/variant company names to canonical forms.
    e.g. 'TCS' → 'Tata Consultancy Services', 'Infosys Ltd' → 'Infosys'
    """
    __tablename__ = "company_aliases"

    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, unique=True, index=True)            # raw variant
    canonical_name = Column(String, index=True)                # normalized form
    source = Column(String, default="HARDCODED")               # HARDCODED | LEARNED | MANUAL
    created_at = Column(DateTime, default=datetime.utcnow)


class LocationNorm(Base):
    """
    Phase 11.4 T6: Location normalization lookup table.
    Maps raw location strings to structured city/state/country.
    e.g. 'Bangalore' → city='Bengaluru', state='Karnataka', country='India'
    """
    __tablename__ = "location_norms"

    id = Column(Integer, primary_key=True, index=True)
    raw_location = Column(String, unique=True, index=True)     # raw variant
    city = Column(String, index=True, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, default="India")
    is_remote = Column(Boolean, default=False)
    source = Column(String, default="HARDCODED")               # HARDCODED | LEARNED | MANUAL
    created_at = Column(DateTime, default=datetime.utcnow)


class DataAlert(Base):
    """
    Phase 11.4 T13: System-wide data quality alerts.
    Distinct from CollectorAlert (which is collector-specific).
    Tracks pipeline-level and global threshold violations.
    """
    __tablename__ = "data_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, index=True)
    # Types: BROKEN_LINKS_HIGH | DUPLICATE_RATE_HIGH | FRESHNESS_LOW |
    #        INDIA_RATIO_LOW | PIPELINE_FAILED | COLLECTOR_ZERO_RESULT |
    #        COLLECTOR_SLOW | LIFECYCLE_STUCK | RESOURCE_INVALID_HIGH
    severity = Column(String, default="WARNING", index=True)   # INFO | WARNING | ALERT | CRITICAL
    source = Column(String, nullable=True)                     # collector name or 'system'
    metric_name = Column(String, nullable=True)
    metric_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    message = Column(Text)
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    cooldown_key = Column(String, nullable=True, index=True)   # dedup: alert_type+source
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Feedback(Base):
    """
    Feedback model for user reviews, bug reports, feature requests, and inquiries.
    Stored exclusively in PostgreSQL with optional foreign key to users.id.
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    rating = Column(Integer, nullable=True)                      # 1 to 5 stars
    category = Column(String(50), nullable=False, index=True)   # Bug Report, Feature Request, UI/UX Improvement, Performance, General Feedback
    priority = Column(String(20), default="Medium")             # Low, Medium, High, Critical
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    file_attachment = Column(String(255), nullable=True)
    status = Column(String(20), default="Open", index=True)     # Open, In Review, Resolved, Closed
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

