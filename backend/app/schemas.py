from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

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
    description: str
    trust_score: int
    salary_range: Optional[str] = None
    apply_url: Optional[str] = None
    opportunity_hash: Optional[str] = None
    primary_source: Optional[str] = None
    source_trust_score: Optional[int] = None
    status: Optional[str] = "Active"
    required_skills: Optional[str] = None

class OpportunityCreate(OpportunityBase):
    pass

class Opportunity(OpportunityBase):
    id: int
    posted_date: datetime
    last_checked: Optional[datetime] = None

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
    opportunity: Opportunity

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
