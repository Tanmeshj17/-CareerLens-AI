"""
Phase 11.4 T7: Skill Normalization (Expanded)
Normalizes 200+ skill variants to canonical forms.
No external dependencies — pure Python stdlib.

Examples:
  MS Excel → Excel
  Python3 → Python
  PowerBI → Power BI
  Spring Boot → Spring Boot (kept distinct)
  scikit learn → Scikit-learn
"""
import re
from typing import List, Set
import functools

# ─────────────────────────────────────────────────────────────
# Canonical skill aliases
# Format: "raw_variant_lower" → "Canonical Name"
# ─────────────────────────────────────────────────────────────
SKILL_ALIASES: dict[str, str] = {

    # ─── Python ───────────────────────────────────────────────
    "python": "Python",
    "python3": "Python",
    "python 3": "Python",
    "python programming": "Python",
    "python language": "Python",
    "python scripting": "Python",
    "python development": "Python",
    "core python": "Python",
    "advanced python": "Python",
    "python (programming language)": "Python",

    # ─── Java ─────────────────────────────────────────────────
    "java": "Java",
    "java programming": "Java",
    "core java": "Java",
    "java development": "Java",
    "java se": "Java",
    "java ee": "Java EE",
    "java 8": "Java",
    "java 11": "Java",
    "java 17": "Java",

    # ─── JavaScript ───────────────────────────────────────────
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "js": "JavaScript",
    "ecmascript": "JavaScript",
    "es6": "JavaScript",
    "es2015": "JavaScript",
    "vanilla js": "JavaScript",
    "vanilla javascript": "JavaScript",

    # ─── TypeScript ───────────────────────────────────────────
    "typescript": "TypeScript",
    "ts": "TypeScript",

    # ─── C/C++ ────────────────────────────────────────────────
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    "c": "C",
    "c language": "C",
    "c programming": "C",
    "c#": "C#",
    "csharp": "C#",
    "c sharp": "C#",
    "dotnet": ".NET",
    ".net": ".NET",
    "dot net": ".NET",
    "asp.net": "ASP.NET",
    "asp net": "ASP.NET",

    # ─── Go / Golang ──────────────────────────────────────────
    "go": "Go",
    "golang": "Go",
    "go lang": "Go",
    "go programming": "Go",

    # ─── Rust / Kotlin / Swift ────────────────────────────────
    "rust": "Rust",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "dart": "Dart",

    # ─── SQL & Databases ──────────────────────────────────────
    "sql": "SQL",
    "structured query language": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "postgre": "PostgreSQL",
    "postgresdb": "PostgreSQL",
    "sql server": "Microsoft SQL Server",
    "ms sql": "Microsoft SQL Server",
    "mssql": "Microsoft SQL Server",
    "microsoft sql server": "Microsoft SQL Server",
    "t-sql": "T-SQL",
    "transact-sql": "T-SQL",
    "sqlite": "SQLite",
    "oracle sql": "Oracle SQL",
    "oracle db": "Oracle SQL",
    "pl/sql": "PL/SQL",
    "nosql": "NoSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "firebase": "Firebase",
    "firestore": "Firestore",
    "neo4j": "Neo4j",
    "couchdb": "CouchDB",

    # ─── Excel & Office ───────────────────────────────────────
    "excel": "Excel",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "advance excel": "Excel",
    "advanced excel": "Excel",
    "excel vba": "Excel VBA",
    "vba": "Excel VBA",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "power-bi": "Power BI",
    "ms power bi": "Power BI",
    "microsoft power bi": "Power BI",
    "tableau": "Tableau",
    "tableau software": "Tableau",
    "qlikview": "QlikView",
    "qlik sense": "Qlik Sense",
    "looker": "Looker",
    "google data studio": "Google Looker Studio",
    "data studio": "Google Looker Studio",
    "looker studio": "Google Looker Studio",
    "ssrs": "SSRS",
    "ssis": "SSIS",
    "ssas": "SSAS",
    "word": "Microsoft Word",
    "ms word": "Microsoft Word",
    "powerpoint": "PowerPoint",
    "ms powerpoint": "PowerPoint",
    "microsoft powerpoint": "PowerPoint",
    "outlook": "Microsoft Outlook",
    "ms office": "Microsoft Office",
    "microsoft office": "Microsoft Office",
    "office 365": "Microsoft 365",
    "ms 365": "Microsoft 365",

    # ─── Cloud ────────────────────────────────────────────────
    "aws": "AWS",
    "amazon web services": "AWS",
    "amazon aws": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "ms azure": "Azure",

    # ─── DevOps ───────────────────────────────────────────────
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous delivery": "CI/CD",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "helm": "Helm",
    "linux": "Linux",
    "unix": "Unix",
    "bash": "Bash",
    "shell scripting": "Shell Scripting",
    "shell script": "Shell Scripting",
    "powershell": "PowerShell",
    "nginx": "Nginx",
    "apache": "Apache",

    # ─── Version Control ──────────────────────────────────────
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "svn": "SVN",
    "version control": "Version Control",

    # ─── Frontend / UI ────────────────────────────────────────
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "react native": "React Native",
    "reactnative": "React Native",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "AngularJS",
    "angular.js": "AngularJS",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "next js": "Next.js",
    "nuxtjs": "Nuxt.js",
    "nuxt.js": "Nuxt.js",
    "svelte": "Svelte",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "sass": "Sass",
    "scss": "SCSS",
    "jquery": "jQuery",

    # ─── Backend / API ────────────────────────────────────────
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring framework": "Spring",
    "laravel": "Laravel",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "ruby": "Ruby",
    "graphql": "GraphQL",
    "rest api": "REST API",
    "restful api": "REST API",
    "rest": "REST API",
    "restful": "REST API",
    "grpc": "gRPC",

    # ─── Machine Learning / AI ────────────────────────────────
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "artificial intelligence": "AI",
    "ai": "AI",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "tensorflow": "TensorFlow",
    "tensor flow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "plotly": "Plotly",
    "opencv": "OpenCV",
    "open cv": "OpenCV",
    "hugging face": "Hugging Face",
    "huggingface": "Hugging Face",
    "langchain": "LangChain",
    "llm": "LLM",
    "large language model": "LLM",
    "generative ai": "Generative AI",
    "gen ai": "Generative AI",
    "mlops": "MLOps",
    "ml ops": "MLOps",

    # ─── Data Engineering ─────────────────────────────────────
    "apache spark": "Apache Spark",
    "spark": "Apache Spark",
    "pyspark": "PySpark",
    "hadoop": "Hadoop",
    "hive": "Hive",
    "kafka": "Apache Kafka",
    "apache kafka": "Apache Kafka",
    "airflow": "Apache Airflow",
    "apache airflow": "Apache Airflow",
    "dbt": "dbt",
    "data build tool": "dbt",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "bigquery": "BigQuery",
    "google bigquery": "BigQuery",
    "etl": "ETL",
    "data pipeline": "Data Pipeline",
    "data warehouse": "Data Warehouse",
    "data lake": "Data Lake",
    "data engineering": "Data Engineering",

    # ─── CS Fundamentals ──────────────────────────────────────
    "data structures": "Data Structures",
    "dsa": "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "algorithms": "Algorithms",
    "oop": "OOP",
    "oops": "OOP",
    "object oriented programming": "OOP",
    "object-oriented programming": "OOP",
    "dbms": "DBMS",
    "database management": "DBMS",
    "os": "Operating Systems",
    "operating system": "Operating Systems",
    "cn": "Computer Networks",
    "computer networks": "Computer Networks",
    "networking": "Computer Networks",

    # ─── Agile / PM ───────────────────────────────────────────
    "agile": "Agile",
    "scrum": "Scrum",
    "kanban": "Kanban",
    "jira": "Jira",
    "confluence": "Confluence",

    # ─── Testing, QA & Performance Testing ────────────────────
    "selenium": "Selenium",
    "selenium webdriver": "Selenium",
    "playwright": "Playwright",
    "cypress": "Cypress",
    "cypress.io": "Cypress",
    "appium": "Appium",
    "unit testing": "Unit Testing",
    "pytest": "pytest",
    "junit": "JUnit",
    "testng": "TestNG",
    "mocha": "Mocha",
    "jest": "Jest",
    "postman": "Postman",
    "restassured": "REST Assured",
    "rest assured": "REST Assured",
    "soapui": "SoapUI",
    "jmeter": "JMeter",
    "apache jmeter": "JMeter",
    "loadrunner": "LoadRunner",
    "hp loadrunner": "LoadRunner",
    "gatling": "Gatling",
    "locust": "Locust",
    "k6": "k6",
    "blazemeter": "BlazeMeter",
    "manual testing": "Manual Testing",
    "automation testing": "Automation Testing",
    "test automation": "Automation Testing",
    "qa": "QA",
    "qa testing": "QA Testing",
    "quality assurance": "QA",
    "sdet": "SDET",
    "performance testing": "Performance Testing",
    "load testing": "Load Testing",
    "stress testing": "Stress Testing",
    "endurance testing": "Performance Testing",
    "spike testing": "Performance Testing",
    "regression testing": "Regression Testing",
    "smoke testing": "Smoke Testing",
    "sanity testing": "Sanity Testing",
    "functional testing": "Functional Testing",
    "api testing": "API Testing",
    "testrail": "TestRail",
    "zephyr": "Zephyr",
    "xray": "Xray",
    "cucumber": "Cucumber",
    "bdd": "BDD",
    "tdd": "TDD",
    "robot framework": "Robot Framework",
    "charles proxy": "Charles Proxy",
    "browserstack": "BrowserStack",
    "saucelabs": "SauceLabs",
    "uat": "UAT",

    # ─── Soft Skills ──────────────────────────────────────────
    "communication": "Communication",
    "communication skills": "Communication",
    "teamwork": "Teamwork",
    "problem solving": "Problem Solving",
    "leadership": "Leadership",
    "critical thinking": "Critical Thinking",
    "analytical skills": "Analytical Thinking",
    "analytical thinking": "Analytical Thinking",
    "time management": "Time Management",
    "project management": "Project Management",
}


@functools.lru_cache(maxsize=4096)
def normalize_skill(skill: str) -> str:
    """Normalizes a single skill string to its canonical form."""
    if not skill:
        return ""
    s = skill.lower().strip()
    # Remove trailing punctuation
    s = re.sub(r'[,;.\s]+$', '', s)
    return SKILL_ALIASES.get(s, skill.strip())


def normalize_skills_list(skills: List[str]) -> List[str]:
    """Normalizes a list of skills, removing duplicates while preserving order."""
    if not skills:
        return []
    seen: Set[str] = set()
    result = []
    for s in skills:
        ns = normalize_skill(s)
        if ns and ns.lower() not in seen:
            seen.add(ns.lower())
            result.append(ns)
    return result


def normalize_skills_string(skills_csv: str) -> str:
    """Normalize a comma-separated skills string."""
    if not skills_csv:
        return ""
    raw = [s.strip() for s in skills_csv.split(",") if s.strip()]
    return ", ".join(normalize_skills_list(raw))


def get_alias_count() -> int:
    """Return total number of skill aliases."""
    return len(SKILL_ALIASES)
