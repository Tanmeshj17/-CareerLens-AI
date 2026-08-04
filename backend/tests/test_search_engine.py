"""
Phase 8.65 - Search Engine Tests
Tests multi-level search, skill intent, and experience parser
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.role_taxonomy import expand_role, ROLE_TAXONOMY
from app.skill_taxonomy import get_roles_for_skill
from app.experience_parser import parse_experience
from app.search_engine import detect_search_intent


def test_role_expansion():
    # Direct family
    result = expand_role("data analyst")
    assert "junior data analyst" in result, f"Expected 'junior data analyst' in {result}"
    assert "bi analyst" in result, f"Expected 'bi analyst' in {result}"
    print("✅ test_role_expansion PASSED")

def test_reverse_role_lookup():
    # ETL Developer should expand to data engineer family
    result = expand_role("etl developer")
    assert "data engineer" in result, f"Expected 'data engineer' in {result}"
    assert "spark engineer" in result, f"Expected 'spark engineer' in {result}"
    print("✅ test_reverse_role_lookup PASSED")

def test_unknown_role_fallback():
    result = expand_role("chef de cuisine")
    assert result == ["chef de cuisine"], f"Expected fallback, got {result}"
    print("✅ test_unknown_role_fallback PASSED")

def test_skill_intent_python():
    roles = get_roles_for_skill("python")
    assert "data engineer" in roles, f"Expected 'data engineer' in {roles}"
    assert "machine learning engineer" in roles, f"Expected 'machine learning engineer' in {roles}"
    print("✅ test_skill_intent_python PASSED")

def test_skill_intent_power_bi():
    roles = get_roles_for_skill("power bi")
    assert "bi analyst" in roles, f"Expected 'bi analyst' in {roles}"
    assert "data analyst" in roles, f"Expected 'data analyst' in {roles}"
    print("✅ test_skill_intent_power_bi PASSED")

def test_experience_fresher():
    min_exp, max_exp, cat = parse_experience("Fresher")
    assert min_exp == 0 and cat == 'Fresher', f"Got ({min_exp}, {max_exp}, {cat})"
    print("✅ test_experience_fresher PASSED")

def test_experience_range():
    min_exp, max_exp, cat = parse_experience("2-4 years")
    assert min_exp == 2 and max_exp == 4, f"Got ({min_exp}, {max_exp}, {cat})"
    assert cat == "Junior", f"Got category {cat}"
    print("✅ test_experience_range PASSED")

def test_experience_plus():
    min_exp, max_exp, cat = parse_experience("5+ years")
    assert min_exp == 5, f"Got min {min_exp}"
    assert cat == "Mid", f"Got category {cat}"
    print("✅ test_experience_plus PASSED")

def test_search_intent_role():
    intent = detect_search_intent("data analyst")
    assert intent["type"] == "role", f"Expected role intent, got {intent}"
    print("✅ test_search_intent_role PASSED")

def test_search_intent_skill():
    intent = detect_search_intent("python")
    assert intent["type"] == "skill", f"Expected skill intent, got {intent}"
    assert "data engineer" in intent["roles"]
    print("✅ test_search_intent_skill PASSED")

if __name__ == "__main__":
    print("\n=== Phase 8.65 Search Engine Tests ===\n")
    test_role_expansion()
    test_reverse_role_lookup()
    test_unknown_role_fallback()
    test_skill_intent_python()
    test_skill_intent_power_bi()
    test_experience_fresher()
    test_experience_range()
    test_experience_plus()
    test_search_intent_role()
    test_search_intent_skill()
    print("\n✅ All tests passed.\n")
