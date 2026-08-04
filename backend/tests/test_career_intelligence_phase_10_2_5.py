import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, RoleSkillMap, UserCareerProfile, UserSkillProfile, ResumeProfile, CareerReadinessSnapshot
from app.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_data(db_session):
    u1 = User(email="readiness1@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    db_session.add(u1)
    db_session.commit()
    db_session.refresh(u1)
    
    # Target Role mapping
    rsm1 = RoleSkillMap(role="Backend Engineer", skill="Python", importance="Required")
    rsm2 = RoleSkillMap(role="Backend Engineer", skill="Docker", importance="Required")
    db_session.add_all([rsm1, rsm2])
    
    # User Career Profile
    cp1 = UserCareerProfile(user_id=u1.id, target_role="Backend Engineer", experience_level="1-3 years")
    db_session.add(cp1)
    
    # User Skills (Python=INTERMEDIATE -> match, Docker=BEGINNER -> partial)
    s1 = UserSkillProfile(user_id=u1.id, skill_name="Python", proficiency_level="INTERMEDIATE")
    s2 = UserSkillProfile(user_id=u1.id, skill_name="Docker", proficiency_level="BEGINNER")
    db_session.add_all([s1, s2])
    
    # User Resume Profile
    rp1 = ResumeProfile(user_id=u1.id, uploaded_file="res.pdf", ats_score=90)
    db_session.add(rp1)
    db_session.commit()
    
    return u1

def get_token(email):
    response = client.post("/api/auth/token", data={"username": email, "password": "password"})
    return response.json()["access_token"]

def test_career_readiness_snapshot(setup_data, db_session):
    u1 = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.get("/api/readiness", headers=headers)
    assert res.status_code == 200
    data = res.json()
    
    assert "readiness_cards" in data
    cards = data["readiness_cards"]
    assert len(cards) == 1
    card = cards[0]
    
    assert card["target_role"] == "Backend Engineer"
    # components calculation:
    # skill_coverage: 1 full, 1 partial out of 2 = 1.5 / 2 = 75%
    # resume_score: 90
    # experience_score: 100
    # readiness_score: (75 * 0.5) + (90 * 0.4) + (100 * 0.1) = 37.5 + 36 + 10 = 83
    assert card["components"]["skill_coverage"] == 75
    assert card["components"]["resume_score"] == 90
    assert card["components"]["experience_score"] == 100
    assert card["readiness_score"] == 83
    
    # Check DB snapshot
    snapshots = db_session.query(CareerReadinessSnapshot).filter(CareerReadinessSnapshot.user_id == u1.id).all()
    assert len(snapshots) == 1
    snap = snapshots[0]
    assert snap.target_role == "Backend Engineer"
    assert snap.readiness_score == 83
    assert snap.skill_coverage_score == 75
    assert snap.experience_score == 100
    assert snap.resume_score == 90
