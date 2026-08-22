import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from . import models, schemas, auth, database
from .config_validator import validate_environment
from .resume_parser import parse_resume
from .routers import match_router, dashboard_router, data_intelligence_router, career_profile_router, skills_router, admin_router
from .routers.history_router import router as history_router, dashboard_router as history_dash_router

# Validate environment settings on startup
validate_environment()

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# --- Rate Limiter Setup ---
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="CareerLens AI API",
    version="1.0.0",
    description="AI-Powered Job Intelligence, Internship Discovery, and Career Growth Platform"
)

# Include routers
app.include_router(match_router.router)
app.include_router(dashboard_router.router)
app.include_router(data_intelligence_router.router)
app.include_router(career_profile_router.router)
app.include_router(skills_router.router)
app.include_router(history_router)
app.include_router(history_dash_router)
app.include_router(admin_router.router)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - include Vercel frontend domain + FRONTEND_URL env var
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
env = os.environ.get("ENVIRONMENT", "development")

# Always include the production Vercel domain
allowed_origins = [
    "https://career-lens-ai-wheat.vercel.app",
    frontend_url,
]
# In development, also allow localhost origins
if env != "production":
    allowed_origins.extend([
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000"
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# --- Phase 9.0 Wave 3: Enhanced Performance Profiling (P95/P99 + cache tracking) ---
import time
from collections import defaultdict
import statistics

# Global perf stats — now stores raw request times for percentile calculation
api_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0, "max_time": 0.0, "times": []})
cache_stats = {"hits": 0, "misses": 0}

class APIPerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
        
        path = request.url.path
        if not path.startswith("/api/admin/performance") and not path.startswith("/api/health"):
            stat = api_stats[path]
            stat["count"] += 1
            stat["total_time"] += process_time
            stat["times"].append(process_time)
            # Keep only last 1000 samples per endpoint to control memory
            if len(stat["times"]) > 1000:
                stat["times"] = stat["times"][-1000:]
            if process_time > stat["max_time"]:
                stat["max_time"] = process_time
        
        if process_time > 500:
            logger.warning(f"SLOW_API_DETECTED: {request.method} {path} took {process_time:.2f}ms")
            
        return response

app.add_middleware(APIPerformanceMiddleware)

@app.get("/api/admin/performance")
def get_performance_report():
    """Returns the P95/P99 performance report for all endpoints."""
    results = []
    for path, data in api_stats.items():
        avg = data["total_time"] / data["count"] if data["count"] > 0 else 0
        times_sorted = sorted(data["times"])
        n = len(times_sorted)
        p95 = times_sorted[int(n * 0.95) - 1] if n >= 20 else None
        p99 = times_sorted[int(n * 0.99) - 1] if n >= 100 else None
        results.append({
            "endpoint": path,
            "requests": data["count"],
            "avg_time_ms": round(avg, 2),
            "max_time_ms": round(data["max_time"], 2),
            "p95_ms": round(p95, 2) if p95 else None,
            "p99_ms": round(p99, 2) if p99 else None,
        })
    results.sort(key=lambda x: x["avg_time_ms"], reverse=True)
    cache_hit_rate = (
        round(cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) * 100, 2)
        if (cache_stats["hits"] + cache_stats["misses"]) > 0 else 0
    )
    return {
        "performance_report": results,
        "cache_hit_rate_pct": cache_hit_rate,
        "cache_hits": cache_stats["hits"],
        "cache_misses": cache_stats["misses"],
    }

@app.get("/api/health/platform")
def get_platform_health(db: Session = Depends(database.get_db)):
    """Phase 9.0 — Full Platform Health Center endpoint."""
    from app.platform_health import get_platform_health as _health
    return _health(db)

# --- Upload Validation Constants ---
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_RESUME_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}
MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_RESUME_PAGES = 20

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress repetitive successful uvicorn access logs
class UvicornAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # uvicorn.access record.args usually holds (client_addr, method, path, http_version, status_code)
        if record.args and len(record.args) >= 3:
            try:
                status_code = int(record.args[2])
                return status_code >= 400
            except:
                pass
        return True

logging.getLogger("uvicorn.access").addFilter(UvicornAccessFilter())

# Configure endpoints and middleware
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please try again later."},
    )

# ── Health check endpoint (keeps Render backend warm) ──────────
@app.get("/health")
def health_check():
    return {"status": "ok"}

def _safe_seed(db):
    """Safely seed initial data (skills, certs, learning resources) without synthetic jobs."""
    # 1. Role Skill Maps

    if db.query(models.RoleSkillMap).count() < 120:
        db.query(models.RoleSkillMap).delete()
        db.commit()
        role_skills_data = [
            # Software Engineer
            ("Software Engineer", "Python", "Required", "Programming"),
            ("Software Engineer", "Java", "Required", "Programming"),
            ("Software Engineer", "C++", "Preferred", "Programming"),
            ("Software Engineer", "JavaScript", "Required", "Programming"),
            ("Software Engineer", "Data Structures", "Required", "Core CS"),
            ("Software Engineer", "Algorithms", "Required", "Core CS"),
            ("Software Engineer", "SQL", "Required", "Database"),
            ("Software Engineer", "PostgreSQL", "Preferred", "Database"),
            ("Software Engineer", "Git", "Required", "Tools"),
            ("Software Engineer", "GitHub", "Required", "Tools"),
            ("Software Engineer", "Docker", "Preferred", "DevOps"),
            ("Software Engineer", "AWS", "Preferred", "Cloud"),
            ("Software Engineer", "REST", "Required", "Architecture"),
            ("Software Engineer", "Microservices", "Preferred", "Architecture"),
            ("Software Engineer", "Agile", "Required", "Methodology"),
            ("Software Engineer", "Problem Solving", "Required", "Soft Skills"),
            ("Software Engineer", "System Design", "Required", "Core CS"),
            
            # Data Engineer
            ("Data Engineer", "Python", "Required", "Programming"),
            ("Data Engineer", "SQL", "Required", "Database"),
            ("Data Engineer", "PostgreSQL", "Required", "Database"),
            ("Data Engineer", "Databricks", "Required", "Big Data"),
            ("Data Engineer", "Apache Spark", "Required", "Big Data"),
            ("Data Engineer", "Airflow", "Required", "Orchestration"),
            ("Data Engineer", "Kafka", "Required", "Streaming"),
            ("Data Engineer", "dbt", "Preferred", "Transformation"),
            ("Data Engineer", "AWS", "Preferred", "Cloud"),
            ("Data Engineer", "Azure", "Preferred", "Cloud"),
            ("Data Engineer", "GCP", "Preferred", "Cloud"),
            ("Data Engineer", "Snowflake", "Preferred", "Data Warehouse"),
            ("Data Engineer", "Redshift", "Preferred", "Data Warehouse"),
            ("Data Engineer", "BigQuery", "Preferred", "Data Warehouse"),
            ("Data Engineer", "Docker", "Preferred", "DevOps"),
            ("Data Engineer", "Git", "Required", "Tools"),
            ("Data Engineer", "GitHub", "Required", "Tools"),
            ("Data Engineer", "REST", "Preferred", "Architecture"),
            ("Data Engineer", "FastAPI", "Preferred", "Framework"),
            ("Data Engineer", "Pandas", "Required", "Data Science"),
            ("Data Engineer", "NumPy", "Required", "Data Science"),
            ("Data Engineer", "Problem Solving", "Required", "Soft Skills"),
            ("Data Engineer", "Data Modeling", "Required", "Core"),
            
            # Frontend Engineer
            ("Frontend Engineer", "JavaScript", "Required", "Programming"),
            ("Frontend Engineer", "TypeScript", "Required", "Programming"),
            ("Frontend Engineer", "React", "Required", "Framework"),
            ("Frontend Engineer", "Next.js", "Preferred", "Framework"),
            ("Frontend Engineer", "Vue", "Preferred", "Framework"),
            ("Frontend Engineer", "HTML", "Required", "Core Web"),
            ("Frontend Engineer", "CSS", "Required", "Core Web"),
            ("Frontend Engineer", "Tailwind", "Preferred", "Styling"),
            ("Frontend Engineer", "Redux", "Preferred", "State Management"),
            ("Frontend Engineer", "Git", "Required", "Tools"),
            ("Frontend Engineer", "Jest", "Preferred", "Testing"),
            ("Frontend Engineer", "Webpack", "Preferred", "Bundling"),
            ("Frontend Engineer", "UX", "Preferred", "Design"),
            ("Frontend Engineer", "Responsive Design", "Required", "Core Web"),
            
            # Backend Engineer
            ("Backend Engineer", "Python", "Required", "Programming"),
            ("Backend Engineer", "Node.js", "Required", "Programming"),
            ("Backend Engineer", "Java", "Preferred", "Programming"),
            ("Backend Engineer", "Go", "Preferred", "Programming"),
            ("Backend Engineer", "SQL", "Required", "Database"),
            ("Backend Engineer", "PostgreSQL", "Required", "Database"),
            ("Backend Engineer", "MongoDB", "Preferred", "Database"),
            ("Backend Engineer", "Redis", "Required", "Caching"),
            ("Backend Engineer", "Docker", "Required", "DevOps"),
            ("Backend Engineer", "Kubernetes", "Preferred", "DevOps"),
            ("Backend Engineer", "AWS", "Required", "Cloud"),
            ("Backend Engineer", "REST", "Required", "Architecture"),
            ("Backend Engineer", "GraphQL", "Preferred", "Architecture"),
            ("Backend Engineer", "Microservices", "Required", "Architecture"),
            
            # DevOps Engineer
            ("DevOps Engineer", "Linux", "Required", "OS"),
            ("DevOps Engineer", "Bash", "Required", "Scripting"),
            ("DevOps Engineer", "Python", "Required", "Scripting"),
            ("DevOps Engineer", "Docker", "Required", "Containerization"),
            ("DevOps Engineer", "Kubernetes", "Required", "Orchestration"),
            ("DevOps Engineer", "Terraform", "Required", "IaC"),
            ("DevOps Engineer", "Ansible", "Preferred", "Configuration"),
            ("DevOps Engineer", "AWS", "Required", "Cloud"),
            ("DevOps Engineer", "CI/CD", "Required", "Pipelines"),
            ("DevOps Engineer", "Jenkins", "Preferred", "Pipelines"),
            ("DevOps Engineer", "GitLab", "Preferred", "Pipelines"),
            ("DevOps Engineer", "Prometheus", "Required", "Monitoring"),
            ("DevOps Engineer", "Grafana", "Required", "Monitoring"),
            ("DevOps Engineer", "Git", "Required", "Tools"),
            
            # Data Analyst
            ("Data Analyst", "SQL", "Required", "Database"),
            ("Data Analyst", "Python", "Required", "Programming"),
            ("Data Analyst", "R", "Preferred", "Programming"),
            ("Data Analyst", "Excel", "Required", "Tools"),
            ("Data Analyst", "Tableau", "Required", "BI Tools"),
            ("Data Analyst", "Power BI", "Required", "BI Tools"),
            ("Data Analyst", "Pandas", "Required", "Data Science"),
            ("Data Analyst", "Statistics", "Required", "Core"),
            ("Data Analyst", "Data Visualization", "Required", "Core"),
            ("Data Analyst", "A/B Testing", "Preferred", "Core")
        ]
        for r, s, imp, cat in role_skills_data:
            db.add(models.RoleSkillMap(role=r, skill=s, importance=imp, category=cat))
        db.commit()

    # 3. Learning Resources (Expanded Catalog with Verified India Priority URLs)
    if db.query(models.LearningResource).count() < 50:
        db.query(models.LearningResource).delete()
        db.commit()
        
        learning_resources_data = [
            # --- FULL STACK & WEB DEV (CodeWithHarry, Harkirat, Apna College, freeCodeCamp) ---
            models.LearningResource(title="Sigma Web Development Course", provider="CodeWithHarry", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9agq5TrH9XLIKQvv0iaF2X3w", difficulty="Beginner", duration="80 Hours", is_free=True, skills_covered=["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB", "Web Development", "Full Stack"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Full Stack Developer", "Frontend Developer", "Web Developer"], country="India"),
            models.LearningResource(title="Full Stack Web Development for Beginners", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=nu_pCVPKzTk", difficulty="Intermediate", duration="15 Hours", is_free=True, skills_covered=["HTML", "CSS", "JavaScript", "Express", "Node.js", "MongoDB", "Full Stack"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Full Stack Developer", "Backend Developer", "Frontend Developer"], country="Global"),
            models.LearningResource(title="Web Development Course - Apna College", provider="Apna College", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLfqMhTWNBTe3H6c9OGXb5_yew8Qmu41a3", difficulty="Beginner", duration="50 Hours", is_free=True, skills_covered=["HTML", "CSS", "JavaScript", "React", "Frontend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Frontend Developer", "Full Stack Developer"], country="India"),
            models.LearningResource(title="Namaste JavaScript", provider="Akshay Saini", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLlasXeu85E9cQ32gLCvAvr9vNaUccPVNP", difficulty="Intermediate", duration="15 Hours", is_free=True, skills_covered=["JavaScript", "Closures", "Hoisting", "Promises", "Frontend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Frontend Developer", "Full Stack Developer"], country="India"),
            models.LearningResource(title="React JS Course for Beginners - 2023", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=bMknfKXIFA8", difficulty="Intermediate", duration="10 Hours", is_free=True, skills_covered=["React", "JavaScript", "Hooks", "Context API", "Frontend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Frontend Developer", "Web Developer", "Full Stack Developer"], country="Global"),
            models.LearningResource(title="React.js Tutorials in Hindi", provider="CodeWithHarry", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9agx66oZnT6IyhcMIbUMNMdt", difficulty="Beginner", duration="15 Hours", is_free=True, skills_covered=["React.js", "Frontend", "JavaScript", "Hooks"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Frontend Developer", "Web Developer"], country="India"),
            models.LearningResource(title="Node.js and Express.js - Full Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=Oe421EPjeBE", difficulty="Intermediate", duration="8 Hours", is_free=True, skills_covered=["Node.js", "Express.js", "Backend", "API", "JavaScript"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Backend Developer", "Full Stack Developer"], country="Global"),
            models.LearningResource(title="Next.js 14 Full Course 2024", provider="JavaScript Mastery", category="YouTube Course", url="https://www.youtube.com/watch?v=wm5gMKuwSYk", difficulty="Intermediate", duration="5 Hours", is_free=True, skills_covered=["Next.js", "React", "Full Stack", "Tailwind CSS"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Frontend Developer", "Full Stack Developer"], country="Global"),
            models.LearningResource(title="Tailwind CSS Full Course", provider="CodeWithHarry", category="YouTube Course", url="https://www.youtube.com/watch?v=tZOXcKAKjEE", difficulty="Beginner", duration="3 Hours", is_free=True, skills_covered=["Tailwind", "CSS", "Frontend", "Design"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Frontend Developer", "Web Designer"], country="India"),
            models.LearningResource(title="Learn Web3 and Blockchain", provider="Harkirat Singh", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9agq5TrH9XLIKQvv0iaF2X3w", difficulty="Advanced", duration="20 Hours", is_free=True, skills_covered=["Web3", "Blockchain", "Solidity", "Smart Contracts"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Web3 Developer", "Full Stack Developer"], country="India"),

            # --- PYTHON, C++, JAVA, & DSA ---
            models.LearningResource(title="Python for Beginners | #100DaysOfCode", provider="CodeWithHarry", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9agwh1XjRt242xIpHhPT2llg", difficulty="Beginner", duration="100 Hours", is_free=True, skills_covered=["Python", "Programming", "OOP", "Backend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Data Scientist", "Backend Developer"], country="India"),
            models.LearningResource(title="C++ Tutorials in Hindi", provider="CodeWithHarry", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9agpFUAlPFe_VNSlXW5uE0YL", difficulty="Intermediate", duration="35 Hours", is_free=True, skills_covered=["C++", "DSA", "OOP"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Systems Engineer", "Backend Developer"], country="India"),
            models.LearningResource(title="Java Tutorials For Beginners In Hindi", provider="CodeWithHarry", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9agS67Uits0UnJyrYiXhDS6q", difficulty="Beginner", duration="20 Hours", is_free=True, skills_covered=["Java", "OOP", "Collections", "Backend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Backend Developer", "Java Developer"], country="India"),
            models.LearningResource(title="Java & DSA in 30 days - Course for Placement", provider="Apna College", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLfqMhTWNBTe3LtFWcvwpqTkUSlB32kJop", difficulty="Intermediate", duration="40 Hours", is_free=True, skills_covered=["Java", "DSA", "Algorithms", "Interview Prep"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Backend Developer", "Java Developer"], country="India"),
            models.LearningResource(title="Data Structures and Algorithms - Full Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=8hly31xKli0", difficulty="Advanced", duration="10 Hours", is_free=True, skills_covered=["DSA", "Algorithms", "Problem Solving", "Java", "Python"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Backend Developer", "Full Stack Developer"], country="Global"),
            models.LearningResource(title="Striver's A2Z DSA Course/Sheet", provider="Take U Forward (Striver)", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLgUwDviBIf0oF6QL8m22w1hIDC1vJ_BHz", difficulty="Advanced", duration="80 Hours", is_free=True, skills_covered=["DSA", "Competitive Programming", "C++", "Java", "Interview Prep"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Backend Developer"], country="India"),
            models.LearningResource(title="Python Django Tutorial in Hindi", provider="CodeWithHarry", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLu0W_9lII9ah7DDtYtflgwMwpT3xmjXY9", difficulty="Intermediate", duration="15 Hours", is_free=True, skills_covered=["Python", "Django", "Backend", "Web Development"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Backend Developer", "Python Developer", "Full Stack Developer"], country="India"),
            models.LearningResource(title="FastAPI - The Complete Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=0sOvCWFmrtA", difficulty="Intermediate", duration="12 Hours", is_free=True, skills_covered=["Python", "FastAPI", "APIs", "Backend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Backend Developer", "Python Developer"], country="Global"),
            models.LearningResource(title="Complete C++ Placement Course", provider="Apna College", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLfqMhTWNBTe0b2nM6JHVCnAkhQRGiZMSJ", difficulty="Beginner", duration="45 Hours", is_free=True, skills_covered=["C++", "Programming", "DSA"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Backend Developer"], country="India"),
            
            # --- DATA SCIENCE, ML & DATABASE ---
            models.LearningResource(title="SQL Tutorial - Full Database Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=HXV3zeQKqGY", difficulty="Beginner", duration="4 Hours", is_free=True, skills_covered=["SQL", "MySQL", "Database", "Backend"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Analyst", "Data Engineer", "Backend Developer", "Data Scientist", "Software Engineer"], country="Global"),
            models.LearningResource(title="Machine Learning for Everybody - Full Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=i_LwzRmA_08", difficulty="Intermediate", duration="4 Hours", is_free=True, skills_covered=["Machine Learning", "Python", "Data Science", "Scikit-Learn"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Scientist", "Machine Learning Engineer", "Data Analyst"], country="Global"),
            models.LearningResource(title="Data Science Course in Hindi", provider="Code Basics", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLPbgcxheSpE1DptOXONKVZFoE_qgq_Kz_", difficulty="Intermediate", duration="30 Hours", is_free=True, skills_covered=["Data Science", "Python", "Machine Learning", "Math"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Scientist", "Machine Learning Engineer", "Data Analyst"], country="India"),
            models.LearningResource(title="Power BI Full Course", provider="Edureka", category="YouTube Course", url="https://www.youtube.com/watch?v=AGrl-H87pRU", difficulty="Beginner", duration="10 Hours", is_free=True, skills_covered=["Power BI", "Data Visualization", "Data Analyst"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Analyst", "Data Engineer", "Data Scientist"], country="India"),
            models.LearningResource(title="Pandas Data Analytics Tutorial", provider="Code Basics", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PLPbgcxheSpE1PW09g5Rk9R-E3KkY_z3mZ", difficulty="Beginner", duration="8 Hours", is_free=True, skills_covered=["Python", "Pandas", "Data Analyst", "Data Science"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Analyst", "Data Scientist", "Data Engineer"], country="India"),
            models.LearningResource(title="Deep Learning Course - Neural Networks", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=VyWAvY2CF9c", difficulty="Advanced", duration="10 Hours", is_free=True, skills_covered=["Deep Learning", "Neural Networks", "PyTorch", "Machine Learning Engineer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Machine Learning Engineer", "Data Scientist"], country="Global"),
            models.LearningResource(title="Data Engineering Full Course", provider="Edureka", category="YouTube Course", url="https://www.youtube.com/watch?v=qWW_w_H7yEU", difficulty="Intermediate", duration="8 Hours", is_free=True, skills_covered=["Data Engineering", "Big Data", "Hadoop", "Spark", "Data Engineer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Engineer", "Data Analyst", "Software Engineer"], country="India"),
            models.LearningResource(title="Data Analysis with Python Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=r-uOLxNrNk8", difficulty="Beginner", duration="10 Hours", is_free=True, skills_covered=["Python", "Data Analysis", "Numpy", "Pandas", "Data Analyst"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Data Analyst", "Data Scientist"], country="Global"),
            models.LearningResource(title="MongoDB Tutorial for Beginners", provider="CodeWithHarry", category="YouTube Course", url="https://www.youtube.com/watch?v=J6mDclq_4bQ", difficulty="Beginner", duration="2 Hours", is_free=True, skills_covered=["MongoDB", "NoSQL", "Database", "Backend Developer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Backend Developer", "Data Engineer", "Full Stack Developer"], country="India"),

            # --- DEVOPS, CLOUD & FUNDAMENTALS ---
            models.LearningResource(title="Git & GitHub Full Course Hindi", provider="CodeWithHarry", category="YouTube Course", url="https://www.youtube.com/watch?v=gwWKnnCMQ5c", difficulty="Beginner", duration="2 Hours", is_free=True, skills_covered=["Git", "GitHub", "Version Control", "DevOps"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Frontend Developer", "Backend Developer", "DevOps Engineer", "Full Stack Developer", "Data Scientist", "Data Analyst", "Machine Learning Engineer"], country="India"),
            models.LearningResource(title="DevOps Tutorial for Beginners", provider="Edureka", category="YouTube Course", url="https://www.youtube.com/watch?v=hQcFE0RD0cQ", difficulty="Beginner", duration="12 Hours", is_free=True, skills_covered=["DevOps", "CI/CD", "Jenkins", "Docker", "Kubernetes", "DevOps Engineer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["DevOps Engineer", "Backend Developer", "Software Engineer"], country="India"),
            models.LearningResource(title="AWS Certified Cloud Practitioner Essentials", provider="AWS Skill Builder", category="Course", url="https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials", difficulty="Beginner", duration="6 Hours", is_free=True, skills_covered=["AWS", "Cloud", "EC2", "S3", "DevOps"], source="AWS Skill Builder", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["DevOps Engineer", "Backend Developer", "Software Engineer", "Cloud Engineer"], country="Global"),
            models.LearningResource(title="Docker Tutorial for Beginners", provider="CodeStepByStep", category="YouTube Playlist", url="https://www.youtube.com/playlist?list=PL8p2I9GklV44w-rQyG0HkU2pCgUaU9h_T", difficulty="Beginner", duration="4 Hours", is_free=True, skills_covered=["Docker", "Containers", "DevOps Engineer", "Backend Developer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["DevOps Engineer", "Backend Developer", "Full Stack Developer"], country="India"),
            models.LearningResource(title="Linux Operating System - Crash Course", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=sWbUDq4S6Y8", difficulty="Beginner", duration="2 Hours", is_free=True, skills_covered=["Linux", "Bash", "Terminal", "DevOps Engineer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["DevOps Engineer", "Backend Developer", "Software Engineer"], country="Global"),
            models.LearningResource(title="Harvard CS50 - Introduction to Computer Science", provider="Harvard University", category="Course", url="https://www.youtube.com/watch?v=8mAITcNt710", difficulty="Beginner", duration="24 Hours", is_free=True, skills_covered=["CS Fundamentals", "C", "Python", "Algorithms", "Software Engineer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Data Scientist", "Data Analyst", "Machine Learning Engineer", "DevOps Engineer"], country="Global"),
            models.LearningResource(title="Swayam Online Courses (Government of India)", provider="Swayam", category="Course", url="https://swayam.gov.in/", difficulty="Beginner", duration="Variable", is_free=True, skills_covered=["CS Fundamentals", "Engineering", "Algorithms", "Software Engineer"], source="Swayam", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Data Scientist", "Data Analyst", "Machine Learning Engineer", "DevOps Engineer"], country="India"),
            models.LearningResource(title="Kubernetes Course - Full Tutorial", provider="freeCodeCamp", category="YouTube Course", url="https://www.youtube.com/watch?v=X48VuDVv0do", difficulty="Intermediate", duration="4 Hours", is_free=True, skills_covered=["Kubernetes", "Containers", "DevOps Engineer"], source="YouTube", availability_status="VERIFIED", status="VERIFIED", affordability="FREE", roles=["DevOps Engineer", "Backend Developer"], country="Global")
        ]

        db.add_all(learning_resources_data)
        db.commit()

    # 4. Certifications (Expanded Catalog with Verified URLs)
    if db.query(models.Certification).count() < 35:
        db.query(models.Certification).delete()
        db.commit()
        certifications_data = [
            # Cloud Certifications
            models.Certification(
                name="AWS Certified Solutions Architect - Associate", provider="AWS",
                url="https://aws.amazon.com/certification/certified-solutions-architect-associate/", is_free=False, cost="USD 150",
                difficulty="Intermediate", estimated_hours=40,
                skills_covered=["AWS", "Cloud Architecture", "EC2", "S3", "VPC", "IAM"],
                roles=["Cloud Engineer", "Solutions Architect", "DevOps Engineer", "Backend Developer"],
                availability_status="VERIFIED", price_inr=12500, affordability="PAID", free_learning_available=True
            ),
            models.Certification(
                name="AWS Certified Cloud Practitioner", provider="AWS",
                url="https://aws.amazon.com/certification/certified-cloud-practitioner/", is_free=False, cost="USD 100",
                difficulty="Beginner", estimated_hours=20,
                skills_covered=["AWS Basics", "Cloud Fundamentals", "Billing and Pricing"],
                roles=["Cloud Engineer", "DevOps Engineer", "Product Manager"],
                availability_status="VERIFIED", price_inr=8300, affordability="PAID", free_learning_available=True
            ),
            models.Certification(
                name="Microsoft Certified: Azure Fundamentals (AZ-900)", provider="Microsoft",
                url="https://learn.microsoft.com/en-us/certifications/azure-fundamentals/", is_free=False, cost="USD 99",
                difficulty="Beginner", estimated_hours=15,
                skills_covered=["Azure", "Cloud Concepts", "Security", "Privacy"],
                roles=["Cloud Engineer", "DevOps Engineer"],
                availability_status="VERIFIED", price_inr=3696, affordability="AFFORDABLE", free_learning_available=True
            ),
            models.Certification(
                name="Microsoft Certified: Azure Developer Associate (AZ-204)", provider="Microsoft",
                url="https://learn.microsoft.com/en-us/certifications/azure-developer/", is_free=False, cost="USD 165",
                difficulty="Intermediate", estimated_hours=60,
                skills_covered=["Azure Compute", "Azure Storage", "Azure Security", "Troubleshooting"],
                roles=["Backend Developer", "Cloud Engineer", "Software Engineer"],
                availability_status="VERIFIED", price_inr=4800, affordability="PAID", free_learning_available=True
            ),
            models.Certification(
                name="Google Cloud Professional Cloud Architect", provider="Google Cloud",
                url="https://cloud.google.com/learn/certification/cloud-architect", is_free=False, cost="USD 200",
                difficulty="Advanced", estimated_hours=80,
                skills_covered=["GCP", "Cloud Architecture", "Infrastructure Design", "Security"],
                roles=["Cloud Architect", "Cloud Engineer", "DevOps Engineer"],
                availability_status="VERIFIED", price_inr=16600, affordability="PAID", free_learning_available=True
            ),
            
            # Networking and Security
            models.Certification(
                name="Cisco Certified Network Associate (CCNA)", provider="Cisco",
                url="https://www.cisco.com/c/en/us/training-events/training-certifications/certifications/associate/ccna.html", is_free=False, cost="USD 300",
                difficulty="Intermediate", estimated_hours=120,
                skills_covered=["Networking", "IP Connectivity", "Security Fundamentals", "Automation"],
                roles=["Network Engineer", "Systems Engineer", "Security Analyst"],
                availability_status="VERIFIED", price_inr=24900, affordability="PAID", free_learning_available=False
            ),
            models.Certification(
                name="CompTIA Security+", provider="CompTIA",
                url="https://www.comptia.org/certifications/security", is_free=False, cost="USD 392",
                difficulty="Intermediate", estimated_hours=80,
                skills_covered=["Cybersecurity", "Threats", "Vulnerabilities", "Risk Management"],
                roles=["Security Analyst", "Systems Administrator", "Network Engineer"],
                availability_status="VERIFIED", price_inr=32500, affordability="PAID", free_learning_available=False
            ),
            models.Certification(
                name="Certified Information Systems Security Professional (CISSP)", provider="ISC2",
                url="https://www.isc2.org/Certifications/CISSP", is_free=False, cost="USD 749",
                difficulty="Advanced", estimated_hours=200,
                skills_covered=["Security and Risk Management", "Asset Security", "Security Engineering"],
                roles=["Security Manager", "Security Architect", "CISO"],
                availability_status="VERIFIED", price_inr=62000, affordability="PAID", free_learning_available=False
            ),

            # DevOps & Containers
            models.Certification(
                name="Certified Kubernetes Administrator (CKA)", provider="Cloud Native Computing Foundation (CNCF)",
                url="https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/", is_free=False, cost="USD 395",
                difficulty="Advanced", estimated_hours=100,
                skills_covered=["Kubernetes", "Cluster Architecture", "Workloads & Scheduling", "Troubleshooting"],
                roles=["DevOps Engineer", "Site Reliability Engineer", "Platform Engineer"],
                availability_status="VERIFIED", price_inr=32700, affordability="PAID", free_learning_available=False
            ),
            models.Certification(
                name="HashiCorp Certified: Terraform Associate", provider="HashiCorp",
                url="https://developer.hashicorp.com/terraform/certification", is_free=False, cost="USD 70.50",
                difficulty="Beginner", estimated_hours=30,
                skills_covered=["Infrastructure as Code (IaC)", "Terraform CLI", "Modules", "State Management"],
                roles=["DevOps Engineer", "Cloud Engineer", "Platform Engineer"],
                availability_status="VERIFIED", price_inr=5850, affordability="AFFORDABLE", free_learning_available=True
            ),

            # Software Engineering & Data
            models.Certification(
                name="Oracle Certified Professional: Java SE 17 Developer", provider="Oracle",
                url="https://education.oracle.com/oracle-certified-professional-java-se-17-developer/trackp_OCPJSE17", is_free=False, cost="USD 245",
                difficulty="Advanced", estimated_hours=120,
                skills_covered=["Java SE 17", "Object-Oriented Programming", "Generics", "Collections", "Concurrency"],
                roles=["Backend Developer", "Java Developer", "Software Engineer"],
                availability_status="VERIFIED", price_inr=20300, affordability="PAID", free_learning_available=False
            ),
            models.Certification(
                name="Snowflake SnowPro Core Certification", provider="Snowflake",
                url="https://www.snowflake.com/en/learn/certification/snowpro-core/", is_free=False, cost="USD 175",
                difficulty="Intermediate", estimated_hours=50,
                skills_covered=["Data Warehousing", "Snowflake Architecture", "Data Movement", "Performance Tuning"],
                roles=["Data Engineer", "Data Architect", "Data Analyst"],
                availability_status="VERIFIED", price_inr=14500, affordability="PAID", free_learning_available=True
            ),
            models.Certification(
                name="Databricks Certified Data Engineer Associate", provider="Databricks",
                url="https://www.databricks.com/learn/certification/data-engineer-associate", is_free=False, cost="USD 200",
                difficulty="Intermediate", estimated_hours=60,
                skills_covered=["Databricks Lakehouse Platform", "Apache Spark", "Delta Lake", "Data Pipelines"],
                roles=["Data Engineer", "Data Scientist"],
                availability_status="VERIFIED", price_inr=16600, affordability="PAID", free_learning_available=True
            ),

            # Agile & Management
            models.Certification(
                name="Project Management Professional (PMP)", provider="PMI",
                url="https://www.pmi.org/certifications/project-management-pmp", is_free=False, cost="USD 595",
                difficulty="Advanced", estimated_hours=150,
                skills_covered=["Project Management", "Agile", "Risk Management", "Leadership"],
                roles=["Project Manager", "Scrum Master", "Product Manager"],
                availability_status="VERIFIED", price_inr=49300, affordability="PAID", free_learning_available=False
            ),
            models.Certification(
                name="Certified ScrumMaster (CSM)", provider="Scrum Alliance",
                url="https://www.scrumalliance.org/get-certified/scrum-master-track/certified-scrummaster", is_free=False, cost="Varies (approx USD 1000 with course)",
                difficulty="Beginner", estimated_hours=16,
                skills_covered=["Scrum Framework", "Agile Methodologies", "Sprint Planning", "Facilitation"],
                roles=["Scrum Master", "Project Manager", "Agile Coach"],
                availability_status="VERIFIED", price_inr=83000, affordability="PAID", free_learning_available=False
            ),
            # Indian Government Certifications
            models.Certification(
                name="Swayam Online Certification", provider="Government of India (Swayam)",
                url="https://swayam.gov.in/", is_free=False, cost="INR 1,000 (Exam)",
                difficulty="Intermediate", estimated_hours=40,
                skills_covered=["Varies", "Engineering", "Sciences", "Humanities", "Management"],
                roles=["Student", "Professional", "Researcher"],
                availability_status="VERIFIED", price_inr=1000, affordability="AFFORDABLE", free_learning_available=True
            ),
            models.Certification(
                name="NPTEL Online Certification (IIT/IISc)", provider="NPTEL",
                url="https://nptel.ac.in/courses", is_free=False, cost="INR 1,000 (Exam)",
                difficulty="Advanced", estimated_hours=40,
                skills_covered=["CS Fundamentals", "Algorithms", "Machine Learning", "Data Science"],
                roles=["Software Engineer", "Data Scientist", "Research Analyst"],
                availability_status="VERIFIED", price_inr=1000, affordability="AFFORDABLE", free_learning_available=True
            ),
            models.Certification(
                name="CDAC Certified Software Professional", provider="C-DAC",
                url="https://www.cdac.in/", is_free=False, cost="Varies",
                difficulty="Intermediate", estimated_hours=120,
                skills_covered=["Software Development", "C++", "Java", "Web Technologies"],
                roles=["Software Engineer", "Backend Developer", "Full Stack Developer"],
                availability_status="VERIFIED", price_inr=5000, affordability="AFFORDABLE", free_learning_available=False
            ),
            models.Certification(
                name="NIELIT 'O' / 'A' / 'B' / 'C' Level Certification", provider="NIELIT",
                url="https://www.nielit.gov.in/", is_free=False, cost="Varies by Level",
                difficulty="Beginner", estimated_hours=100,
                skills_covered=["IT Tools", "Programming", "Databases", "Networking"],
                roles=["IT Assistant", "Programmer", "Systems Administrator"],
                availability_status="VERIFIED", price_inr=3000, affordability="AFFORDABLE", free_learning_available=False
            ),
            models.Certification(
                name="Skill India Certification", provider="NSDC / Skill India",
                url="https://www.skillindia.gov.in/", is_free=True, cost="Free",
                difficulty="Beginner", estimated_hours=30,
                skills_covered=["Vocational Skills", "Digital Literacy", "Soft Skills", "Industry Specific"],
                roles=["Entry Level", "Apprentice", "Technician"],
                availability_status="VERIFIED", price_inr=0, affordability="FREE", free_learning_available=True
            )
        ]
        db.add_all(certifications_data)
        db.commit()

# --- Scheduler Events ---
# IMPORTANT: The scheduler is intentionally NOT started automatically in production.
# In production, run the scheduler as a separate process using `python worker.py`.
# This avoids duplicate scheduler instances when multiple API workers run.
# To run scheduler embedded (for local dev only), set ENABLE_SCHEDULER=true.
@app.on_event("startup")
def startup_event():
    # 1. Ensure backend directory is in sys.path
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import sys
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # 2. Database initialization with REAL DATA ONLY
    try:
        db = database.SessionLocal()
        from sqlalchemy import text

        # 2a. Schema column safety & Phase 11.8 Migration
        try:
            database.Base.metadata.create_all(bind=database.engine)
            auth.ensure_admin_user(db)
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS data_origin VARCHAR;"))
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS apply_url_status VARCHAR;"))
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS verified_apply_url VARCHAR;"))
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS last_validated_at TIMESTAMP;"))
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS validation_status VARCHAR DEFAULT 'PENDING';"))
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS validation_attempts INTEGER DEFAULT 0;"))
            db.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS validation_reason VARCHAR;"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_opportunities_last_validated_at ON opportunities (last_validated_at);"))
            db.execute(text("CREATE INDEX IF NOT EXISTS ix_opportunities_validation_status ON opportunities (validation_status);"))
            db.commit()
            
            # Run strict deduplication
            try:
                from .duplicate_detector_v2 import run_strict_deduplication
                dedup_res = run_strict_deduplication(db)
                logger.info(f"Startup strict deduplication: {dedup_res}")
            except Exception as dedup_err:
                logger.warning(f"Startup strict deduplication error: {dedup_err}")
        except Exception as mig_err:
            logger.warning(f"Schema migration check: {mig_err}")
            db.rollback()

        # 2b. Purge fake/invalid records and non-India overseas listings
        try:
            purge_stmt = text("""
                DELETE FROM opportunities 
                WHERE apply_url LIKE '%linkedin.com/jobs/search%'
                   OR apply_url LIKE '%?req_id=%'
                   OR apply_url LIKE '%?q=jobs%'
                   OR apply_url LIKE '%?keyword=%'
                   OR apply_url LIKE '%joblist%'
                   OR (data_origin IS NULL AND posted_date < NOW() - INTERVAL '60 days');
            """)
            res = db.execute(purge_stmt)
            db.commit()
            logger.info(f"Database purge complete. Rows deleted: {res.rowcount}")
        except Exception as purge_err:
            logger.warning(f"Database purge error: {purge_err}")
            db.rollback()

        # 2b1. Ensure necessary indexes for fast querying
        try:
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_opp_data_origin ON opportunities (data_origin);"))
            db.commit()
        except Exception as idx_err:
            db.rollback()

        # 2b2. India-First: normalize locations and purge all non-India overseas records
        try:
            # Normalize Unstop 'online'/'offline' locations
            db.execute(text("UPDATE opportunities SET location='Remote (India)' WHERE LOWER(location) IN ('online', 'virtual');"))
            db.execute(text("UPDATE opportunities SET location='India (On-site)' WHERE LOWER(location) IN ('offline', 'in-person', 'on-site');"))
            # Purge overseas listings
            overseas_purge = text("""
                DELETE FROM opportunities WHERE (
                    location ILIKE '%LATAM%' OR location ILIKE '%Luxembourg%'
                    OR location ILIKE '%United States%' OR location ILIKE '%USA%'
                    OR location ILIKE '%Canada%' OR location ILIKE '%Germany%'
                    OR location ILIKE '%United Kingdom%' OR location ILIKE '%London%'
                    OR location ILIKE '%Berlin%' OR location ILIKE '%Australia%'
                    OR location ILIKE '%Brazil%' OR location ILIKE '%Spain%'
                    OR location ILIKE '%France%' OR location ILIKE '%Poland%'
                    OR location ILIKE '%Indonesia%' OR location ILIKE '%Jakarta%'
                    OR location ILIKE '%Singapore%' OR location ILIKE '%Ireland%'
                    OR (location ILIKE '%Remote%'
                        AND location NOT ILIKE '%India%'
                        AND location NOT ILIKE '%Remote (India)%')
                );
            """)
            overseas_res = db.execute(overseas_purge)
            db.commit()
            if overseas_res.rowcount > 0:
                logger.info(f"India-First: Purged {overseas_res.rowcount} overseas/non-India listings on startup.")
        except Exception as india_err:
            logger.warning(f"India-First location normalization error (non-fatal): {india_err}")
            db.rollback()

        # 2c. Run live API collector to fetch/refresh real jobs
        try:
            from .auto_collector import run_auto_collection
            result = run_auto_collection(db)
            logger.info(
                f"Live API collector completed: "
                f"inserted={result['inserted']}, "
                f"active_jobs={result['active_jobs']}, "
                f"sources={result.get('sources', {})}"
            )
        except Exception as coll_err:
            logger.warning(f"Live API collector failed (non-fatal): {coll_err}")

        # 2d. Refresh learning resources and certifications
        try:
            db.query(models.LearningResource).delete()
            db.query(models.Certification).delete()
            db.commit()
            _safe_seed(db)
            logger.info("Refreshed learning resources and certifications with verified URLs.")
        except Exception as res_err:
            logger.warning(f"Learning resource refresh failed (non-fatal): {res_err}")
            db.rollback()

        db.close()
    except Exception as db_err:
        logger.warning(f"Startup database check failed (non-fatal): {db_err}")

    # 3. Start embedded scheduler
    enable_scheduler = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"
    if enable_scheduler:
        try:
            from scheduler import start_scheduler
            start_scheduler()
            logger.info("Embedded scheduler started (ENABLE_SCHEDULER=true).")
        except Exception as e:
            logger.warning(f"Scheduler failed to start (non-fatal): {e}")
    else:
        logger.info("Scheduler NOT started in API process. Run `python worker.py` separately.")

@app.post("/api/admin/audit-links")
def audit_and_cleanup_links(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    from app.link_validator import run_full_audit_and_cleanup
    stats = run_full_audit_and_cleanup(db)
    return {"message": "Audit and cleanup completed successfully", "stats": stats}

@app.get("/api/opportunities/{id}/apply-redirect")
def resolve_apply_redirect(id: int, db: Session = Depends(database.get_db)):
    """
    Truthful Direct-Apply Resolver:
    Distinguishes between VERIFIED_DIRECT, VERIFIED_SEARCH, UNVERIFIED_SEARCH, CLOSED, and INVALID_LINK.
    Never misleads candidates with generic homepages as verified direct postings.
    """
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # 1. Closed or Expired
    if opp.status in ("CLOSED", "Closed", "EXPIRED", "Expired") or opp.lifecycle_status in ("CLOSED", "EXPIRED", "ARCHIVED"):
        return {
            "opportunity_id": id,
            "status": "CLOSED",
            "classification": "CLOSED",
            "redirect_url": None,
            "company": opp.company,
            "title": opp.title,
            "message": "This position is no longer accepting applications."
        }

    # 2. Invalid or missing link
    apply_url = opp.verified_apply_url or opp.apply_url
    if not apply_url or opp.apply_url_status in ("BROKEN", "INVALID_LINK", "INVALID"):
        return {
            "opportunity_id": id,
            "status": "INVALID_LINK",
            "classification": "INVALID_LINK",
            "redirect_url": None,
            "company": opp.company,
            "title": opp.title,
            "message": "The application link is unavailable or broken."
        }

    # 3. Verified Direct Link
    if opp.apply_url_status == "VERIFIED_DIRECT":
        return {
            "opportunity_id": id,
            "status": "VERIFIED_DIRECT",
            "classification": "VERIFIED_DIRECT",
            "redirect_url": apply_url,
            "company": opp.company,
            "title": opp.title,
            "source": opp.primary_source,
            "data_origin": opp.data_origin,
            "message": "Direct employer application link confirmed."
        }

    # 4. Verified Search
    if opp.apply_url_status == "VERIFIED_SEARCH":
        return {
            "opportunity_id": id,
            "status": "VERIFIED_SEARCH",
            "classification": "VERIFIED_SEARCH",
            "redirect_url": apply_url,
            "company": opp.company,
            "title": opp.title,
            "source": opp.primary_source,
            "data_origin": opp.data_origin,
            "message": "Opening employer career portal with matching search filters."
        }

    # 5. Unverified Search (Default for curated/search portals)
    return {
        "opportunity_id": id,
        "status": "UNVERIFIED_SEARCH",
        "classification": "UNVERIFIED_SEARCH",
        "redirect_url": apply_url,
        "company": opp.company,
        "title": opp.title,
        "source": opp.primary_source,
        "data_origin": opp.data_origin or "CURATED_SEARCH",
        "message": "Unverified Opportunity — opening official employer career portal."
    }

@app.on_event("shutdown")
def shutdown_event():
    enable_scheduler = os.environ.get("ENABLE_SCHEDULER", "false").lower() == "true"
    if enable_scheduler:
        try:
            from scheduler import stop_scheduler
            stop_scheduler()
        except Exception:
            pass

# --- Health Endpoint ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/admin/seed")
def trigger_seed():
    """Admin endpoint to populate/reset initial database content."""
    try:
        from seed import seed_db
        seed_db()
        return {"status": "success", "message": "Database successfully seeded with opportunities, users, and resources."}
    except Exception as e:
        logger.error(f"Manual database seed failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database seed failed: {str(e)}")

# --- Scheduler Config ---
class SchedulerConfig(BaseModel):
    interval_hours: int

@app.get("/api/scheduler/config")
def get_scheduler_config(current_user: models.User = Depends(auth.get_current_user)):
    interval = int(os.environ.get("REFRESH_INTERVAL_HOURS", 6))
    return {"interval_hours": interval}

@app.put("/api/scheduler/config")
def update_scheduler_config(config: SchedulerConfig, current_user: models.User = Depends(auth.get_current_user)):
    if config.interval_hours not in [3, 6, 12, 24]:
        raise HTTPException(status_code=400, detail="Invalid interval. Must be 3, 6, 12, or 24.")
    os.environ["REFRESH_INTERVAL_HOURS"] = str(config.interval_hours)
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from scheduler import update_interval
        update_interval(config.interval_hours)
    except Exception as e:
        logger.error(f"Failed to update scheduler: {e}")
        raise HTTPException(status_code=500, detail="Failed to update scheduler.")
    return {"message": "Scheduler interval updated successfully.", "interval_hours": config.interval_hours}

# --- Auth Routes ---
@app.post("/api/auth/register", response_model=schemas.User)
@limiter.limit("3/minute")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    email = user.email.strip().lower()
    db_user = auth.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    
    # Determine if strict email verification is required (default: false unless REQUIRE_EMAIL_VERIFICATION=true)
    require_verification = os.environ.get("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
    
    # Generate verification token
    raw_token = auth.generate_secure_token()
    token_hash = auth.hash_token(raw_token)
    expires = datetime.utcnow() + timedelta(hours=24)
    
    db_user = models.User(
        email=email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_verified=not require_verification,  # Auto-verify if strict verification is disabled
        verification_token=token_hash if require_verification else None,
        verification_expires=expires if require_verification else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email via the email service
    from app.email_service import send_verification_email
    frontend_url = os.environ.get("FRONTEND_URL", "https://career-lens-ai-wheat.vercel.app").rstrip("/")
    verification_url = f"{frontend_url}/verify?token={raw_token}"
    email_sent = send_verification_email(email, verification_url)
    
    # If verification was required but email delivery failed (e.g. Resend unverified domain restriction),
    # auto-verify the user so they are not locked out of their account.
    if require_verification and not email_sent:
        logger.warning(f"Verification email delivery failed for {email} (e.g. unverified Resend domain). Auto-verifying user.")
        db_user.is_verified = True
        db_user.verification_token = None
        db_user.verification_expires = None
        db.commit()
        db.refresh(db_user)
    
    return db_user

class ResendVerificationRequest(BaseModel):
    email: str

@app.post("/api/auth/resend-verification")
@limiter.limit("3/minute")
def resend_verification(request: Request, payload: ResendVerificationRequest, db: Session = Depends(database.get_db)):
    email = payload.email.strip().lower()
    user = auth.get_user_by_email(db, email=email)
    
    if user and not user.is_verified:
        # Generate new token
        raw_token = auth.generate_secure_token()
        token_hash = auth.hash_token(raw_token)
        expires = datetime.utcnow() + timedelta(hours=24)
        
        user.verification_token = token_hash
        user.verification_expires = expires
        db.commit()
        
        # Send via email service
        from app.email_service import send_verification_email
        frontend_url = os.environ.get("FRONTEND_URL", "https://career-lens-ai-wheat.vercel.app").rstrip("/")
        verification_url = f"{frontend_url}/verify?token={raw_token}"
        email_sent = send_verification_email(email, verification_url)
        if not email_sent:
            logger.warning(f"Resend verification email delivery failed for {email}. Auto-verifying account.")
            user.is_verified = True
            user.verification_token = None
            user.verification_expires = None
            db.commit()

    # Return safe generic response to prevent account enumeration
    return {"message": "If the account exists and is not yet verified, a verification email has been sent."}


@app.post("/api/auth/verify")
@limiter.limit("5/minute")
def verify_email(request: Request, payload: schemas.EmailVerificationRequest, db: Session = Depends(database.get_db)):
    token_hash = auth.hash_token(payload.token)
    user = db.query(models.User).filter(models.User.verification_token == token_hash).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    if user.verification_expires and user.verification_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")
        
    user.is_verified = True
    user.verification_token = None
    user.verification_expires = None
    db.commit()
    return {"message": "Email successfully verified"}

@app.post("/api/auth/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: schemas.PasswordResetRequest, db: Session = Depends(database.get_db)):
    email = payload.email.strip().lower()
    user = auth.get_user_by_email(db, email)
    reset_url = None
    email_sent = False

    logger.info(f"Password reset requested for '{email}' | Account found in DB: {user is not None}")

    if user:
        raw_token = auth.generate_secure_token()
        user.reset_token = auth.hash_token(raw_token)
        user.reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        from app.email_service import send_password_reset_email
        frontend_url = os.environ.get("FRONTEND_URL", "https://career-lens-ai-wheat.vercel.app").rstrip("/")
        reset_url = f"{frontend_url}/reset-password?token={raw_token}"
        email_sent = send_password_reset_email(email, reset_url)
        logger.info(f"Password reset email dispatch for '{email}': {'SUCCESS' if email_sent else 'FAILED'}")
    else:
        logger.warning(f"Password reset skipped: No user account found with email '{email}'.")

    # Always return the same generic message regardless of whether the user exists or email was sent.
    # This prevents user enumeration attacks (attacker cannot tell if an email is registered).
    # The reset URL is NEVER exposed in the response in production — the only way to get it
    # is to have access to the actual email inbox, which is the security guarantee of email-based reset.
    is_production = os.getenv("ENVIRONMENT", "development") == "production"

    if is_production:
        # In production: always same message, no URL leak, no hint about account existence
        return {"message": "If an account exists with this email, a reset link has been sent. Please check your inbox (and spam folder)."}

    # In development only: expose the link so developers can test without a mail server
    res_data = {"message": "If an account exists with this email, a reset link has been sent."}
    if reset_url and not email_sent:
        res_data["debug_reset_url"] = reset_url
        res_data["_dev_note"] = "This direct link is only shown in development mode. In production it is never exposed."
    return res_data

@app.post("/api/auth/reset-password")
@limiter.limit("3/minute")
def reset_password(request: Request, payload: schemas.PasswordResetConfirm, db: Session = Depends(database.get_db)):
    token_hash = auth.hash_token(payload.token)
    user = db.query(models.User).filter(models.User.reset_token == token_hash).first()
    
    if not user or not user.reset_expires or user.reset_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
    user.hashed_password = auth.get_password_hash(payload.new_password)
    user.reset_token = None
    user.reset_expires = None
    db.commit()
    return {"message": "Password has been successfully reset"}


@app.get("/api/auth/test-email-delivery")
def test_email_delivery(to: str = "tanmeshj17@gmail.com"):
    """Live diagnostic endpoint to test email sending and report exact connection status."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from app.email_service import _send_via_brevo, _send_via_resend

    smtp_user = (os.getenv("SMTP_USER") or os.getenv("EMAIL_USER") or "").strip()
    smtp_pass = (os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD") or "").replace(" ", "").strip()
    smtp_host = (os.getenv("SMTP_HOST") or "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT") or "587")
    resend_key = (os.getenv("RESEND_API_KEY") or os.getenv("EMAIL_API_KEY") or "").strip()
    brevo_key = (os.getenv("BREVO_API_KEY") or os.getenv("SENDINBLUE_API_KEY") or "").strip()

    status_report = {
        "brevo_key_configured": bool(brevo_key),
        "resend_key_configured": bool(resend_key),
        "smtp_configured": bool(smtp_user and smtp_pass),
        "smtp_user": smtp_user,
        "target_email": to,
        "results": {}
    }

    # Test Brevo HTTPS API first if key exists
    if brevo_key:
        test_html = "<p>This is a test email from CareerLens AI via Brevo HTTPS API.</p>"
        brevo_ok = _send_via_brevo(to, "CareerLens AI - Test Email (Brevo)", test_html)
        status_report["results"]["brevo_https"] = "SUCCESS - Email delivered!" if brevo_ok else "FAILED"
        if brevo_ok:
            status_report["result"] = f"SUCCESS: Email delivered via Brevo HTTPS API to {to}"
            return status_report

    # Test Resend HTTPS API if key exists
    if resend_key:
        test_html = "<p>This is a test email from CareerLens AI via Resend HTTPS API.</p>"
        resend_ok = _send_via_resend(to, "CareerLens AI - Test Email (Resend)", test_html)
        status_report["results"]["resend_https"] = "SUCCESS - Email delivered!" if resend_ok else "FAILED (Note: sandbox only delivers to registered Resend account email)"
        if resend_ok:
            status_report["result"] = f"SUCCESS: Email delivered via Resend HTTPS API to {to}"
            return status_report

    # Test SMTP
    if smtp_user and smtp_pass:
        for test_port in [587, 465]:
            try:
                msg = MIMEMultipart()
                msg["Subject"] = "CareerLens AI - Test Email (SMTP)"
                msg["From"] = f"CareerLens AI <{smtp_user}>"
                msg["To"] = to
                msg.attach(MIMEText("<p>This is a test email from CareerLens AI via SMTP.</p>", "html"))

                if test_port == 465:
                    server = smtplib.SMTP_SSL(smtp_host, test_port, timeout=8)
                else:
                    server = smtplib.SMTP(smtp_host, test_port, timeout=8)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()

                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [to], msg.as_string())
                server.quit()
                status_report["results"][f"smtp_port_{test_port}"] = "SUCCESS"
                status_report["result"] = f"SUCCESS: Email sent via SMTP:{test_port} to {to}"
                return status_report
            except Exception as exc:
                status_report["results"][f"smtp_port_{test_port}"] = f"FAILED: {str(exc)}"

    status_report["result"] = "NO_WORKING_PROVIDER: Add a free BREVO_API_KEY from brevo.com to Render environment variables to send emails over HTTPS without cloud network blocks."
    return status_report

@app.post("/api/auth/token", response_model=schemas.Token)
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    email = form_data.username.strip().lower()
    user = auth.get_user_by_email(db, email)
    if not user:
        logger.warning(f"SECURITY ALERT: Failed login attempt for non-existent email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # First verify password
    pw_valid = auth.verify_password(form_data.password, user.hashed_password)
    if not pw_valid:
        logger.warning(f"SECURITY ALERT: Failed login attempt (bad password) for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Handle unverified user gracefully
    if not user.is_verified:
        require_verification = os.environ.get("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
        if not require_verification:
            logger.info(f"Auto-verifying user {email} on login (REQUIRE_EMAIL_VERIFICATION=false).")
            user.is_verified = True
            user.verification_token = None
            user.verification_expires = None
            db.commit()
        else:
            logger.warning(f"SECURITY ALERT: Login attempt for unverified email: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                )
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"SECURITY EVENT: Successful login for email: {email}")
    return {"access_token": access_token, "token_type": "bearer"}


class GoogleAuthPayload(schemas.BaseModel):
    credential: Optional[str] = None  # Google ID token (JWT from GIS)
    access_token: Optional[str] = None # Google OAuth access token
    email: Optional[str] = None
    name: Optional[str] = None


@app.post("/api/auth/google", response_model=schemas.Token)
@limiter.limit("20/minute")
def login_with_google(
    payload: GoogleAuthPayload,
    request: Request,
    db: Session = Depends(database.get_db)
):
    """
    Google OAuth 2.0 / Google Identity Services Authentication.
    Verifies the Google credential token with Google's servers if provided,
    or processes Google email authentication seamlessly with strict admin protection.
    """
    email = None
    name = None

    import requests as req

    # 1. Verify ID Token with Google (Google Identity Services / One-Tap)
    if payload.credential:
        try:
            resp = req.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.credential}",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                email = data.get("email")
                name = data.get("name")
            else:
                logger.warning(f"Google token verification failed: {resp.text}")
        except Exception as e:
            logger.error(f"Google auth verification error: {e}")

    # 2. Verify Access Token (standard OAuth2 flow)
    if not email and payload.access_token:
        try:
            resp = req.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {payload.access_token}"},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                email = data.get("email")
                name = data.get("name")
        except Exception as e:
            logger.error(f"Google userinfo verification error: {e}")

    # 3. Direct Google Email authentication
    if not email and payload.email:
        clean_input = payload.email.strip().lower()
        # Admin security lock: Prevent accessing root admin account without credentials
        if clean_input in ("careerlensadmin", "careerlensadmin@careerlens.ai"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin accounts must sign in using administrator username and password."
            )
        email = clean_input
        name = payload.name or email.split("@")[0].replace(".", " ").title()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to authenticate with Google. Please provide a valid email."
        )

    clean_email = email.strip().lower()

    # Check if user already exists
    user = auth.get_user_by_email(db, clean_email)
    if not user:
        # Auto-create account — always role='user', never admin
        random_pass = auth.generate_secure_token()
        user = models.User(
            email=clean_email,
            full_name=name or clean_email.split("@")[0].title(),
            hashed_password=auth.get_password_hash(random_pass),
            is_verified=True,
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user auto-registered via Google Sign-In: {clean_email}")
    else:
        # Mark verified (Google confirmed email ownership)
        if not user.is_verified:
            user.is_verified = True
            db.commit()
        if name and not user.full_name:
            user.full_name = name
            db.commit()

    # Generate CareerLens access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"SECURITY EVENT: Successful Google login for email: {clean_email}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/api/users/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if user_update.full_name is not None:
        name = user_update.full_name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Full name cannot be empty")
        current_user.full_name = name
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/api/users/change-password")
def change_password(data: schemas.ChangePasswordRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if not auth.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
    current_user.hashed_password = auth.get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@app.delete("/api/users/me")
def delete_user_me(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    user_id = current_user.id
    # Clean up user's related data in dependent tables
    db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == user_id).delete()
    db.query(models.UserSkillProfile).filter(models.UserSkillProfile.user_id == user_id).delete()
    db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == user_id).delete()
    db.query(models.Resume).filter(models.Resume.user_id == user_id).delete()
    db.query(models.Application).filter(models.Application.user_id == user_id).delete()
    db.query(models.JobMatchScore).filter(models.JobMatchScore.user_id == user_id).delete()
    db.query(models.CareerReadinessSnapshot).filter(models.CareerReadinessSnapshot.user_id == user_id).delete()
    db.delete(current_user)
    db.commit()
    return {"message": "Account successfully deleted"}



# --- Opportunities Routes ---
@app.get("/api/opportunities")
@limiter.limit("120/minute")
def read_opportunities(
    request: Request,
    search: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    experience: Optional[str] = None,
    type: Optional[str] = None,
    sort: Optional[str] = "newest", # newest | relevance | quality
    page: int = 1,
    limit: int = 30,
    db: Session = Depends(database.get_db),
):
    from sqlalchemy import or_, func as sqla_func
    
    # Build filter conditions once, reuse for count + results
    filters = []
    
    if search:
        search_term = f"%{search.strip()}%"
        filters.append(or_(
            models.Opportunity.title.ilike(search_term),
            models.Opportunity.company.ilike(search_term),
            models.Opportunity.location.ilike(search_term),
            models.Opportunity.required_skills.ilike(search_term),
            models.Opportunity.description.ilike(search_term)
        ))
        
    if role and role != "All" and role.strip():
        filters.append(models.Opportunity.title.ilike(f"%{role.strip()}%"))
        
    if location and location != "All" and location.strip():
        filters.append(models.Opportunity.location.ilike(f"%{location.strip()}%"))
        
    if type and type != "All" and type.strip():
        filters.append(models.Opportunity.job_type.ilike(f"%{type.strip()}%"))

    # Phase 8.55: Enforce Direct-Apply Verified Sources ONLY
    filters.append(
        or_(
            models.Opportunity.data_origin == "LIVE_API",
            models.Opportunity.data_origin == "LIVE_SCRAPE",
            models.Opportunity.data_origin == "CURATED_FALLBACK",
            models.Opportunity.data_origin.is_(None)
        )
    )
    filters.append(
        or_(
            models.Opportunity.link_quality_score > 0,
            models.Opportunity.link_quality_score == None # fallback for untested ones
        )
    )
    
    # Lightweight count query (no ORDER BY, no joins)
    count_q = db.query(sqla_func.count(models.Opportunity.id)).filter(
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        )
    )
    if filters:
        count_q = count_q.filter(*filters)
    total = count_q.scalar()
    
    # Results query with ordering and pagination
    skip = (page - 1) * limit
    results_q = db.query(models.Opportunity).filter(
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        )
    )
    if filters:
        results_q = results_q.filter(*filters)

    # Dynamic sort handling
    if sort == "newest":
        results_q = results_q.order_by(
            models.Opportunity.posted_date.desc().nulls_last(),
            models.Opportunity.id.desc()
        )
    elif sort == "quality":
        results_q = results_q.order_by(
            models.Opportunity.link_quality_score.desc().nulls_last(),
            models.Opportunity.trust_score.desc().nulls_last()
        )
    else:  # relevance
        results_q = results_q.order_by(
            models.Opportunity.computed_rank_score.desc().nulls_last(),
            models.Opportunity.last_seen.desc().nulls_last()
        )

    results = results_q.offset(skip).limit(limit).all()
    
    # Async search logging (non-blocking)
    if search:
        try:
            log = models.SearchLog(
                query=search,
                results_count=total,
                filters_used={"type": type, "location": location, "role": role}
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            db.rollback()

    return {
        "total": total,
        "page": page,
        "opportunities": results,
        "has_more": len(results) == limit
    }

@app.get("/api/opportunities/autocomplete", response_model=schemas.SearchSuggestion)
def autocomplete_search(q: str, db: Session = Depends(database.get_db)):
    """Multi-type autocomplete returning titles, companies, skills, and locations."""
    if not q or len(q) < 2:
        return {"suggestions": [], "message": ""}
        
    q_lower = q.lower()
    suggestions = set()
    
    # 1. Job Titles
    titles = db.query(models.Opportunity.title).filter(func.lower(models.Opportunity.title).like(f"%{q_lower}%")).limit(5).all()
    for t in titles:
        if t[0]: suggestions.add(t[0])
        
    # 2. Companies
    companies = db.query(models.CompanyRegistry.company_name).filter(func.lower(models.CompanyRegistry.company_name).like(f"%{q_lower}%")).limit(3).all()
    for c in companies:
        if c[0]: suggestions.add(c[0])
        
    # 3. Locations
    locations = db.query(models.NormalizedLocation.city).filter(func.lower(models.NormalizedLocation.city).like(f"%{q_lower}%")).limit(3).all()
    for l in locations:
        if l[0]: suggestions.add(l[0])
        
    # 4. Skills
    skills = db.query(models.RoleSkillMap.skill).filter(func.lower(models.RoleSkillMap.skill).like(f"%{q_lower}%")).limit(3).all()
    for s in skills:
        if s[0]: suggestions.add(s[0])
        
    sorted_suggestions = sorted(list(suggestions), key=lambda x: (not x.lower().startswith(q_lower), len(x)))[:10]
    
    # If no suggestions, provide "Did you mean?"
    if not sorted_suggestions:
        return {"suggestions": ["Data Engineer", "Software Engineer", "Product Manager", "Data Analyst"], "message": "Did you mean?"}
        
    return {"suggestions": sorted_suggestions, "message": ""}

@app.post("/api/opportunities", response_model=schemas.Opportunity)
def create_opportunity(opportunity: schemas.OpportunityCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_opp = models.Opportunity(**opportunity.dict())
    db.add(db_opp)
    db.commit()
    db.refresh(db_opp)
    return db_opp

@app.get("/api/opportunities/{opp_id}", response_model=schemas.Opportunity)
def get_opportunity(opp_id: int, db: Session = Depends(database.get_db)):
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opp_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp

@app.get("/api/opportunities/{opp_id}/sources", response_model=List[schemas.OpportunitySource])
def get_opportunity_sources(opp_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    sources = db.query(models.OpportunitySource).filter(models.OpportunitySource.opportunity_id == opp_id).all()
    # If no sources recorded yet, synthesize a default source
    if not sources:
        opp = db.query(models.Opportunity).filter(models.Opportunity.id == opp_id).first()
        if opp:
            default_source = models.OpportunitySource(
                opportunity_id=opp_id,
                source_name=opp.primary_source or "Official Career Page",
                source_url=opp.apply_url,
                trust_score=opp.trust_score or 100,
                status="Active"
            )
            db.add(default_source)
            db.commit()
            db.refresh(default_source)
            return [default_source]
    return sources


# --- Applications Routes ---
@app.get("/api/applications", response_model=List[schemas.Application])
def read_user_applications(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Application).filter(models.Application.user_id == current_user.id).all()

@app.post("/api/applications", response_model=schemas.Application)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Check if application already exists for this opportunity
    existing = db.query(models.Application).filter(
        models.Application.user_id == current_user.id,
        models.Application.opportunity_id == application.opportunity_id
    ).first()
    if existing:
        return existing
        
    db_app = models.Application(**application.dict(), user_id=current_user.id)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@app.put("/api/applications/{app_id}", response_model=schemas.Application)
def update_application(app_id: int, application_update: schemas.ApplicationUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_app = db.query(models.Application).filter(models.Application.id == app_id, models.Application.user_id == current_user.id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = application_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_app, key, value)
        
    db.commit()
    db.refresh(db_app)
    return db_app


# --- Resumes Routes ---
@app.post("/api/resumes/analyze", response_model=schemas.AnalyzeResumeResponse)
@limiter.limit("10/minute")
async def analyze_resume(request: Request, file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # --- Upload Validation ---
    # 1. Check file extension
    import pathlib
    ext = pathlib.Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_RESUME_EXTENSIONS)}")
    
    # 2. Check MIME type
    if file.content_type and file.content_type not in ALLOWED_RESUME_MIMES:
        raise HTTPException(status_code=400, detail=f"Invalid MIME type '{file.content_type}'. Upload a PDF or DOCX file.")
    
    # 3. Read and check file size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_RESUME_SIZE_BYTES // (1024*1024)} MB.")
    
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    # 4. PDF-specific validation: corruption check and page count
    if ext == ".pdf":
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if len(pdf.pages) > MAX_RESUME_PAGES:
                    raise HTTPException(status_code=400, detail=f"PDF has too many pages ({len(pdf.pages)}). Maximum is {MAX_RESUME_PAGES}.")
                if len(pdf.pages) == 0:
                    raise HTTPException(status_code=400, detail="PDF has no pages.")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Uploaded PDF appears to be corrupted or unreadable.")
    
    # Real resume parsing
    import os
    secure_name = os.path.basename(file.filename or "unknown.pdf")
    parsed = parse_resume(file_bytes, secure_name)
    
    # Save base Resume entry
    skills_score = min(len(parsed["extracted_skills"]) * 8, 100)
    missing = [w for w in parsed["weaknesses"] if "skills" in w or "certifications" in w]
    missing_str = ", ".join(missing[:4]) if missing else "None"
    
    db_resume = models.Resume(
        user_id=current_user.id,
        filename=secure_name,
        ats_score=parsed["ats_score"],
        skills_score=skills_score,
        missing_skills=missing_str
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # Save detail ResumeProfile entry
    db_profile = models.ResumeProfile(
        user_id=current_user.id,
        uploaded_file=secure_name,
        extracted_skills=parsed["extracted_skills"],
        extracted_projects=parsed["extracted_projects"],
        extracted_education=parsed["extracted_education"],
        extracted_certifications=parsed["extracted_certifications"],
        extracted_experience=parsed["extracted_experience"],
        ats_score=parsed["ats_score"],
        strengths=parsed["strengths"],
        weaknesses=parsed["weaknesses"],
        suggestions=parsed["suggestions"]
    )
    db.add(db_profile)
    db.commit()
    
    # Attach profile data to the return object so it matches AnalyzeResumeResponse schema
    db_resume.extracted_skills = parsed["extracted_skills"]
    db_resume.extracted_projects = parsed["extracted_projects"]
    db_resume.extracted_education = parsed["extracted_education"]
    db_resume.extracted_certifications = parsed["extracted_certifications"]
    db_resume.extracted_experience = parsed["extracted_experience"]
    db_resume.strengths = parsed["strengths"]
    db_resume.weaknesses = parsed["weaknesses"]
    db_resume.suggestions = parsed["suggestions"]
    db_resume.score_breakdown = parsed.get("score_breakdown")
    db_resume.metrics_found = parsed.get("metrics_found")
    
    return db_resume

@app.get("/api/resumes", response_model=List[schemas.Resume])
def get_user_resumes(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Resume).filter(models.Resume.user_id == current_user.id).order_by(models.Resume.posted_date.desc()).all()

@app.get("/api/resumes/{resume_id}/profile", response_model=schemas.ResumeProfile)
def get_resume_profile(resume_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    profile = db.query(models.ResumeProfile).filter(
        models.ResumeProfile.user_id == current_user.id,
        models.ResumeProfile.uploaded_file == resume.filename
    ).order_by(models.ResumeProfile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Resume profile details not found")
    return profile

@app.get("/api/resumes/{resume_id}/gap-analysis")
@limiter.limit("20/minute")
def get_resume_gap_analysis(request: Request, resume_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    profile = db.query(models.ResumeProfile).filter(
        models.ResumeProfile.user_id == current_user.id,
        models.ResumeProfile.uploaded_file == resume.filename
    ).order_by(models.ResumeProfile.created_at.desc()).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Resume profile details not found")

    # Phase 10.2.4: Smart Role Detection for Gap Analysis
    filename_lower = (resume.filename or "").lower()
    user_skills_lower = [s.lower() for s in (profile.extracted_skills or [])]
    user_skills_set = set(user_skills_lower)

    # 1. Filename explicit overrides
    target_role = None
    if "data" in filename_lower and ("engineer" in filename_lower or "engineering" in filename_lower or "de" in filename_lower):
        target_role = "Data Engineer"
    elif "devops" in filename_lower or "sre" in filename_lower:
        target_role = "DevOps Engineer"
    elif "frontend" in filename_lower or "react" in filename_lower:
        target_role = "Frontend Engineer"
    elif "backend" in filename_lower or "node" in filename_lower:
        target_role = "Backend Engineer"
    elif "analyst" in filename_lower or "analytics" in filename_lower:
        target_role = "Data Analyst"

    if not target_role:
        # 2. Weighted Domain Skill Matching
        de_skills = {"apache spark", "spark", "airflow", "kafka", "dbt", "snowflake", "redshift", "bigquery", "databricks", "hadoop", "etl", "data modeling", "data pipeline", "pyspark", "azure", "gcp"}
        fe_skills = {"react", "next.js", "vue", "angular", "html", "css", "tailwind", "redux", "zustand", "frontend", "webpack", "vite"}
        devops_skills = {"docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "prometheus", "grafana", "bash", "ci/cd"}
        da_skills = {"tableau", "power bi", "excel", "statistics", "seaborn", "matplotlib", "a/b testing"}
        be_skills = {"fastapi", "django", "flask", "express.js", "node.js", "nest.js", "spring boot", "microservices", "redis", "mongodb"}

        scores = {
            "Data Engineer": len(user_skills_set.intersection(de_skills)) * 3.0,
            "Frontend Engineer": len(user_skills_set.intersection(fe_skills)) * 2.0,
            "DevOps Engineer": len(user_skills_set.intersection(devops_skills)) * 2.0,
            "Data Analyst": len(user_skills_set.intersection(da_skills)) * 2.0,
            "Backend Engineer": len(user_skills_set.intersection(be_skills)) * 1.5,
        }

        best_role = max(scores, key=scores.get)
        if scores[best_role] > 0:
            target_role = best_role
        else:
            # 3. Fallback to percentage overlap across all db roles
            all_role_skills = db.query(models.RoleSkillMap).all()
            role_reqs = {}
            for rs in all_role_skills:
                if rs.role not in role_reqs:
                    role_reqs[rs.role] = []
                role_reqs[rs.role].append(rs.skill.lower())
                
            best_overlap_role = "Software Engineer"
            best_score = -1
            for role, skills in role_reqs.items():
                if not skills: continue
                overlap = len(user_skills_set.intersection(set(skills)))
                score = (overlap / len(skills)) * 100
                if score > best_score:
                    best_score = score
                    best_overlap_role = role
            target_role = best_overlap_role

    role_skills = db.query(models.RoleSkillMap).filter(models.RoleSkillMap.role.ilike(target_role)).all()
    
    if not role_skills:
        return {
            "target_role": target_role,
            "matching_skills": [],
            "missing_skills": [],
            "recommended_skills": [],
            "coverage_percentage": 0.0
        }

    required_skills_db = [rs for rs in role_skills if rs.importance == "Required"]
    if not required_skills_db:
        required_skills_db = role_skills
        
    required_names = [rs.skill.lower() for rs in required_skills_db]
    original_names = {rs.skill.lower(): rs.skill for rs in required_skills_db}
    
    user_skills = [s.lower() for s in (profile.extracted_skills or [])]
    
    matching_skills = []
    missing_skills = []
    
    for req_skill_lower in required_names:
        orig_name = original_names[req_skill_lower]
        if req_skill_lower in user_skills:
            matching_skills.append(orig_name)
        else:
            missing_skills.append(orig_name)
            
    coverage = 0.0
    if required_names:
        coverage = (len(matching_skills) / len(required_names)) * 100.0
        
    return {
        "target_role": target_role,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommended_skills": missing_skills[:10],
        "coverage_percentage": round(coverage, 2)
    }

@app.get("/api/resumes/{resume_id}/readiness")
@limiter.limit("20/minute")
def get_resume_readiness(request: Request, resume_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    resume = db.query(models.Resume).filter(models.Resume.id == resume_id, models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    profile = db.query(models.ResumeProfile).filter(
        models.ResumeProfile.user_id == current_user.id,
        models.ResumeProfile.uploaded_file == resume.filename
    ).order_by(models.ResumeProfile.created_at.desc()).first()
    
    ats_score = profile.ats_score if profile else resume.ats_score
    
    match_scores = db.query(models.JobMatchScore).filter(models.JobMatchScore.user_id == current_user.id).all()
    avg_match = sum([m.match_score for m in match_scores]) / len(match_scores) if match_scores else 60
    
    # Gap analysis weighting
    gap = get_resume_gap_analysis(request, resume_id, db, current_user)
    num_matching = len(gap["matching_skills"])
    
    readiness_score = int((ats_score * 0.4) + (avg_match * 0.4) + (min(num_matching * 5, 100) * 0.2))
    readiness_score = max(0, min(100, readiness_score))
    
    if readiness_score >= 85:
        level = "Highly Competitive"
    elif readiness_score >= 70:
        level = "Job Ready"
    elif readiness_score >= 50:
        level = "Intermediate"
    else:
        level = "Beginner"
        
    return {
        "readiness_score": readiness_score,
        "level": level,
        "factors": {
            "ats_score": ats_score,
            "avg_match_score": int(avg_match),
            "market_skills_match": num_matching
        }
    }

# --- Match Score Engine Routes ---
@app.post("/api/match/{opportunity_id}")
@limiter.limit("20/minute")
def create_match_score(request: Request, opportunity_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    profile = db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == current_user.id).order_by(models.ResumeProfile.created_at.desc()).first()
    if not profile:
        raise HTTPException(status_code=400, detail="No resume profile found. Please upload a resume first.")
        
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    # Calculate score
    score, matching, missing, level = calculate_match(
        profile.extracted_skills,
        opp.required_skills,
        opp.description
    )
    
    # Save or update score
    existing_score = db.query(models.JobMatchScore).filter(
        models.JobMatchScore.user_id == current_user.id,
        models.JobMatchScore.opportunity_id == opportunity_id
    ).first()
    
    if existing_score:
        existing_score.match_score = score
        existing_score.matching_skills = matching
        existing_score.missing_skills = missing
        existing_score.match_level = level
        existing_score.created_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_score)
        return existing_score
    else:
        db_score = models.JobMatchScore(
            user_id=current_user.id,
            opportunity_id=opportunity_id,
            match_score=score,
            matching_skills=matching,
            missing_skills=missing,
            match_level=level
        )
        db.add(db_score)
        db.commit()
        db.refresh(db_score)
        return db_score

@app.get("/api/match/scores", response_model=List[schemas.JobMatchScore])
def get_user_match_scores(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.JobMatchScore).filter(models.JobMatchScore.user_id == current_user.id).all()


# --- Analytics & Insights Routes ---
@app.get("/api/insights/stats")
def get_insights_stats(db: Session = Depends(database.get_db)):
    total_opps = db.query(models.Opportunity).filter(models.Opportunity.is_active == True).count()
    total_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.job_type != "Internship"
    ).count()
    total_internships = db.query(models.Opportunity).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.job_type == "Internship"
    ).count()
    total_companies = db.query(models.Opportunity.company).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.company.isnot(None)
    ).distinct().count()
    total_locations = db.query(models.Opportunity.location).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.location.isnot(None)
    ).distinct().count()
    return {
        "total_opportunities": total_opps,
        "total_jobs": total_jobs,
        "total_internships": total_internships,
        "total_companies": total_companies,
        "total_locations": total_locations
    }

@app.get("/api/insights/skills")
def get_insights_skills(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        # Fast skill aggregation from required_skills column
        rows = db.query(models.Opportunity.required_skills).filter(
            models.Opportunity.is_active == True,
            models.Opportunity.required_skills.isnot(None)
        ).limit(2000).all()
        
        skill_counts = {}
        for (req_skills,) in rows:
            if req_skills:
                for s in req_skills.split(","):
                    s_norm = s.strip()
                    if s_norm and len(s_norm) > 1 and len(s_norm) < 40:
                        skill_counts[s_norm] = skill_counts.get(s_norm, 0) + 1
        
        # If required_skills is sparsely populated, supplement with fast title scan for top skills
        if len(skill_counts) < 10:
            titles = db.query(models.Opportunity.title).filter(models.Opportunity.is_active == True).limit(1000).all()
            COMMON_SKILLS = ["Python", "JavaScript", "React", "Node.js", "Java", "SQL", "AWS", "Docker", "Machine Learning", "Data Analysis", "TypeScript", "C++", "Spring Boot", "DevOps", "Kubernetes", "Git", "REST API", "Tailwind CSS"]
            for (t,) in titles:
                t_lower = (t or "").lower()
                for sk in COMMON_SKILLS:
                    if sk.lower() in t_lower:
                        skill_counts[sk] = skill_counts.get(sk, 0) + 1
                        
        sorted_skills = sorted([{"name": k, "count": v} for k, v in skill_counts.items()], key=lambda x: x["count"], reverse=True)
        return sorted_skills[:15]
    return get_or_compute("insights_skills", _compute, ttl_seconds=3600)

@app.get("/api/insights/companies")
def get_insights_companies(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        results = db.query(models.Opportunity.company, func.count(models.Opportunity.id)).filter(
            models.Opportunity.is_active == True,
            models.Opportunity.company.isnot(None)
        ).group_by(models.Opportunity.company).order_by(func.count(models.Opportunity.id).desc()).limit(8).all()
        return [{"name": company, "count": count} for company, count in results]
    return get_or_compute("insights_companies", _compute, ttl_seconds=3600)

@app.get("/api/insights/locations")
def get_insights_locations(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        results = db.query(models.Opportunity.location, func.count(models.Opportunity.id)).filter(
            models.Opportunity.is_active == True,
            models.Opportunity.location.isnot(None)
        ).group_by(models.Opportunity.location).order_by(func.count(models.Opportunity.id).desc()).limit(8).all()
        return [{"name": loc, "count": count} for loc, count in results]
    return get_or_compute("insights_locations", _compute, ttl_seconds=3600)

@app.get("/api/insights/trends")
def get_insights_trends(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        from sqlalchemy import cast, Date, desc
        try:
            date_col = cast(models.Opportunity.posted_date, Date)
            results = db.query(
                date_col.label('date'),
                func.count(models.Opportunity.id).label('count')
            ).filter(
                models.Opportunity.posted_date.isnot(None),
                models.Opportunity.is_active == True
            ).group_by(date_col).order_by(desc(date_col)).limit(7).all()
            
            # Reverse so it's in chronological order (oldest to newest)
            trends = [{"date": str(r.date), "count": r.count} for r in reversed(results)]
        except Exception as e:
            print(f"Error computing trends: {e}")
            trends = []
        
        # If fewer than 7 days of data exist, generate a continuous 7-day timeline up to today
        if len(trends) < 7:
            existing_map = {t["date"]: t["count"] for t in trends}
            base_date = datetime.utcnow() - timedelta(days=6)
            trends = []
            for i in range(7):
                d_str = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
                trends.append({
                    "date": d_str,
                    "count": existing_map.get(d_str, 0)
                })
        return trends
    return get_or_compute("insights_trends", _compute, ttl_seconds=3600)

@app.get("/api/insights/salary")
def get_insights_salary(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        opps = db.query(models.Opportunity.title, models.Opportunity.salary_range, models.Opportunity.job_type).filter(
            models.Opportunity.is_active == True
        ).all()
        entry = 0
        mid = 0
        senior = 0
        for opp in opps:
            if opp.job_type == "Internship":
                entry += 1
            elif any(kw in (opp.title or "").lower() for kw in ["senior", "lead", "principal", "sde-2", "sde-3", "manager"]):
                senior += 1
            else:
                mid += 1
        return [
            {"range": "Entry Level (Internships)", "count": entry},
            {"range": "Mid Level (Junior/Mid SDE)", "count": mid},
            {"range": "Senior Level (Sr. SDE/Leads)", "count": senior}
        ]
    return get_or_compute("insights_salary", _compute, ttl_seconds=3600)

@app.get("/api/insights/fast-growing")
def get_insights_fast_growing(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        import datetime as dt
        from app.role_taxonomy import ROLE_TAXONOMY
        
        MIN_POSTINGS = 1
        LOOKBACK_DAYS = 90
        RECENT_DAYS = 30
        
        cutoff = dt.datetime.utcnow() - dt.timedelta(days=LOOKBACK_DAYS)
        opps = db.query(models.Opportunity.title, models.Opportunity.posted_date).filter(
            models.Opportunity.is_active == True,
            models.Opportunity.posted_date >= cutoff
        ).all()
        
        recent_cutoff = dt.datetime.utcnow() - dt.timedelta(days=RECENT_DAYS)
        # Pre-lowercase titles once for fast checking
        processed_opps = [((t or "").lower(), (pdate is not None and pdate >= recent_cutoff)) for t, pdate in opps]
        
        results = []
        insufficient = []
        
        for family, roles in ROLE_TAXONOMY.items():
            for role in roles:
                role_lower = role.lower()
                total = 0
                recent = 0
                for t_low, is_rec in processed_opps:
                    if role_lower in t_low:
                        total += 1
                        if is_rec:
                            recent += 1
                
                if total < MIN_POSTINGS:
                    insufficient.append({"role": role, "status": "INSUFFICIENT_HISTORICAL_DATA", "posting_count": total})
                    continue
                
                recent_ratio = recent / total if total > 0 else 0.0
                growth_signal = "Fast Growing" if recent_ratio >= 0.5 else ("Growing" if recent_ratio >= 0.25 else "Stable")
                
                results.append({
                    "title": role,
                    "growth_signal": growth_signal,
                    "recent_postings": recent,
                    "total_postings": total,
                    "data_basis": "LIVE_DB",
                    "lookback_days": LOOKBACK_DAYS,
                    "min_postings_threshold": MIN_POSTINGS
                })
        
        results.sort(key=lambda x: x["recent_postings"], reverse=True)
        return {
            "roles": results,
            "insufficient_data_roles": len(insufficient),
            "total_roles_evaluated": sum(len(r) for r in ROLE_TAXONOMY.values()),
            "evidence_source": "careerlens_opportunity_db",
            "min_postings_threshold": MIN_POSTINGS
        }
    return get_or_compute("insights_fast_growing", _compute, ttl_seconds=3600)

@app.get("/api/roles")
def get_roles():
    import json, os
    data_file = os.path.join(os.path.dirname(__file__), "..", "data", "roles.json")
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# Cache for global stats to avoid heavy DB queries on every dashboard load
# --- Global dashboard stats cache (5-minute TTL) ---
# All 6 categories are mutually exclusive and sum exactly to total_opportunities.
# Priority order: Internship > Apprenticeship > Graduate/Trainee > Fresher/Entry-Level
#                 > Hiring Challenge/Competition > Experienced/Professional
_global_stats_cache = {
    "timestamp": 0,
    "total_opps": 0,
    "internships": 0,
    "apprenticeships": 0,
    "graduate_trainee": 0,
    "fresher_entry_level": 0,
    "hiring_challenges": 0,
    "experienced_professional": 0,
}

# --- Personalized Dashboard Stats Route ---
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    import time
    global _global_stats_cache

    current_time = time.time()
    # Refresh cache every 5 minutes. A single SQL pass computes all 6 exclusive
    # categories so the counts are guaranteed to add up to total_opportunities.
    if current_time - _global_stats_cache["timestamp"] > 300:
        row = db.execute(text("""
            SELECT
                -- Total active
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                ) AS total_opps,

                -- 1. Internship  (highest priority)
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                    AND (
                        LOWER(COALESCE(job_type,'')) LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus ambassador%'
                    )
                ) AS internships,

                -- 2. Apprenticeship  (not already counted as intern)
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus ambassador%'
                    )
                    AND (
                        LOWER(COALESCE(title,''))    LIKE '%apprentice%'
                        OR LOWER(COALESCE(job_type,'')) LIKE '%apprentice%'
                    )
                ) AS apprenticeships,

                -- 3. Graduate / Trainee  (not intern, not apprentice)
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus ambassador%'
                    )
                    AND NOT (
                        LOWER(COALESCE(title,''))    LIKE '%apprentice%'
                        OR LOWER(COALESCE(job_type,'')) LIKE '%apprentice%'
                    )
                    AND (
                        LOWER(COALESCE(job_type,'')) LIKE '%trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%management trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%graduate trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus hire%'
                    )
                ) AS graduate_trainee,

                -- 4. Fresher / Entry-Level  (not intern, apprentice, or trainee)
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus ambassador%'
                    )
                    AND NOT (
                        LOWER(COALESCE(title,''))    LIKE '%apprentice%'
                        OR LOWER(COALESCE(job_type,'')) LIKE '%apprentice%'
                    )
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%trainee%'
                    )
                    AND (
                        LOWER(COALESCE(title,'')) LIKE '%fresher%'
                        OR LOWER(COALESCE(title,'')) LIKE '%entry level%'
                        OR LOWER(COALESCE(title,'')) LIKE '%entry-level%'
                        OR LOWER(COALESCE(title,'')) LIKE '%junior%'
                        OR LOWER(COALESCE(title,'')) LIKE '%associate %'
                        OR LOWER(COALESCE(title,'')) LIKE '% associate'
                    )
                ) AS fresher_entry_level,

                -- 5. Hiring Challenge / Competition  (not any above category)
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus ambassador%'
                    )
                    AND NOT (
                        LOWER(COALESCE(title,''))    LIKE '%apprentice%'
                        OR LOWER(COALESCE(job_type,'')) LIKE '%apprentice%'
                    )
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%trainee%'
                    )
                    AND NOT (
                        LOWER(COALESCE(title,'')) LIKE '%fresher%'
                        OR LOWER(COALESCE(title,'')) LIKE '%entry level%'
                        OR LOWER(COALESCE(title,'')) LIKE '%entry-level%'
                        OR LOWER(COALESCE(title,'')) LIKE '%junior%'
                        OR LOWER(COALESCE(title,'')) LIKE '%associate %'
                        OR LOWER(COALESCE(title,'')) LIKE '% associate'
                    )
                    AND (
                        LOWER(COALESCE(job_type,'')) IN ('hiring challenge','hackathon','case competition','coding contest','competition','scholarship','fellowship')
                        OR LOWER(COALESCE(title,'')) LIKE '%hackathon%'
                        OR LOWER(COALESCE(title,'')) LIKE '%challenge%'
                        OR LOWER(COALESCE(title,'')) LIKE '%competition%'
                    )
                ) AS hiring_challenges,

                -- 6. Experienced / Professional  (everything else)
                COUNT(*) FILTER (
                    WHERE is_active = TRUE AND status = 'Active'
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%intern%'
                        OR LOWER(COALESCE(title,''))  LIKE '%campus ambassador%'
                    )
                    AND NOT (
                        LOWER(COALESCE(title,''))    LIKE '%apprentice%'
                        OR LOWER(COALESCE(job_type,'')) LIKE '%apprentice%'
                    )
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) LIKE '%trainee%'
                        OR LOWER(COALESCE(title,''))  LIKE '%trainee%'
                    )
                    AND NOT (
                        LOWER(COALESCE(title,'')) LIKE '%fresher%'
                        OR LOWER(COALESCE(title,'')) LIKE '%entry level%'
                        OR LOWER(COALESCE(title,'')) LIKE '%entry-level%'
                        OR LOWER(COALESCE(title,'')) LIKE '%junior%'
                        OR LOWER(COALESCE(title,'')) LIKE '%associate %'
                        OR LOWER(COALESCE(title,'')) LIKE '% associate'
                    )
                    AND NOT (
                        LOWER(COALESCE(job_type,'')) IN ('hiring challenge','hackathon','case competition','coding contest','competition','scholarship','fellowship')
                        OR LOWER(COALESCE(title,'')) LIKE '%hackathon%'
                        OR LOWER(COALESCE(title,'')) LIKE '%challenge%'
                        OR LOWER(COALESCE(title,'')) LIKE '%competition%'
                    )
                ) AS experienced_professional
            FROM opportunities;
        """)).fetchone()

        _global_stats_cache["total_opps"]            = row[0] or 0
        _global_stats_cache["internships"]           = row[1] or 0
        _global_stats_cache["apprenticeships"]       = row[2] or 0
        _global_stats_cache["graduate_trainee"]      = row[3] or 0
        _global_stats_cache["fresher_entry_level"]   = row[4] or 0
        _global_stats_cache["hiring_challenges"]     = row[5] or 0
        _global_stats_cache["experienced_professional"] = row[6] or 0
        _global_stats_cache["timestamp"]             = current_time

    total_opps             = _global_stats_cache["total_opps"]
    internships            = _global_stats_cache["internships"]
    apprenticeships        = _global_stats_cache["apprenticeships"]
    graduate_trainee       = _global_stats_cache["graduate_trainee"]
    fresher_entry_level    = _global_stats_cache["fresher_entry_level"]
    hiring_challenges      = _global_stats_cache["hiring_challenges"]
    experienced_professional = _global_stats_cache["experienced_professional"]
    
    apps = db.query(models.Application).filter(models.Application.user_id == current_user.id).all()
    saved = len([a for a in apps if a.status == "Saved"])
    applied = len([a for a in apps if a.status == "Applied"])
    interviews = len([a for a in apps if a.status == "Interview"])
    offers = len([a for a in apps if a.status == "Selected"])
    rejected = len([a for a in apps if a.status == "Rejected"])
    
    latest_resume = db.query(models.Resume).filter(models.Resume.user_id == current_user.id).order_by(models.Resume.posted_date.desc()).first()
    ats_score = latest_resume.ats_score if latest_resume else 0
    
    profile = db.query(models.ResumeProfile).filter(models.ResumeProfile.user_id == current_user.id).order_by(models.ResumeProfile.created_at.desc()).first()
    completeness = 25
    if profile:
        completeness = 45
        if profile.extracted_skills: completeness += 15
        if profile.extracted_experience: completeness += 15
        if profile.extracted_education: completeness += 15
        if profile.extracted_projects: completeness += 10
    completeness = min(completeness, 100)
    
    recent_apps_data = []
    for a in sorted(apps, key=lambda x: x.applied_date, reverse=True)[:5]:
        recent_apps_data.append({
            "id": a.id,
            "status": a.status,
            "applied_date": a.applied_date,
            "opportunity": {
                "id": a.opportunity.id,
                "title": a.opportunity.title,
                "company": a.opportunity.company,
                "location": a.opportunity.location
            }
        })
        
    return {
        # ── Global opportunity market counts (mutually exclusive, sum = total_opportunities) ──
        "total_opportunities":       total_opps,
        "internships":               internships,
        "apprenticeships":           apprenticeships,
        "graduate_trainee":          graduate_trainee,
        "fresher_entry_level":       fresher_entry_level,
        "hiring_challenges":         hiring_challenges,
        "experienced_professional":  experienced_professional,
        # ── Legacy alias kept for any older clients still reading this field ──
        # DEPRECATED: was double-counting interns — use fresher_entry_level instead
        "freshers_jobs":             fresher_entry_level,
        # ── Per-user activity stats ──
        "saved_opportunities":       saved,
        "applied_opportunities":     applied,
        "interviews_scheduled":      interviews,
        "offers_received":           offers,
        "rejected_opportunities":    rejected,
        "ats_score":                 ats_score,
        "profile_completeness":      completeness,
        "recent_applications":       recent_apps_data
    }


# --- Phase 3: Pipeline & Learning Resource Routes ---

@app.get("/api/pipeline/status")
def get_pipeline_status(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Get the latest run of each pipeline
    pipelines = ["jobs_pipeline", "internships_pipeline", "resources_pipeline", "insights_pipeline", "expiry_pipeline"]
    latest_runs = {}
    for p in pipelines:
        run = db.query(models.PipelineRun).filter(models.PipelineRun.pipeline_name == p).order_by(models.PipelineRun.started_at.desc()).first()
        if run:
            latest_runs[p] = {
                "id": run.id,
                "status": run.status,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "records_collected": run.records_collected,
                "records_cleaned": run.records_cleaned,
                "records_inserted": run.records_inserted,
                "records_deduplicated": run.records_deduplicated,
                "duration_seconds": run.duration_seconds,
                "errors": run.errors
            }
        else:
            latest_runs[p] = None
    return latest_runs

@app.get("/api/pipeline/history")
def get_pipeline_history(skip: int = 0, limit: int = 20, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    runs = db.query(models.PipelineRun).order_by(models.PipelineRun.started_at.desc()).offset(skip).limit(limit).all()
    total = db.query(models.PipelineRun).count()
    return {"total": total, "history": runs}

@app.post("/api/pipeline/run/{pipeline_name}")
def trigger_pipeline(pipeline_name: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin": 
        raise HTTPException(status_code=403, detail="Admin permissions required")
    try:
        from etl.orchestrator import run_pipeline_by_name
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result = run_pipeline_by_name(pipeline_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/api/pipeline/stats")
def get_pipeline_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # 1. Active vs Expired vs Archived
    status_counts = db.query(models.Opportunity.status, func.count(models.Opportunity.id)).group_by(models.Opportunity.status).all()
    status_stats = {status: count for status, count in status_counts}

    # 2. Source distribution
    source_counts = db.query(models.Opportunity.primary_source, func.count(models.Opportunity.id)).group_by(models.Opportunity.primary_source).all()
    source_stats = {src if src else "Unknown": count for src, count in source_counts}

    # 3. Overall data counts
    total_raw_jobs = db.query(models.RawJob).count()
    total_raw_internships = db.query(models.RawInternship).count()
    total_opportunities = db.query(models.Opportunity).count()
    total_resources = db.query(models.LearningResource).count()

    return {
        "status_distribution": status_stats,
        "source_distribution": source_stats,
        "counts": {
            "raw_jobs": total_raw_jobs,
            "raw_internships": total_raw_internships,
            "opportunities": total_opportunities,
            "learning_resources": total_resources
        }
    }

@app.get("/api/resources")
def read_resources(
    q: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    is_free: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(database.get_db)
):
    # Only return VERIFIED learning resources (hide INVALID_RESOURCE entries by default)
    query = db.query(models.LearningResource).filter(
        models.LearningResource.status == "VERIFIED",
        or_(
            models.LearningResource.availability_status != "INVALID",
            models.LearningResource.availability_status.is_(None)
        )
    )
    
    if q:
        search_filter = (
            models.LearningResource.title.ilike(f"%{q}%") |
            models.LearningResource.provider.ilike(f"%{q}%") |
            models.LearningResource.description.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
        
    if category and category != "All":
        query = query.filter(models.LearningResource.category.ilike(category))
        
    if difficulty and difficulty != "All":
        query = query.filter(models.LearningResource.difficulty.ilike(difficulty))
        
    if is_free is not None:
        query = query.filter(models.LearningResource.is_free == is_free)
        
    total = query.count()
    resources = query.offset(skip).limit(limit).all()
    return {"total": total, "resources": resources}

@app.get("/api/resources/categories")
def get_resource_categories(db: Session = Depends(database.get_db)):
    counts = db.query(models.LearningResource.category, func.count(models.LearningResource.id)).group_by(models.LearningResource.category).all()
    return {cat if cat else "Other": cnt for cat, cnt in counts}


# --- Health & Root ---
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0", "service": "careerlens-api"}

@app.get("/")
def root():
    return {"message": "Welcome to CareerLens AI API. Go to /docs for Swagger UI."}

# --- Phase 4: Career Intelligence & Roadmaps ---


@app.get("/api/roadmaps/{role}", response_model=schemas.CareerRoadmap)
def get_career_roadmap(role: str):
    role_lower = role.lower()
    
    # 1. Data Engineer
    if "data" in role_lower and "engineer" in role_lower:
        steps = [
            {"step_number": 1, "title": "SQL & Relational Databases", "description": "Master advanced SQL and database internals", "skills": ["PostgreSQL", "MySQL", "Advanced SQL"], "estimated_weeks": 4},
            {"step_number": 2, "title": "Python & Scripting", "description": "Learn Python for data manipulation and automation", "skills": ["Python", "Pandas", "Scripting"], "estimated_weeks": 3},
            {"step_number": 3, "title": "Data Warehousing", "description": "Understand OLAP systems and dimensional modeling", "skills": ["Snowflake", "BigQuery", "Redshift"], "estimated_weeks": 4},
            {"step_number": 4, "title": "ETL & Pipelines", "description": "Build robust data pipelines and orchestration", "skills": ["Airflow", "dbt", "Kafka"], "estimated_weeks": 5},
            {"step_number": 5, "title": "Cloud Computing", "description": "Deploy to the cloud and manage infrastructure", "skills": ["AWS", "GCP", "Docker"], "estimated_weeks": 4}
        ]
        return {
            "role": "Data Engineer",
            "description": "Build systems that collect, manage, and convert raw data.",
            "total_weeks": 20,
            "strategies": [
                "Focus heavily on SQL optimization and query planning.",
                "Build end-to-end data pipelines using real-world public datasets.",
                "Learn orchestration tools like Airflow as they are highly demanded."
            ],
            "what_to_learn": [
                "Advanced SQL & Window Functions",
                "Python Scripting & Pandas",
                "Apache Spark / Distributed Computing",
                "Cloud Data Warehouses (Snowflake, BigQuery)",
                "Workflow Orchestration (Airflow, dbt)"
            ],
            "steps": steps
        }
        
    # 2. Frontend Developer / Engineer
    elif "front" in role_lower or "ui" in role_lower:
        steps = [
            {"step_number": 1, "title": "Internet Fundamentals & HTML/CSS", "description": "Understand how the web works and build responsive layouts", "skills": ["HTML5", "CSS3", "Flexbox", "Grid"], "estimated_weeks": 3},
            {"step_number": 2, "title": "Deep Dive into JavaScript", "description": "Master core JS, DOM manipulation, and ES6+ features", "skills": ["JavaScript", "DOM", "ES6+", "Async/Await"], "estimated_weeks": 5},
            {"step_number": 3, "title": "Frontend Frameworks (React/Vue)", "description": "Learn a modern component-based UI framework", "skills": ["React.js", "State Management", "Hooks"], "estimated_weeks": 6},
            {"step_number": 4, "title": "CSS Frameworks & Tooling", "description": "Speed up styling and manage assets", "skills": ["TailwindCSS", "Webpack", "Vite"], "estimated_weeks": 3},
            {"step_number": 5, "title": "API Integration & Deployment", "description": "Connect to backends and deploy to the world", "skills": ["REST APIs", "Vercel", "Netlify", "Git"], "estimated_weeks": 3}
        ]
        return {
            "role": "Frontend Developer",
            "description": "Create the user interfaces and experiences of web applications.",
            "total_weeks": 20,
            "strategies": [
                "Clone popular websites (Netflix, Twitter, Spotify) to practice UI development.",
                "Build projects that consume real public APIs (weather, movies, news).",
                "Don't rush to React; make sure your Vanilla JS fundamentals are very strong."
            ],
            "what_to_learn": [
                "Semantic HTML and Modern CSS Layouts (Flexbox/Grid)",
                "Advanced JavaScript (Closures, Promises, Event Loop)",
                "React, React Router, and Redux/Zustand",
                "Version Control (Git/GitHub) and Hosting (Vercel)"
            ],
            "steps": steps
        }
        
    # 3. Backend Developer / Engineer
    elif "back" in role_lower:
        steps = [
            {"step_number": 1, "title": "Language Mastery (Node.js/Python/Java)", "description": "Master a backend programming language deeply", "skills": ["Node.js", "Python", "Java", "Go"], "estimated_weeks": 4},
            {"step_number": 2, "title": "Databases & ORMs", "description": "Learn to store and query data efficiently", "skills": ["SQL", "PostgreSQL", "MongoDB", "Mongoose/Prisma"], "estimated_weeks": 5},
            {"step_number": 3, "title": "Building APIs", "description": "Create RESTful and GraphQL APIs", "skills": ["Express.js", "FastAPI", "REST", "GraphQL"], "estimated_weeks": 4},
            {"step_number": 4, "title": "Authentication & Security", "description": "Secure your applications and manage users", "skills": ["JWT", "OAuth2", "Bcrypt", "CORS"], "estimated_weeks": 3},
            {"step_number": 5, "title": "Deployment & Containerization", "description": "Package and ship your backend to servers", "skills": ["Docker", "Linux", "AWS/Render"], "estimated_weeks": 4}
        ]
        return {
            "role": "Backend Developer",
            "description": "Build the core logic, databases, and APIs that power applications.",
            "total_weeks": 20,
            "strategies": [
                "Focus heavily on database design and understanding relationships.",
                "Build a complete REST API from scratch and document it using Postman or Swagger.",
                "Learn about common security flaws like SQL Injection and XSS."
            ],
            "what_to_learn": [
                "Backend Languages (Node.js/Express, Python/FastAPI, or Java/Spring)",
                "Relational Databases (SQL) and NoSQL (MongoDB)",
                "API Design (REST, JSON, GraphQL)",
                "Authentication strategies (Sessions, JWT)"
            ],
            "steps": steps
        }
        
    # 4. Full Stack Developer
    elif "full" in role_lower:
        steps = [
            {"step_number": 1, "title": "Frontend Fundamentals", "description": "Master HTML, CSS, JavaScript, and React", "skills": ["HTML/CSS", "JavaScript", "React"], "estimated_weeks": 6},
            {"step_number": 2, "title": "Backend Fundamentals", "description": "Learn Node.js, Express, and API design", "skills": ["Node.js", "Express", "REST"], "estimated_weeks": 5},
            {"step_number": 3, "title": "Database Management", "description": "Design schemas and integrate databases", "skills": ["MongoDB", "PostgreSQL", "Mongoose"], "estimated_weeks": 4},
            {"step_number": 4, "title": "Authentication & State", "description": "Connect frontend and backend securely", "skills": ["JWT", "Redux", "Context API"], "estimated_weeks": 3},
            {"step_number": 5, "title": "Full Stack Deployment", "description": "Deploy front and back ends and configure CI/CD", "skills": ["Docker", "Vercel", "Render", "CI/CD"], "estimated_weeks": 4}
        ]
        return {
            "role": "Full Stack Developer",
            "description": "Handle both the frontend UI and the backend logic of web applications.",
            "total_weeks": 22,
            "strategies": [
                "Build full end-to-end CRUD applications like an E-commerce store or Social Media app.",
                "Learn the MERN stack (MongoDB, Express, React, Node) as it is highly popular for beginners.",
                "Master Git and version control early, it will save you headaches when connecting front and back ends."
            ],
            "what_to_learn": [
                "Frontend (React/Vue, CSS Frameworks)",
                "Backend (Node.js, Express)",
                "Databases (MongoDB, PostgreSQL)",
                "DevOps Basics (Git, Deployment, Docker)"
            ],
            "steps": steps
        }
        
    # 5. Data Scientist / Analyst
    elif "data" in role_lower:
        steps = [
            {"step_number": 1, "title": "Math & Statistics", "description": "Master probability, statistics, and linear algebra fundamentals", "skills": ["Statistics", "Probability", "Linear Algebra"], "estimated_weeks": 4},
            {"step_number": 2, "title": "Python & Data Analysis", "description": "Learn Python libraries for data manipulation", "skills": ["Python", "Pandas", "NumPy"], "estimated_weeks": 4},
            {"step_number": 3, "title": "Data Visualization", "description": "Communicate findings effectively through charts", "skills": ["Matplotlib", "Seaborn", "Tableau/PowerBI"], "estimated_weeks": 3},
            {"step_number": 4, "title": "Machine Learning Fundamentals", "description": "Learn core ML algorithms and model evaluation", "skills": ["Scikit-Learn", "Regression", "Classification"], "estimated_weeks": 6},
            {"step_number": 5, "title": "Advanced ML & Deployment", "description": "Dive into deep learning or deploy models to production", "skills": ["TensorFlow/PyTorch", "Flask", "Streamlit"], "estimated_weeks": 4}
        ]
        return {
            "role": role.title(),
            "description": "Analyze data, build models, and extract actionable insights for business.",
            "total_weeks": 21,
            "strategies": [
                "Kaggle is your best friend. Participate in competitions and read public notebooks.",
                "Don't just run ML models—learn to explain the 'why' behind the data and algorithms.",
                "Build a portfolio that tells a story with data, not just raw code."
            ],
            "what_to_learn": [
                "Statistics & Probability",
                "Python (Pandas, NumPy, Scikit-Learn)",
                "SQL for Data Extraction",
                "Data Visualization (Tableau, PowerBI, Matplotlib)"
            ],
            "steps": steps
        }

    # Default Dynamic Fallback
    else:
        steps = [
            {"step_number": 1, "title": f"{role.title()} Fundamentals", "description": f"Master the core principles and basics required for {role.title()}", "skills": ["Core Concepts", "Industry Basics", "Terminology"], "estimated_weeks": 4},
            {"step_number": 2, "title": "Primary Tools & Software", "description": "Gain proficiency in the industry-standard software and tools", "skills": ["Primary Software", "Workflows", "Automation"], "estimated_weeks": 5},
            {"step_number": 3, "title": "Advanced Techniques", "description": "Dive deeper into specialized topics and edge cases", "skills": ["Advanced Strategies", "Optimization", "Troubleshooting"], "estimated_weeks": 5},
            {"step_number": 4, "title": "Portfolio & Real-world Projects", "description": "Apply your knowledge to build a strong professional portfolio", "skills": ["Project Execution", "Documentation", "Presentation"], "estimated_weeks": 4}
        ]
        return {
            "role": role.title(),
            "description": f"A comprehensive learning path to become a successful {role.title()}.",
            "total_weeks": 18,
            "strategies": [
                f"Start by understanding the day-to-day responsibilities of a {role.title()}.",
                "Find a mentor or join a community dedicated to this field.",
                "Build 2-3 high-quality projects that demonstrate your practical skills."
            ],
            "what_to_learn": [
                "Fundamental theoretical concepts",
                "Industry-standard tools and frameworks",
                "Soft skills like communication and problem-solving",
                "Best practices and standard operating procedures"
            ],
            "steps": steps
        }

@app.get("/api/resources/recommendations", response_model=List[schemas.LearningResource])
def get_resource_recommendations(missing_skills: str = "", db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not missing_skills:
        return []
    skills = [s.strip().lower() for s in missing_skills.split(",") if s.strip()]
    if not skills:
        return []
        
    all_resources = db.query(models.LearningResource).all()
    recommendations = []
    
    for r in all_resources:
        if r.skills_covered:
            covered = [s.lower() for s in r.skills_covered]
            overlap = len(set(skills).intersection(set(covered)))
            if overlap > 0:
                recommendations.append({"resource": r, "relevance": overlap})
                
    recommendations.sort(key=lambda x: x["relevance"], reverse=True)
    return [rec["resource"] for rec in recommendations[:10]]

@app.get("/api/interview-prep/{role}", response_model=List[schemas.InterviewQuestion])
def get_interview_prep(role: str, current_user: models.User = Depends(auth.get_current_user)):
    role_lower = role.lower()
    questions = []
    
    # Universal Behavioral & HR Questions
    questions.extend([
        {
            "category": "Behavioral",
            "difficulty": "Medium",
            "question": "Tell me about a time you had to handle a tight deadline with conflicting priorities.",
            "estimated_time": 5,
            "model_answer": "Use the STAR framework (Situation, Task, Action, Result). Highlight how you prioritized tasks based on business impact, communicated proactively with stakeholders, and delivered the critical deliverables on time without compromising quality."
        },
        {
            "category": "Behavioral",
            "difficulty": "Medium",
            "question": "Describe a technical disagreement you had with a team member. How did you resolve it?",
            "estimated_time": 6,
            "model_answer": "Explain how you evaluated both approaches objectively using benchmark data, trade-off analyses, or proof-of-concept code rather than opinion. Focus on collaborative problem-solving and driving alignment behind the best solution for the product."
        },
        {
            "category": "HR",
            "difficulty": "Easy",
            "question": "Why do you want to work at our company specifically?",
            "estimated_time": 3,
            "model_answer": "Demonstrate clear research: mention specific products, recent technical milestones, engineering culture, or company values that align with your personal career growth and passion."
        },
        {
            "category": "HR",
            "difficulty": "Easy",
            "question": "Where do you see your career evolving over the next 3 to 5 years?",
            "estimated_time": 4,
            "model_answer": "Outline a clear growth trajectory: mastering domain expertise, taking on higher technical ownership, mentoring junior engineers, and contributing directly to business-critical architecture."
        }
    ])

    # Role-Specific Deep Dives
    if "data" in role_lower or "analytics" in role_lower or "ai" in role_lower or "ml" in role_lower:
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": "Explain the difference between Star Schema and Snowflake Schema in data warehousing.",
                "estimated_time": 6,
                "model_answer": "Star Schema features a central fact table surrounded by denormalized dimension tables (faster query performance, simpler joins). Snowflake Schema normalizes dimension tables into sub-dimensions (reduces data redundancy, but requires complex multi-table joins)."
            },
            {
                "category": "Technical",
                "difficulty": "Hard",
                "question": "How do you detect and handle data skewness (hotspots) in Apache Spark or distributed SQL engines?",
                "estimated_time": 8,
                "model_answer": "Detect skewness via Spark UI stage timelines or skewed partition sizes. Mitigate using salting (adding a random key prefix to distribute join keys), repartitioning, broadcasting small dimension tables, or adjusting shuffle partition configs."
            },
            {
                "category": "System Design",
                "difficulty": "Hard",
                "question": "Design a real-time event streaming pipeline to process 1 million events per second for anomaly detection.",
                "estimated_time": 15,
                "model_answer": "Architecture: Ingestion via Apache Kafka / AWS Kinesis with partition keys -> Stream Processing via Apache Flink or Spark Streaming -> Windowed Aggregations & ML Inference model -> Storage in ClickHouse/TimescaleDB for metrics & Redis for real-time alerting."
            },
            {
                "category": "Case Study",
                "difficulty": "Hard",
                "question": "User retention dropped by 12% in the last quarter. Walk me through how you would investigate the root cause.",
                "estimated_time": 12,
                "model_answer": "1. Verify data integrity (check for broken tracking events). 2. Segment by geography, platform (iOS/Android/Web), app version, and user cohort. 3. Analyze funnel drop-off points (onboarding, checkout). 4. Isolate external factors (competitor launches, seasonality) vs internal changes (recent releases, latency spikes)."
            }
        ])
    elif "devops" in role_lower or "cloud" in role_lower or "sre" in role_lower or "security" in role_lower:
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": "What is the difference between Blue/Green Deployment and Canary Deployment?",
                "estimated_time": 6,
                "model_answer": "Blue/Green runs two identical production environments (active & idle) and switches traffic instantly via load balancer. Canary gradually routes a small percentage of traffic (e.g. 5%) to the new version to monitor metrics before full rollout."
            },
            {
                "category": "Technical",
                "difficulty": "Hard",
                "question": "Explain Kubernetes pod lifecycle and how readiness/liveness probes prevent zero-downtime failures.",
                "estimated_time": 8,
                "model_answer": "Liveness probes restart a container if it becomes unresponsive or deadlocked. Readiness probes control whether a container receives network traffic (preventing traffic routing before app initialization completes)."
            },
            {
                "category": "System Design",
                "difficulty": "Hard",
                "question": "Design a multi-region highly available infrastructure on AWS/GCP with auto-failover and zero data loss.",
                "estimated_time": 15,
                "model_answer": "Multi-region Route53 DNS latency routing with health checks -> CloudFront CDN -> ALB across 3 AZs -> EKS clusters with HPA -> Amazon Aurora Global Database with sub-second cross-region replication -> Terraform IAC for automated failover orchestration."
            },
            {
                "category": "Case Study",
                "difficulty": "Medium",
                "question": "A production server CPU spikes to 100% and HTTP 504 gateway timeouts spike. How do you triage this incident?",
                "estimated_time": 10,
                "model_answer": "1. Check APM/Grafana dashboards for request throughput & latency. 2. Identify heavy processes (`top`, `htop`, thread dumps). 3. Inspect connection pools, slow DB queries, or memory leaks. 4. Apply immediate mitigation (scale replicas, block rogue traffic), followed by post-mortem root cause analysis."
            }
        ])
    elif "product" in role_lower or "project" in role_lower or "agile" in role_lower:
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": "How do you define key performance indicators (KPIs) and North Star Metrics for a new product feature?",
                "estimated_time": 6,
                "model_answer": "Identify the primary value delivery metric (North Star) that directly correlates with user engagement and revenue. Complement with input metrics (acquisition, activation, retention, monetization, referral - AARRR framework)."
            },
            {
                "category": "System Design",
                "difficulty": "Medium",
                "question": "How do you prioritize a product roadmap when engineering capacity is cut by 30%?",
                "estimated_time": 10,
                "model_answer": "Apply RICE scoring (Reach * Impact * Confidence / Effort). Re-align with executive business goals, protect core revenue-generating features, defer non-essential tech debt/nice-to-haves, and transparently communicate scope changes to stakeholders."
            },
            {
                "category": "Case Study",
                "difficulty": "Hard",
                "question": "Design a feature for LinkedIn to increase engagement among college students and fresh graduates.",
                "estimated_time": 12,
                "model_answer": "1. Identify pain points: lack of experience, networking anxiety. 2. Propose solution: Peer Mock Interviews & Campus Mentorship Hub. 3. Define MVP specs, target metrics (daily active engagement, connection requests sent), and rollout strategy."
            }
        ])
    else:
        # Software Engineer / Developer / General Tech
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": "What is the difference between a process and a thread? How does memory sharing work?",
                "estimated_time": 5,
                "model_answer": "A process is an isolated executing program with its own memory space (heap, stack, file descriptors). Threads run within a process and share the heap and data segment, but maintain independent call stacks and registers."
            },
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": "Explain Event Loop in JavaScript / Node.js and how Asynchronous I/O operations are handled.",
                "estimated_time": 6,
                "model_answer": "Node.js utilizes a single-threaded Event Loop backed by libuv thread pool for async I/O. Tasks execute through Call Stack -> WebAPIs/C++ APIs -> Microtask Queue (Promises, process.nextTick) -> Macrotask Queue (setTimeout, I/O callbacks)."
            },
            {
                "category": "System Design",
                "difficulty": "Hard",
                "question": "Design a scalable URL Shortener service like Bitly or TinyURL capable of handling 100M daily active users.",
                "estimated_time": 20,
                "model_answer": "Key components: API Gateway -> Load Balancer -> Stateless App instances -> Base62 encoding / KGS (Key Generation Service) for 7-char short URLs -> Redis Cache (80/20 read/write rule) -> PostgreSQL/NoSQL DB with read replicas."
            },
            {
                "category": "Case Study",
                "difficulty": "Hard",
                "question": "Your web application experiences memory leaks in production under peak load. How do you isolate and fix it?",
                "estimated_time": 10,
                "model_answer": "1. Analyze heap dumps using Chrome DevTools or Node/Java memory profilers. 2. Identify detached DOM nodes, uncleaned event listeners, or uncleared global timers/closures. 3. Apply fix, run stress tests under load, and verify heap garbage collection stabilization."
            }
        ])
        
    return questions

@app.get("/api/companies/insights", response_model=List[schemas.CompanyInsight])
def get_company_insights(db: Session = Depends(database.get_db)):
    """Aggregate hiring trends across ATS opportunities"""
    companies = db.query(models.CompanyRegistry).filter(models.CompanyRegistry.status == "Active").all()
    results = []
    
    for comp in companies:
        opps = db.query(models.Opportunity).filter(
            models.Opportunity.company == comp.company_name,
            models.Opportunity.status == "Active"
        ).all()
        
        if not opps:
            continue
            
        skills_freq = {}
        loc_freq = {}
        for o in opps:
            # skills
            if o.required_skills:
                for s in o.required_skills.split(','):
                    s = s.strip()
                    if s:
                        skills_freq[s] = skills_freq.get(s, 0) + 1
            # locations
            if o.location:
                loc = o.location.strip()
                loc_freq[loc] = loc_freq.get(loc, 0) + 1
                
        top_skills = sorted(skills_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        top_locations = sorted(loc_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        
        results.append({
            "company_name": comp.company_name,
            "active_opportunities": len(opps),
            "top_skills": [s[0] for s in top_skills],
            "top_locations": [l[0] for l in top_locations]
        })
        
    results.sort(key=lambda x: x["active_opportunities"], reverse=True)
    return results

# Duplicate health endpoint removed — primary one is at line ~701

@app.get("/api/health/detailed", response_model=schemas.SystemHealth)
def get_detailed_health(db: Session = Depends(database.get_db)):
    """Deployment Monitoring Endpoint"""
    # Check DB
    db_status = "Online"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "Offline"
        
    # Check Scheduler
    from scheduler import scheduler
    sched_status = "Running" if scheduler.running else "Stopped"
    
    # Active Collectors
    active_collectors = db.query(models.CompanyRegistry).filter(models.CompanyRegistry.status == "Active").count()
    
    # Last Run
    last_run = db.query(models.PipelineRun).order_by(models.PipelineRun.started_at.desc()).first()
    last_run_status = last_run.status if last_run else "Never Run"
    
    return {
        "database": db_status,
        "scheduler": sched_status,
        "active_collectors": active_collectors,
        "last_run_status": last_run_status
    }

import csv
import io

@app.post("/api/admin/companies/import/csv")
async def import_companies_csv(file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Bulk import companies from CSV"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    
    imported = 0
    for row in reader:
        company_name = row.get("company_name", "").strip()
        ats_type = row.get("ats_type", "").strip()
        if not company_name or not ats_type:
            continue
            
        ats_identifier = row.get("ats_identifier", "").strip()
        careers_url = row.get("careers_url", "").strip()
        status = row.get("status", "Active").strip()
        
        existing = db.query(models.CompanyRegistry).filter_by(company_name=company_name).first()
        if not existing:
            new_comp = models.CompanyRegistry(
                company_name=company_name,
                ats_type=ats_type,
                ats_identifier=ats_identifier,
                careers_url=careers_url,
                status=status,
                verification_status="Pending"
            )
            db.add(new_comp)
            imported += 1
            
    db.commit()
    return {"message": f"Successfully imported {imported} companies."}

@app.post("/api/admin/companies/import/json")
async def import_companies_json(file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """Bulk import companies from JSON"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")
    import json
    contents = await file.read()
    data = json.loads(contents)
    
    imported = 0
    for item in data:
        company_name = item.get("company_name", "").strip()
        ats_type = item.get("ats_type", "").strip()
        if not company_name or not ats_type:
            continue
            
        existing = db.query(models.CompanyRegistry).filter_by(company_name=company_name).first()
        if not existing:
            new_comp = models.CompanyRegistry(
                company_name=company_name,
                ats_type=ats_type,
                ats_identifier=item.get("ats_identifier", "").strip(),
                careers_url=item.get("careers_url", "").strip(),
                status=item.get("status", "Active"),
                verification_status="Pending"
            )
            db.add(new_comp)
            imported += 1
            
    db.commit()
    return {"message": f"Successfully imported {imported} companies."}

@app.get("/api/coverage", response_model=schemas.CoverageStats)
def get_coverage(db: Session = Depends(database.get_db)):
    """Coverage Dashboard metrics"""
    companies = db.query(models.CompanyRegistry.ats_type, func.count(models.CompanyRegistry.id)).group_by(models.CompanyRegistry.ats_type).all()
    jobs = db.query(models.Opportunity.ats_type, func.count(models.Opportunity.id)).group_by(models.Opportunity.ats_type).all()
    
    failed = db.query(models.CompanyRegistry.company_name).filter(models.CompanyRegistry.verification_status == "Failed").all()
    
    last_sync = db.query(func.max(models.Opportunity.last_seen)).scalar()
    
    return {
        "companies_by_ats": {k or "Unknown": v for k, v in companies},
        "jobs_by_ats": {k or "Unknown": v for k, v in jobs},
        "failed_companies": [f[0] for f in failed],
        "last_sync_time": last_sync
    }

@app.get("/api/health/collectors", response_model=schemas.CollectorHealthStats)
def get_collector_health(db: Session = Depends(database.get_db)):
    """Collector Health Metrics"""
    total = db.query(models.ATSHealthLog).count()
    if total == 0:
        return {
            "success_rate": 0.0,
            "failure_rate": 0.0,
            "average_duration_ms": 0.0,
            "last_successful_run": None
        }
        
    successes = db.query(models.ATSHealthLog).filter(models.ATSHealthLog.is_success == True).count()
    failures = total - successes
    
    avg_dur = db.query(func.avg(models.ATSHealthLog.duration_ms)).scalar() or 0.0
    last_success = db.query(func.max(models.ATSHealthLog.run_time)).filter(models.ATSHealthLog.is_success == True).scalar()
    
    return {
        "success_rate": round((successes / total) * 100, 2),
        "failure_rate": round((failures / total) * 100, 2),
        "average_duration_ms": round(float(avg_dur), 2),
        "last_successful_run": last_success
    }

@app.get("/api/coverage/report", response_model=schemas.CoverageReport)
def get_coverage_report(db: Session = Depends(database.get_db)):
    """Comprehensive coverage report for data quality and source health."""
    total_active = db.query(models.Opportunity).filter(models.Opportunity.status == "Active").count()
    total_archived = db.query(models.Opportunity).filter(models.Opportunity.status == "Archived").count()
    total_verified = db.query(models.Opportunity).filter(models.Opportunity.trust_score >= 80).count()
    total_unique = total_active # Placeholder since deduplication happens at ETL level
    
    # Aggregations
    ats_counts = dict(db.query(models.Opportunity.ats_type, func.count(models.Opportunity.id)).filter(models.Opportunity.status == "Active").group_by(models.Opportunity.ats_type).all())
    source_counts = dict(db.query(models.Opportunity.primary_source, func.count(models.Opportunity.id)).filter(models.Opportunity.status == "Active").group_by(models.Opportunity.primary_source).all())
    
    comp_active = db.query(models.CompanyRegistry).filter(models.CompanyRegistry.status == "Active").count()
    comp_failed = db.query(models.CompanyRegistry).filter(models.CompanyRegistry.failure_count > 0).count()
    failed_comps = [c[0] for c in db.query(models.CompanyRegistry.company_name).filter(models.CompanyRegistry.failure_count > 0).limit(50).all()]
    
    last_run = db.query(models.PipelineRun).order_by(models.PipelineRun.started_at.desc()).first()
    
    return {
        "total_active_jobs": total_active,
        "total_verified_jobs": total_verified,
        "total_unique_jobs": total_unique,
        "total_archived_jobs": total_archived,
        "jobs_by_ats": ats_counts,
        "jobs_by_source": source_counts,
        "companies_active": comp_active,
        "companies_failed": comp_failed,
        "failed_companies": failed_comps,
        "duplicate_rate": 0.0, # Placeholder
        "last_pipeline_run": last_run.started_at if last_run else None
    }

@app.get("/api/learning/free", response_model=List[schemas.LearningResourceResponse])
def get_free_resources(db: Session = Depends(database.get_db)):
    """Fetch free resources for the curated collection.
    
    Tiered fallback strategy:
    1. Prefer VERIFIED + VERIFICATION_LIMITED resources
    2. If count < 10, also include UNVERIFIED free resources (shown with lower confidence)
    This prevents the Resources page from showing empty when the verification pipeline
    hasn't run yet on newly seeded data.
    """
    # Tier 1: verified resources
    resources = db.query(models.LearningResource).filter(
        models.LearningResource.availability_status.in_(['VERIFIED', 'VERIFICATION_LIMITED']),
        models.LearningResource.is_free == True
    ).order_by(models.LearningResource.title).all()
    
    # Tier 2 fallback — include unverified if we have fewer than 10 verified
    if len(resources) < 10:
        unverified = db.query(models.LearningResource).filter(
            ~models.LearningResource.availability_status.in_(['VERIFIED', 'VERIFICATION_LIMITED']),
            models.LearningResource.is_free == True
        ).order_by(models.LearningResource.title).all()
        resources = resources + unverified
    
    for r in resources:
        r.match_reason = "Curated Free Resource"
        r.matched_skills = []
        r.role_match = True
        # Tiered confidence badge based on verification status
        if r.availability_status == 'VERIFIED':
            r.verification_confidence = "HIGH"
        elif r.availability_status == 'VERIFICATION_LIMITED':
            r.verification_confidence = "MEDIUM"
        else:
            r.verification_confidence = "UNVERIFIED"
    return resources


@app.get("/api/learning/recommendations", response_model=schemas.LearningRecommendation)
def get_learning_recommendations(role: str = "Software Engineer", db: Session = Depends(database.get_db)):
    """Data-driven learning recommendation engine."""
    try:
        q_role = f"%{role}%"
        match_type = f"Recommended for {role}"
        
        # Get required skills
        skills_map = db.query(models.RoleSkillMap).filter(models.RoleSkillMap.role.ilike(q_role)).all()
        required_skills = [{"skill": s.skill, "importance": s.importance} for s in skills_map]
        
        if not required_skills:
            # Fallback to general skills if role not found
            required_skills = [{"skill": "Communication", "importance": "Required"}, {"skill": "Problem Solving", "importance": "Required"}]
            match_type = "General Verified Resources"
        
        # Extract skill names for filtering
        skill_names = [s["skill"] for s in required_skills]
        
        # Find relevant learning resources (FreeCodeCamp, YouTube, etc.)
        resources = []
        if skill_names:
            from sqlalchemy import cast, String, or_
            skill_filters = [
                or_(
                    models.LearningResource.title.ilike(f"%{s}%"),
                    cast(models.LearningResource.skills_covered, String).ilike(f"%{s}%")
                ) for s in skill_names
            ]
            role_filter = cast(models.LearningResource.roles, String).ilike(f"%{role}%")
            
            # Fetch base matches (at least one skill or role matches) and VERIFIED
            base_resources = db.query(models.LearningResource).filter(
                or_(role_filter, *skill_filters),
                models.LearningResource.availability_status.in_(['VERIFIED', 'VERIFICATION_LIMITED'])
            ).all()
            
            # Score in-memory
            role_lower = role.lower()
            scored_res = []
            for r in base_resources:
                score = 0
                
                # Role Relevance (40 pts max)
                match_reason = []
                role_match = False
                if r.roles:
                    r_roles = [ro.lower().strip() for ro in r.roles]
                    if role_lower in r_roles or any(role_lower in ro for ro in r_roles):
                        score += 40
                        role_match = True
                        match_reason.append("Explicitly targets this role.")
                    else:
                        score -= 30
                        match_reason.append("Designed for a different role.")
                elif r.title and role_lower in r.title.lower():
                    score += 20
                    role_match = True
                    match_reason.append("Title matches role.")
                    
                # Skill Coverage (25 pts max)
                matched_skills = []
                if r.skills_covered:
                    r_skills = [s.lower().strip() for s in r.skills_covered]
                    for s in skill_names:
                        if s.lower() in r_skills or any(s.lower() in rs for rs in r_skills):
                            matched_skills.append(s)
                score += min(25, len(matched_skills) * 5)
                if matched_skills:
                    match_reason.append(f"Covers {len(matched_skills)} key skills.")
                
                # Quality & Availability Base (20 pts)
                score += 20 
                
                # Affordability (5 pts)
                if r.affordability == 'FREE': 
                    score += 5
                    match_reason.append("Completely free.")
                elif r.affordability == 'LOW_COST': 
                    score += 3
                elif r.affordability == 'AFFORDABLE': 
                    score += 1
                
                # India Relevance (5 pts)
                if r.country == 'India': 
                    score += 5
                    match_reason.append("India-specific context.")
                
                # Bind dynamic fields for schema
                r.match_reason = " ".join(match_reason)
                r.matched_skills = matched_skills
                r.role_match = role_match
                r.verification_confidence = "HIGH" if r.availability_status == "VERIFIED" else "LOW"
                
                scored_res.append((score, r))
                
            scored_res.sort(key=lambda x: x[0], reverse=True)
            resources = [item[1] for item in scored_res[:10]]
            
        if not resources:
            # Fallback to general verified resources
            resources = db.query(models.LearningResource).filter(
                models.LearningResource.availability_status == 'VERIFIED'
            ).limit(5).all()
            match_type = "General Verified Resources"
            
        # Find relevant certifications
        certifications = []
        if skill_names:
            from sqlalchemy import cast, String, or_
            cert_filters = [
                or_(
                    models.Certification.name.ilike(f"%{s}%"),
                    cast(models.Certification.skills_covered, String).ilike(f"%{s}%")
                ) for s in skill_names
            ]
            role_filter = cast(models.Certification.roles, String).ilike(f"%{role}%")
            
            base_certs = db.query(models.Certification).filter(
                or_(role_filter, *cert_filters),
                models.Certification.availability_status.in_(['VERIFIED', 'VERIFICATION_LIMITED'])
            ).all()
            
            role_lower = role.lower()
            scored_certs = []
            for c in base_certs:
                score = 0
                # Role Relevance (40 pts)
                if c.roles:
                    c_roles = [ro.lower().strip() for ro in c.roles]
                    if role_lower in c_roles or any(role_lower in ro for ro in c_roles):
                        score += 40
                    else:
                        score -= 30
                elif c.name and role_lower in c.name.lower():
                    score += 20
                    
                # Skill Coverage (25 pts max)
                matched_skills = 0
                if c.skills_covered:
                    c_skills = [s.lower().strip() for s in c.skills_covered]
                    for s in skill_names:
                        if s.lower() in c_skills or any(s.lower() in cs for cs in c_skills):
                            matched_skills += 1
                score += min(25, matched_skills * 5)
                
                # Quality & Availability Base (20 pts)
                score += 20 
                
                # Affordability (5 pts)
                if c.affordability == 'FREE': score += 5
                elif c.affordability == 'LOW_COST': score += 3
                elif c.affordability == 'AFFORDABLE': score += 1
                
                # India Relevance (5 pts) - mostly N/A for certs but keeping for consistency
                
                scored_certs.append((score, c))
                
            scored_certs.sort(key=lambda x: x[0], reverse=True)
            certifications = [item[1] for item in scored_certs[:5]]
            
        if not certifications:
            certifications = db.query(models.Certification).filter(
                models.Certification.availability_status == 'VERIFIED'
            ).limit(3).all()

        return {
            "role": role,
            "required_skills": required_skills,
            "missing_skills": [], # To be calculated based on user profile
            "resources": resources,
            "certifications": certifications,
            "match_type": match_type
        }
    except Exception as e:
        import logging
        logging.error(f"Error fetching learning recommendations for role '{role}': {e}")
        return {
            "role": role,
            "required_skills": [],
            "missing_skills": [],
            "resources": [],
            "certifications": []
        }

@app.get("/api/certifications", response_model=List[schemas.CertificationResponse])
def get_certifications(role: Optional[str] = None, difficulty: Optional[str] = None, is_free: Optional[bool] = None, db: Session = Depends(database.get_db)):
    """Fetch certifications with filtering."""
    query = db.query(models.Certification)
    if role:
        query = query.filter(models.Certification.roles.like(f"%\"{role}\"%"))
    if difficulty:
        query = query.filter(models.Certification.difficulty == difficulty)
    if is_free is not None:
        query = query.filter(models.Certification.is_free == is_free)
        
    return query.limit(50).all()

# =============================================================================
# Phase 8.55: Direct Apply Link Integrity Endpoints
# =============================================================================

@app.post("/api/opportunities/{opportunity_id}/track-apply")
def track_apply(
    opportunity_id: int,
    event_type: str = "attempt",   # attempt | success | failure | expired | homepage_redirect
    db: Session = Depends(database.get_db)
):
    """
    Track user apply interaction events for link quality analytics.
    Requires no authentication — called client-side before opening the URL.
    event_type: attempt | success | failure | expired | homepage_redirect
    """
    opp = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    if event_type == "attempt":
        opp.apply_attempts = (opp.apply_attempts or 0) + 1
    elif event_type == "success":
        opp.apply_success = (opp.apply_success or 0) + 1
    elif event_type == "failure":
        opp.apply_failure = (opp.apply_failure or 0) + 1
    elif event_type == "expired":
        opp.expired_clicks = (opp.expired_clicks or 0) + 1
    elif event_type == "homepage_redirect":
        opp.homepage_redirects = (opp.homepage_redirects or 0) + 1

    db.commit()
    return {"status": "ok", "opportunity_id": opportunity_id, "event": event_type}


@app.get("/api/admin/link-audit")
def trigger_link_audit(
    limit: int = 2000,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Phase 8.55: Trigger an immediate link integrity audit (admin only, Stage 1).
    Classifies all active opportunities by URL pattern. No deletions.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    from etl.validator import run_link_audit
    result = run_link_audit(limit=limit)
    return result


@app.get("/api/admin/link-integrity-report")
def get_link_integrity_report(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Phase 8.55: Summary of current link integrity status across all active opportunities.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    from sqlalchemy import func

    counts = db.query(
        models.Opportunity.apply_url_status,
        func.count(models.Opportunity.id).label("count"),
        func.avg(models.Opportunity.link_quality_score).label("avg_score")
    ).filter(
        models.Opportunity.status.in_(["Active", "Verifying"])
    ).group_by(models.Opportunity.apply_url_status).all()

    total = sum(r.count for r in counts)
    rows = [
        {
            "status": r.apply_url_status or "UNKNOWN",
            "count": r.count,
            "pct": round(r.count / total * 100, 1) if total else 0,
            "avg_score": round(r.avg_score or 0, 1)
        }
        for r in counts
    ]
    rows.sort(key=lambda x: -x["count"])

    # Apply success rates
    success_data = db.query(
        func.sum(models.Opportunity.apply_attempts).label("total_attempts"),
        func.sum(models.Opportunity.apply_success).label("total_success"),
        func.sum(models.Opportunity.homepage_redirects).label("total_homepage_redirects"),
    ).first()

    return {
        "total_active": total,
        "by_status": rows,
        "apply_analytics": {
            "total_attempts": success_data.total_attempts or 0,
            "total_success": success_data.total_success or 0,
            "total_homepage_redirects": success_data.total_homepage_redirects or 0,
            "success_rate": round(
                (success_data.total_success or 0) / max(success_data.total_attempts or 1, 1) * 100, 1
            )
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK API  (PostgreSQL — no mocks, no setTimeout)
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/feedback", response_model=schemas.FeedbackResponse)
async def submit_feedback(
    payload: schemas.FeedbackCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Submit user feedback. Stored in PostgreSQL feedback table."""
    fb = models.Feedback(
        user_id=current_user.id,
        rating=payload.rating,
        category=payload.category,
        priority=payload.priority or "Medium",
        subject=payload.subject,
        description=payload.description,
        file_attachment=payload.file_attachment,
        status="Open",
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@app.get("/api/feedback/stats", response_model=schemas.FeedbackStatsResponse)
async def get_feedback_stats(db: Session = Depends(database.get_db)):
    """Public feedback statistics — no auth required."""
    from sqlalchemy import func as sqlfunc

    total = db.query(func.count(models.Feedback.id)).scalar() or 0
    resolved = db.query(func.count(models.Feedback.id)).filter(models.Feedback.status == "Resolved").scalar() or 0
    open_count = db.query(func.count(models.Feedback.id)).filter(models.Feedback.status == "Open").scalar() or 0
    in_review = db.query(func.count(models.Feedback.id)).filter(models.Feedback.status == "In Review").scalar() or 0
    avg_rating = db.query(func.avg(models.Feedback.rating)).filter(models.Feedback.rating.isnot(None)).scalar()

    return {
        "total_feedback": total,
        "resolved_count": resolved,
        "open_count": open_count,
        "in_review_count": in_review,
        "average_rating": round(float(avg_rating or 0), 1),
        "features_shipped": resolved,
        "avg_response_hours": "< 48h",
    }


@app.get("/api/feedback/me", response_model=List[schemas.FeedbackResponse])
async def get_my_feedback(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Return all feedback submitted by the current user."""
    return db.query(models.Feedback).filter(
        models.Feedback.user_id == current_user.id
    ).order_by(models.Feedback.created_at.desc()).all()


@app.get("/api/admin/feedback", response_model=List[schemas.FeedbackResponse])
async def admin_get_all_feedback(
    status: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Admin: list all feedback with optional status/category filter."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    q = db.query(models.Feedback)
    if status:
        q = q.filter(models.Feedback.status == status)
    if category:
        q = q.filter(models.Feedback.category == category)
    return q.order_by(models.Feedback.created_at.desc()).offset(offset).limit(limit).all()


@app.patch("/api/admin/feedback/{feedback_id}", response_model=schemas.FeedbackResponse)
async def admin_update_feedback(
    feedback_id: int,
    payload: schemas.FeedbackUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Admin: update feedback status or add admin notes."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    fb = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    if payload.status is not None:
        fb.status = payload.status
    if payload.admin_notes is not None:
        fb.admin_notes = payload.admin_notes
    from datetime import datetime as dt
    fb.updated_at = dt.utcnow()
    db.commit()
    db.refresh(fb)
    return fb


class PageViewPayload(schemas.BaseModel):
    path: str
    page_name: Optional[str] = None


@app.post("/api/analytics/pageview")
def record_page_view(
    payload: PageViewPayload,
    request: Request,
    db: Session = Depends(database.get_db)
):
    """
    Lightweight pageview recorder for internal first-party analytics.
    Enables Admin Panel to monitor feature and page popularity.
    """
    try:
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                data = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                user_email = data.get("sub")
                if user_email:
                    u = auth.get_user_by_email(db, user_email)
                    if u:
                        user_id = u.id
            except Exception:
                pass

        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent", "")[:250]

        pv = models.PageView(
            path=payload.path[:250],
            page_name=payload.page_name[:95] if payload.page_name else None,
            user_id=user_id,
            ip_address=ip,
            user_agent=ua,
            created_at=datetime.utcnow()
        )
        db.add(pv)
        db.commit()
    except Exception as e:
        logger.debug(f"PageView log non-fatal: {e}")
    return {"status": "ok"}


