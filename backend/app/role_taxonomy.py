# Role Taxonomy Mapping

ROLE_TAXONOMY = {
    "qa engineer": [
        "qa engineer",
        "quality assurance engineer",
        "sdet",
        "software development engineer in test",
        "software test engineer",
        "test automation engineer",
        "automation tester",
        "qa automation engineer",
        "qa tester",
        "test engineer",
        "quality analyst",
        "quality engineer",
        "qa specialist",
        "qa lead",
        "test lead"
    ],
    "performance tester": [
        "performance tester",
        "performance test engineer",
        "performance engineer",
        "load tester",
        "load testing engineer",
        "stress testing engineer",
        "performance qa engineer",
        "performance testing analyst",
        "jmeter engineer",
        "performance lead"
    ],
    "manual tester": [
        "manual tester",
        "manual qa tester",
        "qa tester",
        "functional tester",
        "software tester",
        "quality assurance tester",
        "qa analyst",
        "manual test engineer",
        "test associate",
        "user acceptance tester",
        "uat tester"
    ],
    "data analyst": [
        "data analyst",
        "junior data analyst",
        "senior data analyst",
        "business analyst",
        "business data analyst",
        "bi analyst",
        "business intelligence analyst",
        "sql analyst",
        "reporting analyst",
        "analytics consultant",
        "analytics associate",
        "data science analyst"
    ],
    "data engineer": [
        "data engineer",
        "junior data engineer",
        "senior data engineer",
        "etl developer",
        "data platform engineer",
        "big data engineer",
        "spark engineer",
        "azure data engineer",
        "aws data engineer",
        "gcp data engineer",
        "cloud data engineer"
    ],
    "software engineer": [
        "software engineer",
        "sde",
        "sde 1",
        "sde 2",
        "sde 3",
        "sde-1",
        "sde-2",
        "sde-3",
        "software developer",
        "backend developer",
        "full stack developer",
        "frontend developer",
        "python developer",
        "java developer",
        "c++ developer",
        "systems engineer",
        "programmer analyst"
    ],
    "machine learning engineer": [
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "artificial intelligence engineer",
        "deep learning engineer",
        "nlp engineer",
        "computer vision engineer",
        "mlops engineer"
    ],
    "data scientist": [
        "data scientist",
        "applied scientist",
        "research scientist",
        "decision scientist",
        "machine learning scientist"
    ],
    "product manager": [
        "product manager",
        "technical product manager",
        "associate product manager",
        "apm",
        "senior product manager",
        "product owner"
    ],
    "devops engineer": [
        "devops engineer",
        "site reliability engineer",
        "sre",
        "platform engineer",
        "cloud engineer",
        "infrastructure engineer",
        "build and release engineer",
        "ci/cd engineer"
    ],
    "cybersecurity analyst": [
        "cybersecurity analyst",
        "security analyst",
        "information security analyst",
        "soc analyst",
        "penetration tester",
        "pen tester",
        "security engineer",
        "vulnerability analyst"
    ]
}

def expand_role(normalized_query: str) -> list[str]:
    """Expands a normalized query into a list of related roles in its family."""
    q = normalized_query.lower().strip()
    # Direct lookup
    if q in ROLE_TAXONOMY:
        return ROLE_TAXONOMY[q]
        
    # Reverse lookup (if user types 'sdet' or 'load tester', expand to testing family)
    for family, roles in ROLE_TAXONOMY.items():
        if q in roles or any(q in r or r in q for r in roles):
            return roles
            
    # Default fallback - return the query itself
    return [q]
