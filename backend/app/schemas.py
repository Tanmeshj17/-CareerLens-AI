
from typing import Optional, List, Any, Dict
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

class UserUpdate(BaseModel):
    full_name: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

# Security Schemas
class EmailVerificationRequest(BaseModel):
    token: str = Field(..., min_length=16)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=16)
    new_password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Opportunity Schemas
class OpportunityBase(BaseModel):
    title: str
    company: str
    location: str
    job_type: str
    opportunity_category: Optional[str] = "Job"
    description: str
    trust_score: int
    salary_range: Optional[str] = None
    apply_url: Optional[str] = None
    opportunity_hash: Optional[str] = None
    primary_source: Optional[str] = None
    source_trust_score: Optional[int] = None
    status: Optional[str] = "Active"
    required_skills: Optional[str] = None
    collected_by: Optional[str] = None
    ats_type: Optional[str] = None

    # Fresher & Internship Metadata
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    fresher_friendly: Optional[bool] = False
    campus_hiring: Optional[bool] = False
    walk_in_drive: Optional[bool] = False
    mass_hiring: Optional[bool] = False
    internship_type: Optional[str] = None
    work_mode: Optional[str] = None
    duration_months: Optional[int] = None
    stipend_min: Optional[str] = None
    stipend_max: Optional[str] = None

    # Phase 8.6 Fields
    legacy_hash: Optional[str] = None
    lifecycle_status: Optional[str] = "NEW"
    verification_count: Optional[int] = 0
    expired_reason: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    confidence_score: Optional[int] = 0
    completeness_score: Optional[int] = 0
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "INR"
    salary_period: Optional[str] = None
    ppo_available: Optional[bool] = None
    application_deadline: Optional[datetime] = None
    minimum_cgpa: Optional[float] = None
    allowed_degrees: Optional[str] = None
    allowed_branches: Optional[str] = None
    backlogs_allowed: Optional[bool] = None
    year_of_passing: Optional[str] = None
    bond_period: Optional[str] = None
    relocation_required: Optional[bool] = None
    service_agreement: Optional[bool] = None
    selection_rounds: Optional[List[str]] = None
    expected_round_count: Optional[int] = None
    difficulty_level: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class Opportunity(OpportunityBase):
    id: int
    posted_date: datetime
    computed_rank_score: Optional[int] = 0
    last_checked: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True

# Application Schemas
class ApplicationBase(BaseModel):
    opportunity_id: int
    status: str = "Saved"
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class Application(ApplicationBase):
    id: int
    user_id: int
    applied_date: datetime
    opportunity: Optional[Opportunity] = None

    class Config:
        from_attributes = True

# Resume Schemas
class ResumeBase(BaseModel):
    filename: str
    ats_score: int
    skills_score: int
    missing_skills: str

class ResumeCreate(ResumeBase):
    pass


class AnalyzeResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    ats_score: int
    skills_score: int
    extracted_skills: Optional[List[str]] = []
    extracted_projects: Optional[List[Dict[str, Any]]] = []
    extracted_education: Optional[List[Dict[str, Any]]] = []
    extracted_certifications: Optional[List[str]] = []
    extracted_experience: Optional[List[Dict[str, Any]]] = []
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    suggestions: Optional[List[str]] = []
    score_breakdown: Optional[Dict[str, Any]] = None
    metrics_found: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class Resume(ResumeBase):
    id: int
    user_id: int
    posted_date: datetime

    class Config:
        from_attributes = True

# ResumeProfile Schemas (Phase 2)
class ResumeProfileBase(BaseModel):
    uploaded_file: str
    extracted_skills: Optional[List[str]] = []
    extracted_projects: Optional[List[Dict[str, Any]]] = []
    extracted_education: Optional[List[Dict[str, Any]]] = []
    extracted_certifications: Optional[List[str]] = []
    extracted_experience: Optional[List[Dict[str, Any]]] = []
    ats_score: int
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    suggestions: Optional[List[str]] = []

class ResumeProfileCreate(ResumeProfileBase):
    user_id: int

class ResumeProfile(ResumeProfileBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# JobMatchScore Schemas (Phase 2)
class JobMatchScoreBase(BaseModel):
    opportunity_id: int
    match_score: int
    matching_skills: Optional[List[str]] = []
    missing_skills: Optional[List[str]] = []
    match_level: str

class JobMatchScoreCreate(JobMatchScoreBase):
    user_id: int

class JobMatchScore(JobMatchScoreBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# RawJob Schemas (Phase 2)
class RawJobBase(BaseModel):
    title: str
    company: str
    location: str
    job_type: str
    description: str
    salary_range: Optional[str] = None
    apply_url: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    raw_data: Optional[str] = None
    is_processed: Optional[bool] = False

class RawJobCreate(RawJobBase):
    pass

class RawJob(RawJobBase):
    id: int
    collected_at: datetime

    class Config:
        from_attributes = True

# OpportunitySource Schemas (Phase 2)
class OpportunitySourceBase(BaseModel):
    opportunity_id: int
    source_name: str
    source_url: Optional[str] = None
    trust_score: int
    status: Optional[str] = "Active"

class OpportunitySourceCreate(OpportunitySourceBase):
    pass

class OpportunitySource(OpportunitySourceBase):
    id: int
    last_checked: datetime

    class Config:
        from_attributes = True

# CareerInsight Schemas (Phase 2)
class CareerInsightBase(BaseModel):
    insight_type: str
    data: Dict[str, Any]

class CareerInsightCreate(CareerInsightBase):
    pass

class CareerInsight(CareerInsightBase):
    id: int
    generated_at: datetime

    class Config:
        from_attributes = True


# Phase 3 Schemas

# RawInternship Schemas
class SystemHealth(BaseModel):
    database: str
    scheduler: str
    active_collectors: int
    last_run_status: Optional[str] = None
    
# CompanyRegistry Schemas (Phase 5 + 7.2 enhancements)
class CompanyRegistryBase(BaseModel):
    company_name: str
    ats_type: str
    ats_identifier: Optional[str] = None
    careers_url: Optional[str] = None
    active_jobs: int = 0
    status: str = "Active"
    verification_status: str = "Pending"
    category: Optional[str] = None
    priority: int = 5
    failure_count: int = 0
    retry_interval_minutes: int = 60

class CompanyRegistryCreate(CompanyRegistryBase):
    pass

class CompanyRegistry(CompanyRegistryBase):
    id: int
    last_checked: datetime
    last_success: Optional[datetime] = None

    class Config:
        from_attributes = True

class CompanyInsight(BaseModel):
    company_name: str
    active_opportunities: int
    top_skills: List[str]
    top_locations: List[str]

class ATSHealthLogBase(BaseModel):
    company_name: str
    ats_type: str
    is_success: bool = True
    jobs_collected: int = 0
    duration_ms: int = 0
    error_message: Optional[str] = None

class ATSHealthLogCreate(ATSHealthLogBase):
    pass

class ATSHealthLog(ATSHealthLogBase):
    id: int
    run_time: datetime

    class Config:
        from_attributes = True

class CollectorHealthStats(BaseModel):
    success_rate: float
    failure_rate: float
    average_duration_ms: float
    last_successful_run: Optional[datetime] = None

class CoverageStats(BaseModel):
    companies_by_ats: Dict[str, int]
    jobs_by_ats: Dict[str, int]
    failed_companies: List[str]
    last_sync_time: Optional[datetime] = None

class RawInternshipBase(BaseModel):
    title: str
    company: str
    location: str
    duration: Optional[str] = None
    stipend: Optional[str] = None
    description: str
    apply_url: Optional[str] = None
    source: str
    source_url: Optional[str] = None
    raw_data: Optional[str] = None
    is_processed: Optional[bool] = False

class RawInternshipCreate(RawInternshipBase):
    pass

class RawInternship(RawInternshipBase):
    id: int
    collected_at: datetime

    class Config:
        from_attributes = True

# LearningResource Schemas (Phase 7.2 enhanced)
class LearningResourceBase(BaseModel):
    title: str
    provider: str
    category: str
    description: Optional[str] = None
    url: str
    difficulty: Optional[str] = None
    duration: Optional[str] = None
    is_free: Optional[bool] = True
    skills_covered: Optional[List[str]] = []
    source: Optional[str] = None
    language: Optional[str] = "English"
    channel: Optional[str] = None
    rating: Optional[float] = None
    last_verified: Optional[datetime] = None
    is_processed: Optional[bool] = False
    # Phase 9.7.1.5
    availability_status: Optional[str] = "VERIFIED"
    affordability: Optional[str] = "FREE"
    price: Optional[str] = None
    currency: Optional[str] = None
    roles: Optional[List[str]] = []
    verification_source: Optional[str] = None
    country: Optional[str] = "Global"

class LearningResourceCreate(LearningResourceBase):
    pass

class LearningResource(LearningResourceBase):
    id: int
    collected_at: datetime

    @field_validator('skills_covered', mode='before')
    @classmethod
    def parse_skills_covered(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator('roles', mode='before')
    @classmethod
    def parse_roles(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    class Config:
        from_attributes = True

class LearningResourceResponse(LearningResource):
    match_reason: Optional[str] = None
    matched_skills: Optional[List[str]] = []
    role_match: Optional[bool] = None
    verification_confidence: Optional[str] = "HIGH"

    class Config:
        from_attributes = True

# PipelineRun Schemas
class PipelineRunBase(BaseModel):
    pipeline_name: str
    status: str
    records_collected: Optional[int] = 0
    records_cleaned: Optional[int] = 0
    records_inserted: Optional[int] = 0
    records_deduplicated: Optional[int] = 0
    errors: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[float] = None

class PipelineRunCreate(PipelineRunBase):
    pass

class PipelineRun(PipelineRunBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI Schemas — aligned with actual endpoint return data
class SkillGapAnalysis(BaseModel):
    matching_skills: List[str]
    missing_skills: List[str]
    recommended_skills: List[str]

class ReadinessFactors(BaseModel):
    ats_score: int
    avg_match_score: int
    market_skills_match: int

class MarketReadiness(BaseModel):
    readiness_score: int
    level: str
    factors: ReadinessFactors

class RoadmapStep(BaseModel):
    step_number: Optional[int] = None
    title: str
    description: str
    skills: Optional[List[str]] = None
    estimated_weeks: int

class CareerRoadmap(BaseModel):
    role: str
    description: Optional[str] = None
    total_weeks: Optional[int] = None
    strategies: Optional[List[str]] = None
    what_to_learn: Optional[List[str]] = None
    steps: List[RoadmapStep]

class InterviewQuestion(BaseModel):
    model_config = {"protected_namespaces": ()}
    category: str
    question: str
    difficulty: str
    estimated_time: Optional[int] = None
    model_answer: str

# ══════════════════════════════════════════════════════════════
# Phase 7.2 Schemas — Search Intelligence & Learning Engine
# ══════════════════════════════════════════════════════════════

class AutocompleteResult(BaseModel):
    text: str
    type: str  # 'title', 'company', 'skill', 'location'
    count: Optional[int] = None

class SearchSuggestion(BaseModel):
    suggestions: List[str]
    message: str = "Did you mean?"

class SearchLogCreate(BaseModel):
    query: str
    results_count: int = 0
    filters_used: Optional[Dict[str, Any]] = None

class SearchLogResponse(BaseModel):
    id: int
    query: str
    results_count: int
    clicked_job_id: Optional[int] = None
    click_position: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NormalizedLocationBase(BaseModel):
    raw_value: str
    city: str
    state: Optional[str] = None
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None

class NormalizedLocation(NormalizedLocationBase):
    id: int

    class Config:
        from_attributes = True

class RoleSkillMapCreate(BaseModel):
    role: str
    skill: str
    importance: str = "Required"
    category: Optional[str] = None

class RoleSkillMapResponse(BaseModel):
    role: str
    skills: List[Dict[str, str]]

class CertificationBase(BaseModel):
    name: str
    provider: str
    url: Optional[str] = None
    is_free: bool = False
    cost: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[int] = None
    validity_years: Optional[int] = None
    exam_required: bool = True
    skills_covered: Optional[List[str]] = []
    roles: Optional[List[str]] = []
    # Phase 9.7.1.5
    availability_status: Optional[str] = "VERIFIED"
    last_verified_at: Optional[datetime] = None
    currency: Optional[str] = None
    price_inr: Optional[int] = None
    affordability: Optional[str] = None
    free_learning_available: Optional[bool] = False
    financial_aid_available: Optional[bool] = False
    student_discount_available: Optional[bool] = False
    certification_type: Optional[str] = None
    verification_source: Optional[str] = None

class CertificationResponse(CertificationBase):
    id: int
    created_at: datetime

    @field_validator('skills_covered', mode='before')
    @classmethod
    def parse_skills_covered(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator('roles', mode='before')
    @classmethod
    def parse_roles(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    class Config:
        from_attributes = True

class LearningRecommendation(BaseModel):
    role: str
    required_skills: List[Dict[str, str]]
    missing_skills: Optional[List[str]] = []
    resources: List[LearningResourceResponse]
    certifications: List[CertificationResponse]
    match_type: Optional[str] = "Exact Role Match"

class CoverageReport(BaseModel):
    total_active_jobs: int
    total_verified_jobs: int
    total_unique_jobs: int
    total_archived_jobs: int
    jobs_by_ats: Dict[str, int]
    jobs_by_source: Dict[str, int]
    companies_active: int
    companies_failed: int
    failed_companies: List[str]
    duplicate_rate: float
    last_pipeline_run: Optional[datetime] = None


# Phase 7.3 Extensions
class JobQualityMetricsBase(BaseModel):
    quality_score: int = 0
    trust_score: int = 0
    verification_status: str = 'Pending'
    is_duplicate: bool = False
    is_official: bool = False
    salary_confidence: Optional[int] = None

class JobQualityMetrics(JobQualityMetricsBase):
    id: int
    opportunity_id: int
    last_verified: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CollectionLineageBase(BaseModel):
    source_type: str
    source_url: Optional[str] = None
    collector_name: str
    collector_version: str
    parser_version: str

class CollectionLineage(CollectionLineageBase):
    id: int
    opportunity_id: int
    collection_time: datetime
    verification_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobSourceBase(BaseModel):
    source_name: str
    source_type: str
    priority: int = 5
    country: str = 'India'
    is_official: bool = False
    is_active: bool = True
    health_score: int = 100

class JobSource(JobSourceBase):
    id: int
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    average_response_time: Optional[float] = None
    
    class Config:
        from_attributes = True

class CollectorHealthBase(BaseModel):
    collector_name: str
    status: str = 'Active'
    success_rate: float = 100.0
    avg_runtime: Optional[float] = None
    jobs_collected: int = 0
    duplicates_removed: int = 0
    errors: int = 0

class CollectorHealth(CollectorHealthBase):
    id: int
    last_run: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DashboardStatsCacheBase(BaseModel):
    total_jobs: int = 0
    active_jobs: int = 0
    verified_jobs: int = 0
    remote_jobs: int = 0
    freshers_jobs: int = 0
    internships: int = 0

class DashboardStatsCache(DashboardStatsCacheBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Phase 10.2 Schemas
class UserCareerProfileBase(BaseModel):
    target_role: str
    experience_level: Optional[str] = None
    current_role: Optional[str] = None
    education: Optional[str] = None
    location: Optional[str] = None

class UserCareerProfileCreate(UserCareerProfileBase):
    pass

class UserCareerProfileUpdate(UserCareerProfileBase):
    target_role: Optional[str] = None

class UserCareerProfile(UserCareerProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class UserSkillProfileBase(BaseModel):
    skill_name: str
    proficiency_level: Optional[str] = "BEGINNER"
    source: Optional[str] = "MANUAL"

class UserSkillProfileCreate(UserSkillProfileBase):
    pass

class UserSkillProfileUpdate(BaseModel):
    proficiency_level: Optional[str] = None
    skill_name: Optional[str] = None

class UserSkillProfile(UserSkillProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class CareerReadinessSnapshotBase(BaseModel):
    target_role: str
    readiness_score: int
    skill_coverage_score: int
    experience_score: int
    resume_score: int

class CareerReadinessSnapshot(CareerReadinessSnapshotBase):
    id: int
    user_id: int
    calculated_at: datetime
    class Config:
        from_attributes = True
        
class SkillGapAnalysisResponse(BaseModel):
    target_role: str
    required_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    partial_skills: List[str]
    coverage_percentage: float
    skill_gap_count: int
    
class CareerReadinessResponse(BaseModel):
    overall_score: int
    readiness_level: str
    skill_coverage: int
    profile_completeness: int
    experience_alignment: int
    learning_progress: int
    strengths: List[str]
    weaknesses: List[str]
    missing_skills: List[str]
    
class ResumeGapAnalysisResponse(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    skill_coverage: float
    role_alignment_score: int
    recommendations: List[str]


# Feedback Schemas
class FeedbackCreate(BaseModel):
    rating: Optional[int] = None
    category: str
    priority: Optional[str] = "Medium"
    subject: str
    description: str
    file_attachment: Optional[str] = None

class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    rating: Optional[int] = None
    category: str
    priority: str
    subject: str
    description: str
    file_attachment: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FeedbackStatsResponse(BaseModel):
    total_feedback: int
    resolved_count: int
    open_count: int
    in_review_count: int
    average_rating: float
    features_shipped: int
    avg_response_hours: str

