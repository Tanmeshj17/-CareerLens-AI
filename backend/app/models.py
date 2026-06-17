from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    applications = relationship("Application", back_populates="user")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    job_type = Column(String) # 'Full-time', 'Part-time', 'Internship', 'Contract'
    description = Column(Text)
    trust_score = Column(Integer)
    salary_range = Column(String, nullable=True)
    apply_url = Column(String, nullable=True)  # Direct apply link
    posted_date = Column(DateTime, default=datetime.utcnow)
    
    # Phase 2 columns
    opportunity_hash = Column(String, index=True, nullable=True)
    primary_source = Column(String, nullable=True)
    source_trust_score = Column(Integer, nullable=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Active")
    required_skills = Column(Text, nullable=True)
    
    applications = relationship("Application", back_populates="opportunity")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    status = Column(String, default="Saved") # 'Saved', 'Applied', 'Interview', 'Rejected', 'Selected'
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

class JobMatchScore(Base):
    __tablename__ = "job_match_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    match_score = Column(Integer)
    matching_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    match_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    opportunity = relationship("Opportunity")

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
    source_url = Column(String, nullable=True)
    raw_data = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)

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
