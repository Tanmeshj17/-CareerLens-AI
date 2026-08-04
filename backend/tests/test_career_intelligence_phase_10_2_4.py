import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, RoleSkillMap, Resume, ResumeProfile, UserCareerProfile
from app.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_data(db_session):
    u1 = User(email="resumeuser1@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    u2 = User(email="resumeuser2@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)
    
    # Target Role mapping
    rsm1 = RoleSkillMap(role="Data Engineer", skill="Python", importance="Required")
    rsm2 = RoleSkillMap(role="Data Engineer", skill="SQL", importance="Required")
    rsm3 = RoleSkillMap(role="Data Engineer", skill="Airflow", importance="Required")
    db_session.add_all([rsm1, rsm2, rsm3])
    
    # User 1 Career Profile
    cp1 = UserCareerProfile(user_id=u1.id, target_role="Data Engineer")
    db_session.add(cp1)
    
    # User 1 Resume
    res1 = Resume(user_id=u1.id, filename="user1_resume.pdf")
    db_session.add(res1)
    db_session.commit()
    
    # User 1 Resume Profile
    rp1 = ResumeProfile(user_id=u1.id, uploaded_file="user1_resume.pdf", extracted_skills=["Python", "Java", "Docker"], ats_score=80)
    db_session.add(rp1)
    db_session.commit()
    db_session.refresh(res1)
    
    return u1, u2, res1

def get_token(email):
    response = client.post("/api/auth/token", data={"username": email, "password": "password"})
    return response.json()["access_token"]

def test_resume_gap_analysis(setup_data):
    u1, u2, res1 = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.get(f"/api/resumes/{res1.id}/gap-analysis", headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    assert data["target_role"] == "Data Engineer"
    assert "Python" in data["matching_skills"]
    assert "SQL" in data["missing_skills"]
    assert "Airflow" in data["missing_skills"]
    assert len(data["matching_skills"]) == 1
    assert len(data["missing_skills"]) == 2
    assert "coverage_percentage" in data

def test_resume_gap_analysis_idor(setup_data):
    u1, u2, res1 = setup_data
    token2 = get_token(u2.email)
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # u2 tries to access u1's resume gap analysis
    res = client.get(f"/api/resumes/{res1.id}/gap-analysis", headers=headers2)
    assert res.status_code == 404 # Isolated
