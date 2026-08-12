import re
import io
import pdfplumber
import docx

# Expanded and robust taxonomy
SKILLS_DB = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "golang", "rust", "swift", "kotlin", "php", "sql", "r", "scala", "shell", "bash", "powershell", "html", "css", "sass", "less", "solidity", "dart", "perl", "haskell", "lua", "matlab", "objective-c", "assembly", "vba", "groovy",
    # Frontend
    "react", "angular", "vue", "vue.js", "next.js", "nuxt.js", "svelte", "jquery", "bootstrap", "tailwind", "tailwindcss", "material-ui", "mui", "redux", "zustand", "graphql", "apollo", "webpack", "vite", "npm", "yarn", "html5", "css3", "ember.js", "backbone.js", "lit", "alpine.js", "chakra ui",
    # Backend
    "fastapi", "flask", "django", "node.js", "express", "express.js", "spring", "spring boot", "ruby on rails", "rails", "asp.net", "laravel", "nest.js", "fastify", "celery", "gunicorn", "uvicorn", "koa", "hapi", "phoenix", "gin", "echo", "actix", "rocket",
    # Cloud & DevOps
    "aws", "amazon web services", "gcp", "google cloud", "azure", "kubernetes", "k8s", "docker", "terraform", "ansible", "jenkins", "git", "github", "gitlab", "ci/cd", "circleci", "prometheus", "grafana", "nginx", "apache", "linux", "unix", "vagrant", "heroku", "travis ci", "bitbucket", "argocd", "datadog", "new relic", "splunk", "elastic stack", "elk", "pulumi", "puppet", "chef", "openshift", "cloudformation",
    # Databases
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "mariadb", "oracle", "firebase", "couchdb", "neo4j", "supabase", "cockroachdb", "snowflake", "redshift", "bigquery", "clickhouse", "influxdb", "couchbase", "realm", "arango",
    # Data & ML
    "pandas", "numpy", "scipy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "nltk", "spacy", "spark", "hadoop", "hive", "airflow", "kafka", "dbt", "tableau", "power bi", "matplotlib", "seaborn", "pyspark", "databricks", "hugging face", "transformers", "langchain", "llamaindex", "llm", "genai", "generative ai", "computer vision", "nlp", "xgboost", "lightgbm", "mlflow",
    # Security
    "penetration testing", "pentesting", "cryptography", "oauth", "jwt", "saml", "owasp", "burp suite", "wireshark", "nmap", "metasploit", "iam", "siem", "soc", "firewall", "ids/ips", "kali linux", "zero trust", "devsecops",
    # Architecture & Concepts
    "microservices", "rest", "restful", "graphql", "grpc", "soap", "webhooks", "websocket", "serverless", "event-driven", "oop", "functional programming", "tdd", "bdd", "domain driven design", "ddd", "solid principles", "mvc",
    # Management & Soft Skills
    "agile", "scrum", "jira", "confluence", "trello", "gitflow", "product management", "project management", "communication", "leadership", "problem solving", "teamwork", "kanban", "sprint planning", "stakeholder management", "roadmap", "okr",
}

CERT_KEYWORDS = [
    "AWS Certified", "Solutions Architect", "Developer Associate", "SysOps Administrator",
    "Google Cloud Professional", "Cloud Digital Leader", "Azure Administrator", "Azure Developer",
    "CompTIA Security+", "CompTIA Network+", "CompTIA A+", "PMP", "Project Management Professional",
    "Certified Scrum Master", "CSM", "CKA", "Certified Kubernetes Administrator", "CKAD",
    "Terraform Associate", "Cisco Certified", "CCNA", "CCNP", "CISSP", "CEH", "Certified Ethical Hacker",
    "CISA", "CISM", "ITIL", "Salesforce Certified"
]

DEGREE_KEYWORDS = [
    r"b\.?tech", r"b\.?e\.?", r"b\.?s\.?", r"bachelor", r"m\.?tech", r"m\.?s\.?", r"master", r"ph\.?d\.?", r"doctorate", r"m\.?b\.?a\.?", r"diploma", r"b\.?c\.?a\.?", r"m\.?c\.?a\.?"
]

SECTION_HEADERS = {
    "education": ["education", "academic qualification", "academic background", "qualification"],
    "experience": ["experience", "employment", "work history", "work experience", "professional experience", "career history", "professional summary"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "skills": ["skills", "technical skills", "expertise", "core competencies", "technologies"],
    "certifications": ["certifications", "licenses", "certificates", "credentials"]
}

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    text = ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
                text += "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def format_skill_name(skill: str) -> str:
    formatting_map = {
        "aws": "AWS", "gcp": "GCP", "azure": "Azure", "ci/cd": "CI/CD", "k8s": "Kubernetes",
        "ml": "Machine Learning", "ai": "AI", "db": "Database", "sql": "SQL", "ui": "UI",
        "ux": "UX", "sre": "SRE", "mvc": "MVC", "spring boot": "Spring Boot", "node.js": "Node.js",
        "react": "React", "angular": "Angular", "vue": "Vue", "django": "Django", "python": "Python",
        "java": "Java", "c++": "C++", "c#": "C#", "docker": "Docker", "kubernetes": "Kubernetes",
        "html": "HTML", "css": "CSS", "javascript": "JavaScript", "typescript": "TypeScript",
        "php": "PHP", "ruby": "Ruby", "go": "Go", "golang": "Go", "rust": "Rust",
        "aws certified": "AWS Certified", "github": "GitHub", "gitlab": "GitLab",
        "postgresql": "PostgreSQL", "mysql": "MySQL", "mongodb": "MongoDB",
        "next.js": "Next.js", "express.js": "Express.js", "graphql": "GraphQL",
        "linux": "Linux", "unix": "Unix", "api": "API", "rest": "REST",
    }
    return formatting_map.get(skill, skill.title())

def parse_resume(file_bytes: bytes, filename: str) -> dict:
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        try:
            text = file_bytes.decode("utf-8")
        except:
            text = file_bytes.decode("latin1", errors="ignore")

    text_lower = text.lower()
    
    # Improved Skill Extraction
    extracted_skills_set = set()
    
    # For special characters like C++, C#, Node.js, Next.js, .NET we can't just use \b blindly
    # We use a custom regex approach
    for skill in SKILLS_DB:
        # Escape the skill for regex
        escaped_skill = re.escape(skill)
        
        # If the skill starts or ends with a non-word character (like C++, .NET), relax the boundary
        prefix_boundary = r"(?<![a-z0-9])" if not skill[0].isalnum() else r"\b"
        suffix_boundary = r"(?![a-z0-9])" if not skill[-1].isalnum() else r"\b"
        
        pattern = rf"{prefix_boundary}{escaped_skill}{suffix_boundary}"
        
        if re.search(pattern, text_lower):
            extracted_skills_set.add(format_skill_name(skill))

    extracted_skills = list(extracted_skills_set)

    # Experience Extraction (Heuristic)
    extracted_experience = []
    years_matches = re.findall(r'(\d+)\s*\+?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:experience)?', text_lower)
    total_years = 0
    if years_matches:
        try:
            total_years = max([int(y) for y in years_matches if int(y) < 40])
        except:
            pass

    # Projects Extraction (Heuristic)
    extracted_projects = []
    if "github.com" in text_lower:
        extracted_projects.append({"title": "Open Source / GitHub Repository", "description": "Linked in resume"})

    # Certifications
    extracted_certs = []
    for cert in CERT_KEYWORDS:
        if cert.lower() in text_lower:
            extracted_certs.append(cert)
    
    extracted_certs = list(set(extracted_certs))

    # Education
    extracted_edu = []
    for deg in DEGREE_KEYWORDS:
        if re.search(r'\b' + deg + r'\b', text_lower):
            extracted_edu.append({"degree": deg.replace('\\', '').replace('.', '').upper()})
    
    dedup_edu = []
    seen = set()
    for e in extracted_edu:
        d = e["degree"]
        if d not in seen:
            seen.add(d)
            dedup_edu.append(e)

    # Improved Scoring Logic
    # 1. Base Score for readable structure & contact info (30 points)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    base_score = 25
    if email_match: base_score += 5
    if phone_match: base_score += 5
    
    # 2. Skill Density Score (Up to 40 points)
    # 15+ skills = 40 pts, 10 skills = 30 pts, 5 skills = 20 pts
    num_skills = len(extracted_skills)
    if num_skills >= 15:
        skill_score = 40
    elif num_skills >= 10:
        skill_score = 32 + (num_skills - 10) * 1.5
    elif num_skills >= 5:
        skill_score = 20 + (num_skills - 5) * 2.4
    else:
        skill_score = num_skills * 4

    # 3. Impact Metrics & Action Keywords (Up to 20 points)
    # Broader pattern matching numbers, scale, percentages, and strong action verbs
    impact_matches = re.findall(r'(\d+%\b|\$\d+|\d+x\b|\b\d+\s*(?:tb|gb|mb|m|k|rows|users|pipelines|services|models|projects)\b|increased|decreased|reduced|improved|built|engineered|architected|optimized|scaled)', text_lower)
    impact_score = min(20, len(impact_matches) * 2)

    # 4. Certifications & Education Bonus (Up to 10 points)
    cert_score = 5 if extracted_certs else 0
    edu_score = 5 if dedup_edu else 0

    # Total ATS Score (Bounded 0 to 100)
    raw_ats_score = int(base_score + skill_score + impact_score + cert_score + edu_score)
    ats_score = max(35, min(98, raw_ats_score))

    # Dynamic Feedback Generation
    strengths = []
    weaknesses = []
    suggestions = []

    # 1. Evaluate Skills
    if len(extracted_skills) > 15:
        strengths.append(f"Excellent technical density with {len(extracted_skills)} industry skills detected.")
    elif len(extracted_skills) >= 8:
        strengths.append(f"Solid foundation with {len(extracted_skills)} key skills identified.")
    else:
        weaknesses.append("Low keyword density limits ATS visibility.")
        suggestions.append("Ensure technical skills are explicitly listed (e.g., 'Python' instead of 'scripting').")

    # 2. Evaluate Achievements / Metrics
    if achievement_score >= 15:
        strengths.append(f"Strong use of quantifiable metrics ({len(achievement_matches)} data points found).")
    elif achievement_score > 0:
        weaknesses.append("Some metrics found, but impact could be quantified more aggressively.")
        suggestions.append("Use the X-Y-Z formula: 'Accomplished [X] as measured by [Y], by doing [Z]'.")
    else:
        weaknesses.append("No quantifiable metrics or numbers detected in experience bullet points.")
        suggestions.append("Quantify your achievements! Add numbers to show scale (e.g., 'improved performance by 20%').")

    # 3. Evaluate Certifications
    if extracted_certs:
        strengths.append(f"Professional credentials verified: {', '.join(extracted_certs[:2])}")
    else:
        weaknesses.append("No recognizable industry certifications detected.")
        suggestions.append("Adding certifications (e.g., AWS Cloud Practitioner) can significantly boost ATS ranking.")

    # 4. Evaluate Layout / Formatting
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    
    if email_match and phone_match:
        strengths.append("Contact information is easily readable by ATS parsers.")
    else:
        weaknesses.append("Missing or improperly formatted contact information.")

    word_count = len(text.split())
    if word_count > 800:
        weaknesses.append(f"Resume is very dense ({word_count} words), which risks overwhelming recruiters.")
        suggestions.append("Trim your resume down to highlight only the most relevant, recent 3-5 years of experience.")
    elif word_count < 150:
        weaknesses.append("Resume is too brief and may lack sufficient detail for ATS keyword matching.")

    # Phase 7.3: Role matching and Gap Analysis
    import json, os
    matched_role = "General Software Engineer"
    missing_skills = []
    try:
        data_file = os.path.join(os.path.dirname(__file__), "..", "data", "roles.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                roles = json.load(f)
            
            best_match = None
            max_overlap = 0
            user_skills_lower = [s.lower() for s in extracted_skills]
            
            for r in roles:
                core_skills = r.get("core_skills", [])
                core_skills_lower = [s.lower() for s in core_skills]
                overlap = len(set(user_skills_lower).intersection(set(core_skills_lower)))
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_match = r
                    
            if best_match:
                matched_role = best_match["title"]
                core_skills_lower = [s.lower() for s in best_match["core_skills"]]
                missing = set(core_skills_lower) - set(user_skills_lower)
                
                for cs in best_match["core_skills"]:
                    if cs.lower() in missing:
                        missing_skills.append(cs)
                
                if missing_skills:
                    suggestions.append(f"To align perfectly with {matched_role} roles, consider adding: {', '.join(missing_skills[:3])}")
    except Exception as e:
        print(f"Error in gap analysis: {e}")

    # Ensure we always return at least some default feedback if nothing matched
    if not strengths: strengths.append("Formatting conforms to standard ATS guidelines.")
    if not weaknesses: weaknesses.append("No significant formatting issues detected.")
    if not suggestions: suggestions.append("Keep your skills section updated with the latest in-demand frameworks.")

    return {
        "uploaded_file": filename,
        "extracted_skills": extracted_skills,
        "extracted_projects": extracted_projects,
        "extracted_education": dedup_edu,
        "extracted_certifications": extracted_certs,
        "extracted_experience": extracted_experience,
        "ats_score": ats_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions
    }
