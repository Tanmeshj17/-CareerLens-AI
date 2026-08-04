import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, RoleSkillMap, UserSkillProfile
from app.auth import get_password_hash
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_data(db_session):
    u1 = User(email="skilluser1@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    u2 = User(email="skilluser2@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)
    
    # Create Role Skill Map for Data Engineer
    rsm1 = RoleSkillMap(role="Data Engineer", skill="Python", importance="Required")
    rsm2 = RoleSkillMap(role="Data Engineer", skill="SQL", importance="Required")
    rsm3 = RoleSkillMap(role="Data Engineer", skill="Airflow", importance="Required")
    rsm4 = RoleSkillMap(role="Data Engineer", skill="Spark", importance="Preferred") # not required
    db_session.add_all([rsm1, rsm2, rsm3, rsm4])
    db_session.commit()
    
    return u1, u2

def get_token(email):
    response = client.post("/api/auth/token", data={"username": email, "password": "password"})
    return response.json()["access_token"]

def test_unauthenticated_skills():
    assert client.get("/api/skills/gap-analysis?target_role=Data+Engineer").status_code == 401

def test_zero_skills(setup_data):
    u1, _ = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.get("/api/skills/gap-analysis?target_role=Data Engineer", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["target_role"] == "Data Engineer"
    assert len(data["required_skills"]) == 3
    assert len(data["matched_skills"]) == 0
    assert len(data["missing_skills"]) == 3
    assert len(data["partial_skills"]) == 0
    assert data["coverage_percentage"] == 0.0
    assert data["skill_gap_count"] == 3

def test_partial_match(setup_data, db_session):
    u1, _ = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    s1 = UserSkillProfile(user_id=u1.id, skill_name="Python", proficiency_level="BEGINNER")
    s2 = UserSkillProfile(user_id=u1.id, skill_name="SQL", proficiency_level="INTERMEDIATE")
    db_session.add_all([s1, s2])
    db_session.commit()
    
    res = client.get("/api/skills/gap-analysis?target_role=Data Engineer", headers=headers)
    data = res.json()
    
    # Python is beginner -> partial
    # SQL is intermediate -> matched
    # Airflow -> missing
    assert "Python" in data["partial_skills"]
    assert "SQL" in data["matched_skills"]
    assert "Airflow" in data["missing_skills"]
    
    # 1 matched (1.0), 1 partial (0.5), out of 3 = 1.5/3.0 = 50%
    assert data["coverage_percentage"] == 50.0
    assert data["skill_gap_count"] == 2 # missing + partial

def test_fully_matched(setup_data, db_session):
    u1, _ = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    s1 = UserSkillProfile(user_id=u1.id, skill_name="Python", proficiency_level="EXPERT")
    s2 = UserSkillProfile(user_id=u1.id, skill_name="SQL", proficiency_level="ADVANCED")
    s3 = UserSkillProfile(user_id=u1.id, skill_name="Airflow", proficiency_level="INTERMEDIATE")
    db_session.add_all([s1, s2, s3])
    db_session.commit()
    
    res = client.get("/api/skills/gap-analysis?target_role=Data Engineer", headers=headers)
    data = res.json()
    assert len(data["matched_skills"]) == 3
    assert len(data["partial_skills"]) == 0
    assert len(data["missing_skills"]) == 0
    assert data["coverage_percentage"] == 100.0
    assert data["skill_gap_count"] == 0

def test_unknown_role(setup_data):
    u1, _ = setup_data
    token = get_token(u1.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.get("/api/skills/gap-analysis?target_role=Quantum Developer", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["target_role"] == "Quantum Developer"
    assert len(data["required_skills"]) == 0
    assert data["coverage_percentage"] == 0.0

def test_idor_isolation(setup_data, db_session):
    u1, u2 = setup_data
    t1 = get_token(u1.email)
    t2 = get_token(u2.email)
    
    # u1 is fully matched
    s1 = UserSkillProfile(user_id=u1.id, skill_name="Python", proficiency_level="EXPERT")
    s2 = UserSkillProfile(user_id=u1.id, skill_name="SQL", proficiency_level="ADVANCED")
    s3 = UserSkillProfile(user_id=u1.id, skill_name="Airflow", proficiency_level="INTERMEDIATE")
    db_session.add_all([s1, s2, s3])
    db_session.commit()
    
    res1 = client.get("/api/skills/gap-analysis?target_role=Data Engineer", headers={"Authorization": f"Bearer {t1}"})
    assert res1.json()["coverage_percentage"] == 100.0
    
    # u2 has zero skills, calling same endpoint doesn't see u1's skills
    res2 = client.get("/api/skills/gap-analysis?target_role=Data Engineer", headers={"Authorization": f"Bearer {t2}"})
    assert res2.json()["coverage_percentage"] == 0.0
