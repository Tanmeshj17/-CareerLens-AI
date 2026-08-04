import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.main import app
from app.database import Base, get_db
from app.auth import get_password_hash
import app.models as models

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_users(db_session):
    # Seed users
    user1 = models.User(email="test1@example.com", full_name="User One", hashed_password=get_password_hash("password123"), is_verified=True, role="user")
    user2 = models.User(email="test2@example.com", full_name="User Two", hashed_password=get_password_hash("password123"), is_verified=True, role="user")
    admin1 = models.User(email="admin@example.com", full_name="Admin", hashed_password=get_password_hash("password123"), is_verified=True, role="admin")
    unverified = models.User(email="unverified@example.com", full_name="Unverified", hashed_password=get_password_hash("password123"), is_verified=False, role="user")
    db_session.add_all([user1, user2, admin1, unverified])
    db_session.commit()
    
    # Give user 1 a resume
    resume1 = models.Resume(user_id=user1.id, filename="user1_resume.pdf", ats_score=80, skills_score=80, missing_skills="None")
    db_session.add(resume1)
    db_session.commit()


def test_login_unverified_blocked():
    response = client.post("/api/auth/token", data={"username": "unverified@example.com", "password": "password123"})
    assert response.status_code == 403
    assert "not verified" in response.json()["detail"]

def get_token(email):
    response = client.post("/api/auth/token", data={"username": email, "password": "password123"})
    return response.json()["access_token"]

def test_intelligence_endpoints_protected_from_anonymous():
    response = client.get("/api/intelligence/collectors")
    assert response.status_code == 401
    
    response = client.post("/api/intelligence/quality/audit")
    assert response.status_code == 401

def test_intelligence_endpoints_protected_from_regular_users():
    token = get_token("test1@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/intelligence/collectors", headers=headers)
    assert response.status_code == 403
    
    response = client.post("/api/intelligence/quality/audit", headers=headers)
    assert response.status_code == 403

def test_intelligence_endpoints_allow_admin():
    token = get_token("admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/intelligence/collectors", headers=headers)
    # 200 OK
    assert response.status_code == 200

def test_idor_prevention_resumes():
    token1 = get_token("test1@example.com")
    headers1 = {"Authorization": f"Bearer {token1}"}
    
    token2 = get_token("test2@example.com")
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # User 1 should see their own resume
    response = client.get("/api/resumes", headers=headers1)
    assert response.status_code == 200
    resumes = response.json()
    assert len(resumes) == 1
    resume_id = resumes[0]["id"]
    
    # User 2 tries to access User 1's profile
    # The endpoint will look for resume where id=resume_id AND user_id=User2.id
    response = client.get(f"/api/resumes/{resume_id}/profile", headers=headers2)
    assert response.status_code == 404 # 404 is correct, it shouldn't find it or leak existence

def test_password_length_validation():
    # Trying to register with a 5-char password should fail via Pydantic
    response = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "full_name": "New User",
        "password": "short"
    })
    assert response.status_code == 422
    assert "String should have at least 8 characters" in str(response.text)
