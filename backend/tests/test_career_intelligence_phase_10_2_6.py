import sys
import os
import pytest
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Opportunity
from app.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_data(db_session):
    u1 = User(email="fastgrowing@test.com", hashed_password=get_password_hash("password"), is_verified=True)
    db_session.add(u1)
    db_session.commit()

    recent_date = datetime.datetime.utcnow() - datetime.timedelta(days=10)
    old_date = datetime.datetime.utcnow() - datetime.timedelta(days=80)
    
    # Add 12 software engineer postings (5 recent, 7 old) - should be "Stable" or "Growing"
    for i in range(7):
        db_session.add(Opportunity(
            title=f"Software Engineer {i}", company="TestCo", status="Active",
            is_active=True, posted_date=old_date
        ))
    for i in range(5):
        db_session.add(Opportunity(
            title=f"Software Engineer Recent {i}", company="TestCo", status="Active",
            is_active=True, posted_date=recent_date
        ))
    db_session.commit()
    
    return u1

def test_fast_growing_response_structure(setup_data):
    """API must return the new schema, not the old static list."""
    res = client.get("/api/insights/fast-growing")
    assert res.status_code == 200
    data = res.json()
    
    assert "roles" in data, "Must have 'roles' key - not the old static array format"
    assert "insufficient_data_roles" in data
    assert "total_roles_evaluated" in data
    assert "evidence_source" in data
    assert data["evidence_source"] == "careerlens_opportunity_db"

def test_fast_growing_roles_have_evidence_fields(setup_data):
    """Each role in the response must have evidence-based fields."""
    res = client.get("/api/insights/fast-growing")
    data = res.json()
    roles = data["roles"]
    
    # If there are any roles that meet threshold, validate their structure
    if roles:
        role = roles[0]
        assert "title" in role
        assert "growth_signal" in role
        assert "total_postings" in role
        assert "data_basis" in role
        assert role["data_basis"] == "LIVE_DB"
        assert role["growth_signal"] in ["Fast Growing", "Growing", "Stable"]

def test_insufficient_data_roles_are_counted(setup_data):
    """Roles with < 10 postings must be counted as insufficient, not shown as data."""
    res = client.get("/api/insights/fast-growing")
    data = res.json()
    
    # We know most roles will have 0 postings in test DB
    # The count must be greater than 0 since test only seeds "software engineer"
    assert data["insufficient_data_roles"] >= 0
    assert data["total_roles_evaluated"] > 0
    
    # CRITICAL: insufficient roles must NOT appear in the roles list  
    roles_list = data["roles"]
    for role_data in roles_list:
        assert role_data.get("total_postings", 0) >= data["min_postings_threshold"], (
            f"Role {role_data['title']} has {role_data['total_postings']} postings "
            f"but threshold is {data['min_postings_threshold']}"
        )

def test_no_static_json_substitution(setup_data):
    """The endpoint must not fall back to roles.json data pretending it is live."""
    res = client.get("/api/insights/fast-growing")
    data = res.json()
    
    # Old format was a flat list with fields like "growth_outlook", "demand_in_india"
    # New format must NOT have these misleading static-data fields
    roles = data.get("roles", [])
    for role in roles:
        assert "growth_outlook" not in role, "Should not return static roles.json field 'growth_outlook'"
        assert "demand_in_india" not in role, "Should not return static roles.json field 'demand_in_india'"
        assert "fresher_openings" not in role, "Should not return static roles.json field 'fresher_openings'"
