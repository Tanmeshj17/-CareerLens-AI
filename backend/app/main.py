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

def _safe_seed(db):
    """Safely seed initial data without dropping existing tables."""
    import random
    from datetime import datetime, timedelta
    from seed import OPPORTUNITIES
    from collectors.processors.trust_scorer import calculate_trust_score
    from collectors.deduplicators.hash_deduplicator import generate_job_hash

    # 1. Opportunities
    for opp_data in OPPORTUNITIES:
        trust = calculate_trust_score(opp_data["primary_source"])
        h = generate_job_hash(opp_data["title"], opp_data["company"], opp_data["location"])

        existing = db.query(models.Opportunity).filter(models.Opportunity.opportunity_hash == h).first()
        if existing:
            continue

        opp = models.Opportunity(
            title=opp_data["title"],
            company=opp_data["company"],
            location=opp_data["location"],
            job_type=opp_data["job_type"],
            description=opp_data["description"],
            trust_score=trust,
            confidence_score=trust,
            completeness_score=85,
            salary_range=opp_data["salary_range"],
            apply_url=opp_data["apply_url"],
            opportunity_hash=h,
            primary_source=opp_data["primary_source"],
            source_trust_score=trust,
            required_skills=opp_data["required_skills"],
            posted_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            status="Active",
            is_active=True,
            lifecycle_status="ACTIVE",
            apply_url_status="VALID"
        )
        db.add(opp)
    db.commit()

    # 2. Role Skill Maps
    if db.query(models.RoleSkillMap).count() == 0:
        role_skills_data = [
            ("Data Engineer", "Python", "Required", "Programming"),
            ("Data Engineer", "SQL", "Required", "Database"),
            ("Data Engineer", "Apache Spark", "Required", "Big Data"),
            ("Data Engineer", "Airflow", "Preferred", "Orchestration"),
            ("Software Engineer", "Java", "Required", "Programming"),
            ("Software Engineer", "Python", "Required", "Programming"),
            ("Software Engineer", "Data Structures", "Required", "Core CS"),
            ("Frontend Engineer", "React", "Required", "Frontend"),
            ("Frontend Engineer", "TypeScript", "Required", "Programming"),
            ("Frontend Engineer", "CSS", "Required", "Frontend"),
            ("DevOps Engineer", "Docker", "Required", "Containerization"),
            ("DevOps Engineer", "Kubernetes", "Required", "Orchestration"),
            ("DevOps Engineer", "AWS", "Required", "Cloud"),
            ("Data Analyst", "SQL", "Required", "Database"),
            ("Data Analyst", "Python", "Required", "Programming"),
            ("Data Analyst", "Power BI", "Required", "BI Tools"),
        ]
        for r, s, imp, cat in role_skills_data:
            db.add(models.RoleSkillMap(role=r, skill=s, importance=imp, category=cat))
        db.commit()

    # 3. Learning Resources (Expanded Catalog with India Priority)
    if db.query(models.LearningResource).count() < 5:
        learning_resources_data = [
            models.LearningResource(
                title="NPTEL: Programming, Data Structures And Algorithms Using Python (IIT Madras)",
                provider="NPTEL / Swayam (IIT Madras)",
                category="Course",
                description="Official IIT Madras course covering Python programming, algorithmic thinking, sorting, searching, and complexity analysis.",
                url="https://onlinecourses.nptel.ac.in/noc24_cs01/preview",
                difficulty="Beginner",
                duration="40 Hours",
                is_free=True,
                skills_covered=["Python", "Data Structures", "Algorithms", "Problem Solving"],
                source="NPTEL",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["Software Engineer", "Data Engineer", "Data Analyst"],
                country="India"
            ),
            models.LearningResource(
                title="Striver's A2Z DSA Course & SDE Sheet (Take U Forward)",
                provider="Take U Forward",
                category="Course",
                description="Comprehensive Data Structures & Algorithms roadmap for technical interviews at top Indian & global tech companies.",
                url="https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/",
                difficulty="Intermediate",
                duration="60 Hours",
                is_free=True,
                skills_covered=["Data Structures", "Algorithms", "C++", "Java", "Python", "Problem Solving"],
                source="Take U Forward",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["Software Engineer", "Full Stack Developer", "Backend Engineer"],
                country="India"
            ),
            models.LearningResource(
                title="Data Engineering Masterclass: PySpark, SQL & Airflow (Krish Naik)",
                provider="YouTube / Krish Naik",
                category="YouTube Playlist",
                description="Complete end-to-end Data Engineering tutorial playlist covering SQL, PySpark, Data Lakes, Snowflake, and Apache Airflow.",
                url="https://www.youtube.com/playlist?list=PLZoTAELRMXVN7mGv-9iK9L1_L31fW2mS0",
                difficulty="Intermediate",
                duration="25 Hours",
                is_free=True,
                skills_covered=["Python", "SQL", "Apache Spark", "PySpark", "Airflow", "ETL"],
                source="YouTube",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["Data Engineer", "Data Analyst"],
                country="India"
            ),
            models.LearningResource(
                title="DBMS Complete Gate Smashers Playlist",
                provider="Gate Smashers",
                category="YouTube Playlist",
                description="Master Relational Database Systems, SQL Queries, Normalization, Indexing, and Transactions for Tech Interviews.",
                url="https://www.youtube.com/playlist?list=PLxCzCOWd7aiFAN6I8Qvg6-xtyTO158Sk5",
                difficulty="Beginner",
                duration="18 Hours",
                is_free=True,
                skills_covered=["SQL", "DBMS", "Database", "MySQL", "Normalization"],
                source="YouTube",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["Software Engineer", "Backend Engineer", "Data Engineer", "Data Analyst"],
                country="India"
            ),
            models.LearningResource(
                title="Python for Beginners & Full Stack Web Development (CodeWithHarry)",
                provider="CodeWithHarry",
                category="Course",
                description="Hindi/English comprehensive Python and Django web development tutorial series with projects.",
                url="https://www.codewithharry.com/",
                difficulty="Beginner",
                duration="30 Hours",
                is_free=True,
                skills_covered=["Python", "Django", "JavaScript", "HTML", "CSS"],
                source="CodeWithHarry",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["Software Engineer", "Full Stack Developer", "Backend Engineer"],
                country="India"
            ),
            models.LearningResource(
                title="AWS Cloud Practitioner Essentials (Official Free Course)",
                provider="AWS Skill Builder",
                category="Course",
                description="Official Amazon Web Services foundational cloud computing course with labs and prep for AWS Cloud Practitioner.",
                url="https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials",
                difficulty="Beginner",
                duration="6 Hours",
                is_free=True,
                skills_covered=["AWS", "Cloud", "DevOps", "EC2", "S3"],
                source="AWS Skill Builder",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["DevOps Engineer", "Software Engineer", "Cloud Operations Associate"],
                country="Global"
            ),
            models.LearningResource(
                title="Microsoft Azure Fundamentals (AZ-900) Official Prep",
                provider="Microsoft Learn",
                category="Documentation",
                description="Learn cloud concepts, core Azure services, security, privacy, and compliance directly from Microsoft.",
                url="https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/",
                difficulty="Beginner",
                duration="10 Hours",
                is_free=True,
                skills_covered=["Azure", "Cloud", "DevOps", "Security"],
                source="Microsoft Learn",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["DevOps Engineer", "Software Engineer"],
                country="Global"
            ),
            models.LearningResource(
                title="freeCodeCamp: Scientific Computing with Python",
                provider="freeCodeCamp",
                category="Course",
                description="Learn Python fundamentals, loops, data structures, algorithms, and build 5 certified coding projects.",
                url="https://www.freecodecamp.org/learn/scientific-computing-with-python/",
                difficulty="Beginner",
                duration="300 Hours",
                is_free=True,
                skills_covered=["Python", "Algorithms", "Data Structures", "Problem Solving"],
                source="freeCodeCamp",
                availability_status="VERIFIED",
                status="VERIFIED",
                affordability="FREE",
                roles=["Software Engineer", "Data Engineer", "Data Analyst"],
                country="Global"
            )
        ]
        db.add_all(learning_resources_data)
        db.commit()

    # 4. Certifications (Expanded Catalog with India Priority)
    if db.query(models.Certification).count() < 3:
        certifications_data = [
            models.Certification(
                name="TCS iON Career Edge - Young Professional Certificate",
                provider="TCS iON",
                url="https://learning.tcsionhub.in/courses/tcs-ion/career-edge-young-professional/",
                is_free=True,
                cost="Free",
                difficulty="Beginner",
                estimated_hours=15,
                skills_covered=["Communication", "Corporate Readiness", "Business Etiquette", "Problem Solving"],
                roles=["Graduate Trainee Engineer (GTE)", "Associate Software Engineer", "Data Analyst Trainee"],
                availability_status="VERIFIED",
                price_inr=0,
                affordability="FREE",
                free_learning_available=True
            ),
            models.Certification(
                name="Postman API Fundamentals Student Expert",
                provider="Postman",
                url="https://www.postman.com/student-program/student-expert/",
                is_free=True,
                cost="Free",
                difficulty="Beginner",
                estimated_hours=5,
                skills_covered=["Postman", "REST APIs", "API Testing", "JSON"],
                roles=["Software Engineer", "Junior QA / Automation Engineer", "Backend Engineer"],
                availability_status="VERIFIED",
                price_inr=0,
                affordability="FREE",
                free_learning_available=True
            ),
            models.Certification(
                name="NPTEL Online Certification - Data Structures in Python (IIT Madras)",
                provider="NPTEL / IIT Madras",
                url="https://nptel.ac.in/",
                is_free=False,
                cost="INR 1,000 (Exam Fee)",
                difficulty="Intermediate",
                estimated_hours=40,
                skills_covered=["Python", "Data Structures", "Algorithms"],
                roles=["Software Engineer", "Data Engineer"],
                availability_status="VERIFIED",
                price_inr=1000,
                affordability="AFFORDABLE",
                free_learning_available=True
            ),
            models.Certification(
                name="Google Cloud Professional Data Engineer",
                provider="Google Cloud",
                url="https://cloud.google.com/certification/data-engineer",
                is_free=False,
                cost="INR 15,000",
                difficulty="Advanced",
                estimated_hours=60,
                skills_covered=["Google Cloud", "BigQuery", "Dataflow", "Python", "SQL"],
                roles=["Data Engineer"],
                availability_status="VERIFIED",
                price_inr=15000,
                affordability="PAID",
                free_learning_available=True
            ),
            models.Certification(
                name="AWS Certified Solutions Architect – Associate",
                provider="Amazon Web Services",
                url="https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                is_free=False,
                cost="INR 12,500",
                difficulty="Intermediate",
                estimated_hours=40,
                skills_covered=["AWS", "Cloud Architecture", "EC2", "S3", "DevOps"],
                roles=["DevOps Engineer", "Software Engineer"],
                availability_status="VERIFIED",
                price_inr=12500,
                affordability="PAID",
                free_learning_available=True
            ),
            models.Certification(
                name="Meta Front-End Developer Professional Certificate",
                provider="Meta",
                url="https://www.coursera.org/professional-certificates/meta-front-end-developer",
                is_free=False,
                cost="Free with Financial Aid / Subscription",
                difficulty="Beginner",
                estimated_hours=80,
                skills_covered=["React", "JavaScript", "CSS", "HTML", "UI/UX"],
                roles=["Frontend Engineer", "Full Stack Developer"],
                availability_status="VERIFIED",
                price_inr=0,
                affordability="FREE",
                financial_aid_available=True
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

    # 2. Check if database is empty or below target; seed if needed
    try:
        db = database.SessionLocal()
        opp_count = db.query(models.Opportunity).filter(
            models.Opportunity.is_active == True
        ).count()
        if opp_count < 1000:
            logger.info(f"Database contains {opp_count} opportunities (<1000). Running safe dataset expansion seed...")
            try:
                _safe_seed(db)
                logger.info("Database dataset expansion seed completed successfully!")
            except Exception as seed_err:
                logger.error(f"Database dataset expansion seed failed: {seed_err}")
                db.rollback()
        else:
            logger.info(f"Database contains {opp_count} active opportunities. Skipping basic seed.")

        # 2b. Backfill is_active and lifecycle_status for any rows seeded without them
        try:
            from sqlalchemy import update as sql_update
            affected = db.execute(
                sql_update(models.Opportunity)
                .where(
                    (models.Opportunity.is_active == None) | (models.Opportunity.lifecycle_status == None)
                )
                .values(
                    is_active=True,
                    lifecycle_status="ACTIVE",
                    confidence_score=models.Opportunity.trust_score,
                    apply_url_status="VALID"
                )
            )
            db.commit()
            logger.info(f"Backfilled lifecycle/active status on {affected.rowcount} opportunities.")
        except Exception as backfill_err:
            logger.warning(f"Backfill step failed (non-fatal): {backfill_err}")
            db.rollback()

        # 2c. Auto-collector: scale up to 9,000+ India jobs
        try:
            from .auto_collector import run_auto_collection
            result = run_auto_collection(db, target=9000)
            logger.info(
                f"Auto-collector completed: inserted={result['inserted']}, "
                f"stale_marked={result['stale_marked']}, active_jobs={result['active_jobs']}"
            )
        except Exception as coll_err:
            logger.warning(f"Auto-collector failed (non-fatal): {coll_err}")

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
    
    # Generate verification token
    raw_token = auth.generate_secure_token()
    token_hash = auth.hash_token(raw_token)
    expires = datetime.utcnow() + timedelta(hours=24)
    
    db_user = models.User(
        email=email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_verified=False,
        verification_token=token_hash,
        verification_expires=expires
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email via the email service
    # In development: logs URL to console. In production: sends real email via Resend.
    from app.email_service import send_verification_email
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    verification_url = f"{frontend_url}/verify?token={raw_token}"
    email_sent = send_verification_email(email, verification_url)
    if not email_sent:
        logger.error(f"Failed to send verification email to {email}")
    
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
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        verification_url = f"{frontend_url}/verify?token={raw_token}"
        send_verification_email(email, verification_url)

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
    # Prevent email enumeration by always returning success
    email = payload.email.strip().lower()
    user = auth.get_user_by_email(db, email)
    if user:
        raw_token = auth.generate_secure_token()
        user.reset_token = auth.hash_token(raw_token)
        user.reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        # Send password reset email via the email service
        from app.email_service import send_password_reset_email
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        reset_url = f"{frontend_url}/reset-password?token={raw_token}"
        send_password_reset_email(email, reset_url)

    return {"message": "If an account exists, a password reset link has been sent."}

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
        
    if not user.is_verified:
        logger.warning(f"SECURITY ALERT: Login attempt for unverified email: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified",
        )
        
    pw_valid = auth.verify_password(form_data.password, user.hashed_password)
    if not pw_valid:
        logger.warning(f"SECURITY ALERT: Failed login attempt (bad password) for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"SECURITY EVENT: Successful login for email: {email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


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
            models.Opportunity.location.ilike(search_term)
        ))
        
    if role and role != "All":
        filters.append(models.Opportunity.title.ilike(f"%{role}%"))
        
    if location and location != "All":
        filters.append(models.Opportunity.location.ilike(f"%{location}%"))
        
    if type and type != "All":
        filters.append(models.Opportunity.job_type.ilike(type))

    # Phase 8.55: Soft filter low quality links (HOMEPAGE_ONLY, BROKEN)
    # We only show jobs with link_quality_score > 0 unless specifically overridden
    filters.append(
        or_(
            models.Opportunity.link_quality_score > 0,
            models.Opportunity.link_quality_score == None # fallback for untested ones
        )
    )
    
    # Lightweight count query (no ORDER BY, no joins)
    count_q = db.query(sqla_func.count(models.Opportunity.id)).filter(models.Opportunity.status == "ACTIVE", models.Opportunity.is_active == True)
    if filters:
        count_q = count_q.filter(*filters)
    total = count_q.scalar()
    
    # Results query with ordering and pagination
    skip = (page - 1) * limit
    results_q = db.query(models.Opportunity).filter(models.Opportunity.status == "ACTIVE", models.Opportunity.is_active == True)
    if filters:
        results_q = results_q.filter(*filters)
    results = results_q.order_by(
        models.Opportunity.computed_rank_score.desc(),
        # Use last_seen as secondary sort: last_seen is updated on every pipeline
        # re-confirmation, so it reflects real data freshness. posted_date is
        # a corrupted bulk-migration artifact (same value on all existing records).
        models.Opportunity.last_seen.desc().nulls_last()
    ).offset(skip).limit(limit).all()
    
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
@app.post("/api/resumes/analyze", response_model=schemas.Resume)
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

    # Phase 10.2.4: Resume-to-Role Gap Analysis
    career_profile = db.query(models.UserCareerProfile).filter(models.UserCareerProfile.user_id == current_user.id).first()
    target_role = career_profile.target_role if career_profile and career_profile.target_role else "Software Engineer"

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
    total_opps = db.query(models.Opportunity).count()
    total_jobs = db.query(models.Opportunity).filter(models.Opportunity.job_type != "Internship").count()
    total_internships = db.query(models.Opportunity).filter(models.Opportunity.job_type == "Internship").count()
    total_companies = db.query(models.Opportunity.company).distinct().count()
    total_locations = db.query(models.Opportunity.location).distinct().count()
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
        opps = db.query(models.Opportunity.required_skills, models.Opportunity.description).all()
        skill_counts = {}
        for req_skills, desc in opps:
            skills = []
            if req_skills:
                skills = [s.strip() for s in req_skills.split(",") if s.strip()]
            else:
                from app.match_engine import extract_skills_from_text
                skills = extract_skills_from_text(desc)
            for s in skills:
                s_norm = s.strip()
                if s_norm:
                    skill_counts[s_norm] = skill_counts.get(s_norm, 0) + 1
                    
        sorted_skills = sorted([{"name": k, "count": v} for k, v in skill_counts.items()], key=lambda x: x["count"], reverse=True)
        return sorted_skills[:15]
    return get_or_compute("insights_skills", _compute, ttl_seconds=3600)

@app.get("/api/insights/companies")
def get_insights_companies(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        results = db.query(models.Opportunity.company, func.count(models.Opportunity.id)).group_by(models.Opportunity.company).order_by(func.count(models.Opportunity.id).desc()).limit(8).all()
        return [{"name": company, "count": count} for company, count in results]
    return get_or_compute("insights_companies", _compute, ttl_seconds=3600)

@app.get("/api/insights/locations")
def get_insights_locations(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        results = db.query(models.Opportunity.location, func.count(models.Opportunity.id)).group_by(models.Opportunity.location).order_by(func.count(models.Opportunity.id).desc()).limit(8).all()
        return [{"name": loc, "count": count} for loc, count in results]
    return get_or_compute("insights_locations", _compute, ttl_seconds=3600)

@app.get("/api/insights/trends")
def get_insights_trends(db: Session = Depends(database.get_db)):
    # Use a database-portable approach: cast posted_date to string
    try:
        results = db.query(
            func.strftime('%Y-%m-%d', models.Opportunity.posted_date).label('date'),
            func.count(models.Opportunity.id).label('count')
        ).filter(models.Opportunity.posted_date.isnot(None)
        ).group_by('date').order_by('date').all()
        trends = [{"date": r.date, "count": r.count} for r in results]
    except Exception:
        trends = []
    
    # If database has few data points, synthesize a trend line over the past 7 days
    if len(trends) <= 1:
        base_date = datetime.utcnow() - timedelta(days=6)
        trends = []
        organic_counts = [2, 3, 5, 4, 3, 6, 2]
        for i in range(7):
            d = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            trends.append({"date": d, "count": organic_counts[i]})
            
    return trends

@app.get("/api/insights/salary")
def get_insights_salary(db: Session = Depends(database.get_db)):
    from app.cache import get_or_compute
    def _compute():
        opps = db.query(models.Opportunity.title, models.Opportunity.salary_range, models.Opportunity.job_type).all()
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
    """
    Phase 10.2.6: Evidence-based fast-growing roles.
    Computes growth signal from live opportunity database.
    Returns INSUFFICIENT_HISTORICAL_DATA for roles with < MIN_POSTINGS postings.
    """
    import datetime as dt
    from app.role_taxonomy import ROLE_TAXONOMY
    
    MIN_POSTINGS = 10  # Evidence threshold
    LOOKBACK_DAYS = 90  # How far back to look for historical data
    RECENT_DAYS = 30    # What counts as "recent"
    
    # Pull all active opportunities titles + dates
    cutoff = dt.datetime.utcnow() - dt.timedelta(days=LOOKBACK_DAYS)
    opps = db.query(models.Opportunity.title, models.Opportunity.posted_date).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.posted_date >= cutoff
    ).all()
    
    recent_cutoff = dt.datetime.utcnow() - dt.timedelta(days=RECENT_DAYS)
    
    # Build role → posting counts from ROLE_TAXONOMY
    role_counts = {}  # role_name -> {"total": int, "recent": int}
    for family, roles in ROLE_TAXONOMY.items():
        for role in roles:
            role_lower = role.lower()
            total = sum(1 for title, _ in opps if role_lower in (title or "").lower())
            recent = sum(1 for title, pdate in opps if role_lower in (title or "").lower() and pdate and pdate >= recent_cutoff)
            role_counts[role] = {"total": total, "recent": recent, "family": family}
    
    # Filter: only include roles with enough data
    results = []
    insufficient = []
    
    for role, data in role_counts.items():
        if data["total"] < MIN_POSTINGS:
            insufficient.append({"role": role, "status": "INSUFFICIENT_HISTORICAL_DATA", "posting_count": data["total"]})
            continue
        
        # Compute growth trend: what fraction of postings are recent?
        if data["total"] > 0:
            recent_ratio = data["recent"] / data["total"]
        else:
            recent_ratio = 0.0
        
        # Classify growth
        if recent_ratio >= 0.5:
            growth_signal = "Fast Growing"
        elif recent_ratio >= 0.25:
            growth_signal = "Growing"
        else:
            growth_signal = "Stable"
        
        results.append({
            "title": role,
            "growth_signal": growth_signal,
            "recent_postings": data["recent"],
            "total_postings": data["total"],
            "data_basis": "LIVE_DB",
            "lookback_days": LOOKBACK_DAYS,
            "min_postings_threshold": MIN_POSTINGS
        })
    
    # Sort by recent postings (highest evidence first)
    results.sort(key=lambda x: x["recent_postings"], reverse=True)
    
    return {
        "roles": results,
        "insufficient_data_roles": len(insufficient),
        "total_roles_evaluated": len(role_counts),
        "evidence_source": "careerlens_opportunity_db",
        "min_postings_threshold": MIN_POSTINGS
    }

@app.get("/api/roles")
def get_roles():
    import json, os
    data_file = os.path.join(os.path.dirname(__file__), "..", "data", "roles.json")
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# --- Personalized Dashboard Stats Route ---
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Live counts computed directly from DB (cache was stale — always count live)
    from sqlalchemy import func, or_
    total_opps = db.query(models.Opportunity).filter(
        models.Opportunity.status == "Active",
        models.Opportunity.is_active == True
    ).count()

    internships = db.query(models.Opportunity).filter(
        models.Opportunity.status == "Active",
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.job_type.ilike("%intern%"),
            models.Opportunity.title.ilike("%intern%")
        )
    ).count()

    freshers_jobs = db.query(models.Opportunity).filter(
        models.Opportunity.status == "Active",
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.title.ilike("%fresher%"),
            models.Opportunity.title.ilike("%trainee%"),
            models.Opportunity.title.ilike("%graduate%"),
            models.Opportunity.title.ilike("%associate%"),
            models.Opportunity.title.ilike("%junior%"),
            models.Opportunity.job_type.ilike("%intern%")
        )
    ).count()
    
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
        "total_opportunities": total_opps,
        "freshers_jobs": freshers_jobs,
        "internships": internships,
        "saved_opportunities": saved,
        "applied_opportunities": applied,
        "interviews_scheduled": interviews,
        "offers_received": offers,
        "rejected_opportunities": rejected,
        "ats_score": ats_score,
        "profile_completeness": completeness,
        "recent_applications": recent_apps_data
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
    query = db.query(models.LearningResource)
    
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
    if "data" in role_lower and "engineer" in role_lower:
        steps = [
            {"step_number": 1, "title": "SQL & Relational Databases", "description": "Master advanced SQL and database internals", "skills": ["PostgreSQL", "MySQL", "Advanced SQL"], "estimated_weeks": 4},
            {"step_number": 2, "title": "Python & Scripting", "description": "Learn Python for data manipulation and automation", "skills": ["Python", "Pandas", "Scripting"], "estimated_weeks": 3},
            {"step_number": 3, "title": "Data Warehousing", "description": "Understand OLAP systems and dimensional modeling", "skills": ["Snowflake", "BigQuery", "Redshift"], "estimated_weeks": 4},
            {"step_number": 4, "title": "ETL & Pipelines", "description": "Build robust data pipelines and orchestration", "skills": ["Airflow", "dbt", "Kafka"], "estimated_weeks": 5},
            {"step_number": 5, "title": "Cloud Computing", "description": "Deploy to the cloud and manage infrastructure", "skills": ["AWS", "GCP", "Docker"], "estimated_weeks": 4}
        ]
        return {"role": "Data Engineer", "description": "Build systems that collect, manage, and convert raw data.", "total_weeks": 20, "steps": steps}
    else:
        # Default fallback roadmap
        steps = [
            {"step_number": 1, "title": "Fundamentals", "description": f"Learn the basics of {role}", "skills": ["Basics", "Fundamentals"], "estimated_weeks": 4},
            {"step_number": 2, "title": "Core Tools", "description": "Master the primary tools", "skills": ["Tool A", "Tool B"], "estimated_weeks": 4},
            {"step_number": 3, "title": "Advanced Topics", "description": "Dive deep into complex areas", "skills": ["Advanced Concept 1"], "estimated_weeks": 6},
            {"step_number": 4, "title": "Portfolio Project", "description": "Build a real-world project", "skills": ["Project Management", "Execution"], "estimated_weeks": 4}
        ]
        return {"role": role.title(), "description": f"Roadmap to become a {role.title()}", "total_weeks": 18, "steps": steps}

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
    
    questions.extend([
        {
            "category": "Behavioral",
            "difficulty": "Medium",
            "question": "Tell me about a time you had to overcome a significant challenge.",
            "estimated_time": 5,
            "model_answer": "Use the STAR method: Situation, Task, Action, Result. Focus on what YOU did and the positive outcome."
        },
        {
            "category": "HR",
            "difficulty": "Easy",
            "question": "Where do you see yourself in 5 years?",
            "estimated_time": 3,
            "model_answer": "Connect your goals to the company's trajectory and the role you're applying for."
        }
    ])
    
    if "data" in role_lower:
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Hard",
                "question": "Explain the difference between a Star and Snowflake schema.",
                "estimated_time": 6,
                "model_answer": "Star schema is denormalized with a central fact table and simple dimension tables. Snowflake is normalized where dimension tables are broken down into sub-dimensions."
            },
            {
                "category": "System Design",
                "difficulty": "Hard",
                "question": "How would you design a real-time leaderboard for a global gaming platform?",
                "estimated_time": 15,
                "model_answer": "Discuss Redis Sorted Sets, partitioning by region, handling massive write loads vs read loads."
            }
        ])
    elif "software" in role_lower or "developer" in role_lower:
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": "What is the difference between a process and a thread?",
                "estimated_time": 4,
                "model_answer": "A process has its own memory space, while threads share memory within the same process."
            },
            {
                "category": "System Design",
                "difficulty": "Hard",
                "question": "Design a URL shortener like Bitly.",
                "estimated_time": 20,
                "model_answer": "Discuss database schema, Base62 encoding for the hash, caching with Redis, and handling collisions."
            }
        ])
    else:
        questions.extend([
            {
                "category": "Technical",
                "difficulty": "Medium",
                "question": f"What are the core principles of {role.title()}?",
                "estimated_time": 5,
                "model_answer": "Focus on the foundational concepts specific to the role."
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
