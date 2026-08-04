import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, UserCareerProfile, UserSkillProfile, ResumeProfile
from app.auth import get_password_hash
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_users(db_session):
    u1 = User(email="testuser1@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    u2 = User(email="testuser2@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)
    return u1, u2

def get_token(email):
    response = client.post("/api/auth/token", data={"username": email, "password": "password"})
    return response.json()["access_token"]

# --- Career Profile Tests ---
def test_unauthenticated_requests():
    assert client.get("/api/profile/career").status_code == 401
    assert client.post("/api/profile/career", json={"target_role": "Data Engineer"}).status_code == 401
    assert client.put("/api/profile/career", json={"target_role": "Data Engineer"}).status_code == 401
    assert client.get("/api/profile/skills").status_code == 401
    assert client.get("/api/profile/completeness").status_code == 401

def test_career_profile_crud(setup_users):
    u1, _ = setup_users
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get non-existent
    res = client.get("/api/profile/career", headers=headers)
    assert res.status_code == 404
    
    # 2. Create
    res = client.post("/api/profile/career", json={"target_role": "Data Engineer", "experience_level": "Mid"}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["target_role"] == "Data Engineer"
    assert data["experience_level"] == "Mid"
    
    # 3. Duplicate create handling
    res = client.post("/api/profile/career", json={"target_role": "Data Scientist"}, headers=headers)
    assert res.status_code == 400
    
    # 4. Get existing
    res = client.get("/api/profile/career", headers=headers)
    assert res.status_code == 200
    assert res.json()["target_role"] == "Data Engineer"
    
    # 5. Update
    res = client.put("/api/profile/career", json={"target_role": "Data Scientist", "location": "Bangalore"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["target_role"] == "Data Scientist"
    assert res.json()["location"] == "Bangalore"

def test_career_profile_isolation(setup_users):
    u1, u2 = setup_users
    t1 = get_token(u1.email)
    t2 = get_token(u2.email)
    
    client.post("/api/profile/career", json={"target_role": "Data Engineer"}, headers={"Authorization": f"Bearer {t1}"})
    
    # User 2 shouldn't see User 1's profile
    res = client.get("/api/profile/career", headers={"Authorization": f"Bearer {t2}"})
    assert res.status_code == 404
    
    # User 2 creates their own
    client.post("/api/profile/career", json={"target_role": "Software Engineer"}, headers={"Authorization": f"Bearer {t2}"})
    
    # User 1 should still see their own
    res = client.get("/api/profile/career", headers={"Authorization": f"Bearer {t1}"})
    assert res.json()["target_role"] == "Data Engineer"

# --- Skill Profile Tests ---
def test_skill_profile_crud(setup_users):
    u1, _ = setup_users
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Add skill
    res = client.post("/api/profile/skills", json={"skill_name": "Python", "proficiency_level": "BEGINNER"}, headers=headers)
    assert res.status_code == 200
    skill_id = res.json()["id"]
    
    # 2. Add duplicate skill
    res = client.post("/api/profile/skills", json={"skill_name": "python"}, headers=headers)
    assert res.status_code == 400
    
    # 3. Invalid proficiency
    res = client.post("/api/profile/skills", json={"skill_name": "Java", "proficiency_level": "MASTER"}, headers=headers)
    assert res.status_code == 400
    
    # 4. Update proficiency
    res = client.put(f"/api/profile/skills/{skill_id}?proficiency_level=ADVANCED", headers=headers)
    assert res.status_code == 200
    assert res.json()["proficiency_level"] == "ADVANCED"
    
    # 5. Delete skill
    res = client.delete(f"/api/profile/skills/{skill_id}", headers=headers)
    assert res.status_code == 200
    
    # 6. Verify deleted
    res = client.get("/api/profile/skills", headers=headers)
    assert len(res.json()) == 0

def test_skill_profile_isolation(setup_users):
    u1, u2 = setup_users
    t1 = get_token(u1.email)
    t2 = get_token(u2.email)
    
    res = client.post("/api/profile/skills", json={"skill_name": "Python"}, headers={"Authorization": f"Bearer {t1}"})
    skill_id = res.json()["id"]
    
    # User 2 tries to update User 1's skill
    res = client.put(f"/api/profile/skills/{skill_id}?proficiency_level=EXPERT", headers={"Authorization": f"Bearer {t2}"})
    assert res.status_code == 403
    
    # User 2 tries to delete User 1's skill
    res = client.delete(f"/api/profile/skills/{skill_id}", headers={"Authorization": f"Bearer {t2}"})
    assert res.status_code == 403

def test_profile_completeness(setup_users, db_session):
    u1, _ = setup_users
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Empty completeness
    res = client.get("/api/profile/completeness", headers=headers)
    assert res.status_code == 200
    data = res.json()
    print("COMPLETENESS DATA:", data)
    assert data["completeness_percentage"] == 20
    assert len(data["missing_items"]) > 0
    
    # 2. Add career profile
    client.post("/api/profile/career", json={"target_role": "DE", "experience_level": "Entry"}, headers=headers)
    res = client.get("/api/profile/completeness", headers=headers)
    assert res.json()["completeness_percentage"] == 40 # 20 (base) + 20 (career points: target+exp)
    
    # 3. Add skills (5 skills = 20 points)
    for s in ["Python", "SQL", "Airflow", "Spark", "AWS"]:
        client.post("/api/profile/skills", json={"skill_name": s}, headers=headers)
    res = client.get("/api/profile/completeness", headers=headers)
    assert res.json()["completeness_percentage"] == 60 # 40 + 20
    
    # 4. Add resume profile
    resume = ResumeProfile(user_id=u1.id, extracted_skills=["Python", "SQL"])
    db_session.add(resume)
    db_session.commit()
    
    res = client.get("/api/profile/completeness", headers=headers)
    # Resume base (15) + extracted_skills (15) = 30 points
    assert res.json()["completeness_percentage"] == 90
    assert len(res.json()["missing_items"]) == 0
