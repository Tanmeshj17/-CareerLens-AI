# Skill Taxonomy Mapping

# Maps specific skills to the primary roles that use them
SKILL_TO_ROLE_MAPPING = {
    # QA & Automation Testing
    "selenium": ["qa engineer", "qa automation engineer", "sdet", "software test engineer"],
    "cypress": ["qa engineer", "qa automation engineer", "sdet", "frontend developer"],
    "playwright": ["qa engineer", "qa automation engineer", "sdet", "software engineer"],
    "appium": ["mobile test engineer", "qa automation engineer", "sdet", "qa engineer"],
    "postman": ["qa engineer", "sdet", "backend developer", "api tester", "software engineer"],
    "restassured": ["qa automation engineer", "sdet", "backend developer", "qa engineer"],
    "rest assured": ["qa automation engineer", "sdet", "backend developer", "qa engineer"],
    "testng": ["qa automation engineer", "sdet", "qa engineer", "java developer"],
    "junit": ["qa automation engineer", "sdet", "java developer", "backend developer"],
    "pytest": ["qa automation engineer", "sdet", "python developer", "backend developer"],
    "cucumber": ["qa engineer", "qa automation engineer", "sdet", "business analyst"],
    "bdd": ["qa engineer", "qa automation engineer", "sdet"],
    "tdd": ["software engineer", "backend developer", "qa engineer", "sdet"],
    "test automation": ["qa automation engineer", "sdet", "qa engineer", "software test engineer"],
    "automation testing": ["qa automation engineer", "sdet", "qa engineer", "software test engineer"],
    "qa testing": ["qa engineer", "qa tester", "manual tester", "quality analyst"],
    "quality assurance": ["qa engineer", "qa tester", "manual tester", "quality analyst"],
    "manual testing": ["manual tester", "qa tester", "qa analyst", "functional tester"],
    "regression testing": ["qa engineer", "manual tester", "qa tester", "sdet"],
    "smoke testing": ["qa engineer", "manual tester", "qa tester", "sdet"],
    "api testing": ["qa engineer", "sdet", "backend developer", "api tester"],
    "testrail": ["qa engineer", "qa tester", "qa lead", "manual tester"],
    "jira": ["qa engineer", "scrum master", "software engineer", "product manager", "project manager"],
    "charles proxy": ["qa engineer", "mobile test engineer", "sdet"],
    "browserstack": ["qa engineer", "qa automation engineer", "frontend developer"],
    "saucelabs": ["qa automation engineer", "sdet", "qa engineer"],
    "robot framework": ["qa automation engineer", "sdet", "qa engineer"],

    # Performance Testing
    "jmeter": ["performance tester", "performance test engineer", "performance engineer", "qa engineer"],
    "apache jmeter": ["performance tester", "performance test engineer", "performance engineer"],
    "loadrunner": ["performance tester", "performance test engineer", "performance engineer"],
    "locust": ["performance tester", "performance engineer", "python developer"],
    "k6": ["performance tester", "performance engineer", "sdet", "devops engineer"],
    "gatling": ["performance tester", "performance engineer", "sdet"],
    "blazemeter": ["performance tester", "performance engineer"],
    "performance testing": ["performance tester", "performance test engineer", "performance engineer", "qa engineer"],
    "load testing": ["performance tester", "performance test engineer", "performance engineer"],
    "stress testing": ["performance tester", "performance test engineer", "performance engineer"],
    "endurance testing": ["performance tester", "performance engineer"],
    "scalability testing": ["performance tester", "performance engineer", "site reliability engineer"],

    # Software Engineering & Languages
    "python": ["python developer", "data engineer", "machine learning engineer", "backend developer", "software engineer", "data scientist", "sdet"],
    "sql": ["sql developer", "data analyst", "database engineer", "data engineer", "backend developer", "business intelligence analyst", "qa engineer"],
    "power bi": ["bi analyst", "data analyst", "reporting analyst", "business analyst"],
    "tableau": ["bi analyst", "data analyst", "reporting analyst", "business analyst"],
    "java": ["java developer", "backend developer", "software engineer", "sde", "full stack developer", "sdet"],
    "react": ["frontend developer", "full stack developer", "software engineer", "react developer"],
    "node.js": ["backend developer", "full stack developer", "node developer"],
    "aws": ["aws engineer", "cloud engineer", "devops engineer", "data engineer", "backend developer"],
    "azure": ["azure engineer", "cloud engineer", "devops engineer", "azure data engineer"],
    "spark": ["spark engineer", "big data engineer", "data engineer"],
    "machine learning": ["machine learning engineer", "data scientist", "ai engineer"],
    "excel": ["data analyst", "business analyst", "financial analyst", "manual tester"],
    "docker": ["devops engineer", "backend developer", "cloud engineer", "sre"],
    "kubernetes": ["devops engineer", "cloud engineer", "sre", "platform engineer"],
    "ci/cd": ["devops engineer", "sdet", "backend developer", "qa automation engineer"]
}

# Maps standard roles to the typical core skills they require (used for smart query skill expansion)
ROLE_TO_SKILLS_MAPPING = {
    "qa engineer": ["selenium", "cypress", "playwright", "postman", "test automation", "qa testing", "api testing", "jira", "sql", "testng", "junit", "pytest"],
    "sdet": ["selenium", "playwright", "cypress", "java", "python", "api testing", "postman", "restassured", "ci/cd", "docker", "data structures", "git"],
    "performance tester": ["jmeter", "loadrunner", "k6", "locust", "performance testing", "load testing", "stress testing", "gatling", "api testing", "grafana"],
    "performance test engineer": ["jmeter", "loadrunner", "k6", "locust", "performance testing", "load testing", "stress testing", "gatling", "api testing"],
    "manual tester": ["manual testing", "functional testing", "regression testing", "smoke testing", "test cases", "jira", "bug tracking", "api testing", "postman"],
    "qa automation engineer": ["selenium", "cypress", "playwright", "java", "python", "test automation", "testng", "pytest", "restassured", "git", "ci/cd"],
    "software engineer": ["python", "java", "c++", "javascript", "data structures", "algorithms", "system design", "sql", "git", "rest api"],
    "backend developer": ["python", "node.js", "java", "sql", "postgresql", "redis", "docker", "rest api", "microservices", "fastapi", "django", "spring boot"],
    "frontend developer": ["react", "javascript", "typescript", "html", "css", "tailwind", "next.js", "redux", "vue"],
    "data engineer": ["python", "sql", "spark", "airflow", "kafka", "dbt", "snowflake", "databricks", "bigquery", "aws", "etl"],
    "data analyst": ["sql", "python", "excel", "tableau", "power bi", "pandas", "statistics", "data visualization"],
    "machine learning engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp", "computer vision", "mlflow"],
    "data scientist": ["python", "r", "machine learning", "statistics", "pandas", "numpy", "sql", "data science"],
    "devops engineer": ["docker", "kubernetes", "terraform", "ansible", "aws", "azure", "ci/cd", "jenkins", "linux", "bash", "prometheus", "grafana"]
}

def get_roles_for_skill(query: str) -> list[str]:
    """Returns a list of roles associated with a given skill, if it exists in the taxonomy."""
    q = query.lower().strip()
    return SKILL_TO_ROLE_MAPPING.get(q, [])

def get_skills_for_role(query: str) -> list[str]:
    """Returns a list of core skills associated with a given role name or role query."""
    q = query.lower().strip()
    # Direct match
    if q in ROLE_TO_SKILLS_MAPPING:
        return ROLE_TO_SKILLS_MAPPING[q]
    
    # Partial match
    for role_key, skills in ROLE_TO_SKILLS_MAPPING.items():
        if role_key in q or q in role_key:
            return skills
            
    return []
