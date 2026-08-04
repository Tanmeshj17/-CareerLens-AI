import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import RoleSkillMap, LearningResource, Certification
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_data(db_session):
    # Seed data required by the tests
    rs1 = RoleSkillMap(role="Data Engineer", skill="Python", importance="High", category="Programming")
    rs2 = RoleSkillMap(role="Data Analyst", skill="SQL", importance="High", category="Database")
    rs3 = RoleSkillMap(role="DevOps Engineer", skill="Docker", importance="High", category="Tools")
    rs4 = RoleSkillMap(role="Full Stack Developer", skill="React", importance="High", category="Frontend")
    rs5 = RoleSkillMap(role="Software Engineer", skill="Java", importance="High", category="Programming")
    
    lr1 = LearningResource(title="Python for Data Engineering", provider="Coursera", url="http://test.com/de", category="Course", skills_covered=["Python", "SQL", "Airflow"], country="India", availability_status="VERIFIED", price="0", currency="INR")
    lr2 = LearningResource(title="React Full Stack", provider="Udemy", url="http://test.com/fs", category="Course", skills_covered=["React", "JavaScript", "Web"], country="India", availability_status="VERIFIED", price="0", currency="INR")
    lr3 = LearningResource(title="Broken Software Course", provider="BrokenSite", url="http://test.com/broken", category="Course", skills_covered=["Java"], availability_status="BROKEN", price="0", currency="INR")
    lr4 = LearningResource(title="Python for Beginners", provider="YouTube", url="http://test.com/pb", category="Course", skills_covered=["Python"], availability_status="VERIFIED", price="0", currency="INR")
    
    c1 = Certification(name="Free Data Analyst Cert", provider="Google", url="http://test.com/da", skills_covered=["SQL"], price_inr=0, affordability="FREE", availability_status="VERIFIED")
    c2 = Certification(name="Expensive DevOps Cert", provider="AWS", url="http://test.com/devops", skills_covered=["Docker"], price_inr=10000, affordability="EXPENSIVE", availability_status="VERIFIED")
    
    db_session.add_all([rs1, rs2, rs3, rs4, rs5, lr1, lr2, lr3, lr4, c1, c2])
    db_session.commit()


def test_data_engineer_relevance():
    response = client.get("/api/learning/recommendations?role=Data%20Engineer")
    assert response.status_code == 200
    resources = response.json()["resources"]
    assert len(resources) > 0
    top_resource = resources[0]
    assert "Data Analyst" not in top_resource["title"]

def test_broken_resources_excluded():
    response = client.get("/api/learning/recommendations?role=Data%20Engineer")
    assert response.status_code == 200
    resources = response.json()["resources"]
    for r in resources:
        assert r.get("availability_status") in ["VERIFIED", "VERIFICATION_LIMITED"]

def test_api_transparency_fields_present():
    response = client.get("/api/learning/recommendations?role=Full%20Stack%20Developer")
    assert response.status_code == 200
    resources = response.json()["resources"]
    assert len(resources) > 0
    top_resource = resources[0]
    assert "match_reason" in top_resource
    assert "matched_skills" in top_resource
    assert "verification_confidence" in top_resource

def test_free_learning_is_not_labeled_as_free_certification():
    response = client.get("/api/learning/recommendations?role=Data%20Analyst")
    assert response.status_code == 200
    certs = response.json().get("certifications", [])
    for c in certs:
        if c.get("affordability") == "FREE":
            assert c.get("price_inr", 0) == 0

def test_generic_resource_overreach():
    response = client.get("/api/learning/recommendations?role=Data%20Engineer")
    assert response.status_code == 200
    resources = response.json()["resources"]
    assert len(resources) > 0
    top_resource = resources[0]
    assert "python for beginners" not in top_resource.get("title", "").lower()
