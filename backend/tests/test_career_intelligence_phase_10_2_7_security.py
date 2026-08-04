import sys
import os
import pytest
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, RoleSkillMap, UserCareerProfile, UserSkillProfile, CareerReadinessSnapshot, ResumeProfile
from app.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_data(db_session):
    u1 = User(email="audit1@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    db_session.add(u1)
    db_session.commit()
    db_session.refresh(u1)
    
    rsm1 = RoleSkillMap(role="QA Engineer", skill="Testing", importance="Required")
    db_session.add(rsm1)
    db_session.commit()
    
    return u1

def get_token(email):
    response = client.post("/api/auth/token", data={"username": email, "password": "password"})
    return response.json()["access_token"]

def test_unauthenticated_readiness():
    res = client.get("/api/readiness")
    assert res.status_code == 401

def test_duplicate_career_profile(setup_data, db_session):
    token = get_token("audit1@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create first
    res = client.post("/api/profile/career", json={"target_role": "QA Engineer"}, headers=headers)
    assert res.status_code == 200
    
    # Create duplicate
    res2 = client.post("/api/profile/career", json={"target_role": "Data Analyst"}, headers=headers)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_duplicate_skills(setup_data, db_session):
    token = get_token("audit1@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create first
    res = client.post("/api/profile/skills", json={"skill_name": "Testing", "proficiency_level": "ADVANCED"}, headers=headers)
    assert res.status_code == 200
    
    # Create duplicate
    res2 = client.post("/api/profile/skills", json={"skill_name": "testing", "proficiency_level": "BEGINNER"}, headers=headers)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

def test_readiness_missing_resume_and_experience(setup_data, db_session):
    u1 = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create career profile without experience
    db_session.add(UserCareerProfile(user_id=u1.id, target_role="QA Engineer"))
    # No skills, no resume
    db_session.commit()
    
    res = client.get("/api/readiness", headers=headers)
    assert res.status_code == 200
    card = res.json()["readiness_cards"][0]
    
    assert card["components"]["skill_coverage"] == 0
    assert card["components"]["resume_score"] == 0
    assert card["components"]["experience_score"] == 0
    assert card["readiness_score"] == 0
    assert card["target_role"] == "QA Engineer"

def test_readiness_snapshot_idempotency_and_immutability(setup_data, db_session):
    u1 = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Insert a historical snapshot (yesterday)
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    old_snap = CareerReadinessSnapshot(
        user_id=u1.id, target_role="QA Engineer", readiness_score=50,
        skill_coverage_score=50, experience_score=50, resume_score=50
    )
    old_snap.calculated_at = yesterday
    db_session.add(old_snap)
    db_session.commit()
    
    # Call readiness today
    res = client.get("/api/readiness", headers=headers)
    assert res.status_code == 200
    
    # Call again today (should not duplicate)
    res2 = client.get("/api/readiness", headers=headers)
    assert res2.status_code == 200
    
    snapshots = db_session.query(CareerReadinessSnapshot).filter(CareerReadinessSnapshot.user_id == u1.id).order_by(CareerReadinessSnapshot.calculated_at.asc()).all()
    
    # Should only have 2 snapshots: yesterday's and today's
    assert len(snapshots) == 2
    
    # Ensure yesterday's is immutable
    assert snapshots[0].readiness_score == 50
    assert snapshots[0].calculated_at.date() == yesterday.date()
    
    # Ensure today's was updated correctly
    today = datetime.datetime.utcnow().date()
    assert snapshots[1].calculated_at.date() == today
    assert snapshots[1].readiness_score == 0 # no skills or resume

def test_readiness_score_bounds(setup_data, db_session):
    # What if a user has partial match but the math somehow rounds up? It shouldn't exceed 100
    u1 = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Provide everything 100%
    db_session.add(UserCareerProfile(user_id=u1.id, target_role="QA Engineer", experience_level="Senior"))
    db_session.add(UserSkillProfile(user_id=u1.id, skill_name="Testing", proficiency_level="EXPERT"))
    db_session.add(ResumeProfile(user_id=u1.id, uploaded_file="test.pdf", ats_score=100))
    db_session.commit()
    
    res = client.get("/api/readiness", headers=headers)
    assert res.status_code == 200
    card = res.json()["readiness_cards"][0]
    
    assert card["components"]["skill_coverage"] == 100
    assert card["components"]["resume_score"] == 100
    assert card["components"]["experience_score"] == 100
    assert card["readiness_score"] == 100
