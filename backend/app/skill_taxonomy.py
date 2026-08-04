# Skill Taxonomy Mapping

# Maps specific skills to the primary roles that use them
SKILL_TO_ROLE_MAPPING = {
    "python": ["python developer", "data engineer", "machine learning engineer", "backend developer", "software engineer", "data scientist"],
    "sql": ["sql developer", "data analyst", "database engineer", "data engineer", "backend developer", "business intelligence analyst"],
    "power bi": ["bi analyst", "data analyst", "reporting analyst", "business analyst"],
    "tableau": ["bi analyst", "data analyst", "reporting analyst", "business analyst"],
    "java": ["java developer", "backend developer", "software engineer", "sde", "full stack developer"],
    "react": ["frontend developer", "full stack developer", "software engineer", "react developer"],
    "node.js": ["backend developer", "full stack developer", "node developer"],
    "aws": ["aws engineer", "cloud engineer", "devops engineer", "data engineer", "backend developer"],
    "azure": ["azure engineer", "cloud engineer", "devops engineer", "azure data engineer"],
    "spark": ["spark engineer", "big data engineer", "data engineer"],
    "machine learning": ["machine learning engineer", "data scientist", "ai engineer"],
    "excel": ["data analyst", "business analyst", "financial analyst"]
}

def get_roles_for_skill(query: str) -> list[str]:
    """Returns a list of roles associated with a given skill, if it exists in the taxonomy."""
    q = query.lower().strip()
    return SKILL_TO_ROLE_MAPPING.get(q, [])
