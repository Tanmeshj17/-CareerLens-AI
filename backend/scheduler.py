"""
CareerLens AI — Full Background Scheduler
==========================================
Runs automatically:
  1. Every 6 hours  → Auto-collector: fills DB to 9,000+ India jobs, tries real APIs
  2. Every 24 hours → Expire stale jobs (>45 days old)
  3. Every 1 hour   → Freshness verification (archive >30 day old)
  4. Every 12 hours → Real API scrape (Remotive, Arbeitnow — open, no key needed)
  5. Every 7 days   → Re-seed learning resources / certifications if low

To run: python worker.py   (run as separate process or Render Background Worker)
To enable inside API process: set ENABLE_SCHEDULER=true in env vars
"""

import os
import sys
import logging

# Ensure backend root directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("careerlens.scheduler")

scheduler = BackgroundScheduler()


# ─── Task 1: Auto-Collector — expand to 9k+ jobs ─────────────────────────────

def auto_collector_task():
    """Fill DB with 9,000+ India jobs. Runs every 6 hours."""
    logger.info("[Task] auto_collector_task started")
    try:
        from app.database import SessionLocal
        from app.auto_collector import run_auto_collection
        db = SessionLocal()
        try:
            result = run_auto_collection(db, target=9000)
            logger.info(
                f"[Task] auto_collector_task done: "
                f"inserted={result['inserted']}, "
                f"stale_marked={result['stale_marked']}, "
                f"active_jobs={result['active_jobs']}"
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Task] auto_collector_task failed: {e}")


# ─── Task 2: Real API Scrape — Remotive + Arbeitnow ─────────────────────────

def real_api_scrape_task():
    """Fetch live jobs from Remotive.com and Arbeitnow.com (free, no API key). Runs every 12 hours."""
    logger.info("[Task] real_api_scrape_task started")
    try:
        from app.database import SessionLocal
        from app.auto_collector import _fetch_remotive_jobs, _fetch_arbeitnow_jobs, _insert_jobs
        db = SessionLocal()
        try:
            jobs = []
            jobs.extend(_fetch_remotive_jobs(db))
            jobs.extend(_fetch_arbeitnow_jobs())
            if jobs:
                n = _insert_jobs(db, jobs)
                logger.info(f"[Task] real_api_scrape_task: inserted {n} jobs from live APIs")
            else:
                logger.info("[Task] real_api_scrape_task: no new API jobs this cycle")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Task] real_api_scrape_task failed: {e}")


# ─── Task 3: Expire Stale Jobs — jobs older than 45 days ────────────────────

def expire_stale_jobs_task():
    """Mark jobs older than 45 days as STALE. Runs every 24 hours."""
    logger.info("[Task] expire_stale_jobs_task started")
    try:
        from app.database import SessionLocal
        from app.auto_collector import _expire_old_jobs
        db = SessionLocal()
        try:
            stale = _expire_old_jobs(db)
            logger.info(f"[Task] expire_stale_jobs_task: marked {stale} jobs as STALE")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Task] expire_stale_jobs_task failed: {e}")


# ─── Task 4: Freshness Verification — archive very old jobs ─────────────────

def freshness_verification_task():
    """Archive jobs older than 60 days. Runs every hour."""
    logger.info("[Task] freshness_verification_task started")
    try:
        from app.database import SessionLocal
        from app.models import Opportunity
        from datetime import datetime, timedelta

        db = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(days=60)
            archived_count = db.query(Opportunity).filter(
                Opportunity.lifecycle_status.in_(["STALE", "ACTIVE"]),
                Opportunity.posted_date < cutoff,
                Opportunity.is_active == False
            ).update({"lifecycle_status": "ARCHIVED"}, synchronize_session=False)
            db.commit()
            logger.info(f"[Task] freshness_verification_task: archived {archived_count} very old jobs")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Task] freshness_verification_task failed: {e}")


# ─── Task 5: Re-Seed Learning Resources ─────────────────────────────────────

def reseed_learning_task():
    """Re-seed learning resources and certifications if they fall below threshold. Runs every 7 days."""
    logger.info("[Task] reseed_learning_task started")
    try:
        from app.database import SessionLocal
        from app import models
        db = SessionLocal()
        try:
            lr_count = db.query(models.LearningResource).count()
            cert_count = db.query(models.Certification).count()
            if lr_count < 20 or cert_count < 10:
                from app.main import _safe_seed
                _safe_seed(db)
                logger.info("[Task] reseed_learning_task: re-seeded learning resources and certs")
            else:
                logger.info(f"[Task] reseed_learning_task: resources={lr_count}, certs={cert_count}. No reseed needed.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Task] reseed_learning_task failed: {e}")


# ─── Task 6: Dashboard Cache Refresh ────────────────────────────────────────

def refresh_dashboard_cache_task():
    """Update DashboardStatsCache with fresh live counts. Runs every 2 hours."""
    logger.info("[Task] refresh_dashboard_cache_task started")
    try:
        from app.database import SessionLocal
        from app import models
        from sqlalchemy import or_
        from datetime import datetime

        db = SessionLocal()
        try:
            total = db.query(models.Opportunity).filter(
                models.Opportunity.is_active == True
            ).count()
            internships = db.query(models.Opportunity).filter(
                models.Opportunity.is_active == True,
                or_(
                    models.Opportunity.job_type.ilike("%intern%"),
                    models.Opportunity.title.ilike("%intern%")
                )
            ).count()
            freshers = db.query(models.Opportunity).filter(
                models.Opportunity.is_active == True,
                or_(
                    models.Opportunity.title.ilike("%fresher%"),
                    models.Opportunity.title.ilike("%trainee%"),
                    models.Opportunity.title.ilike("%junior%"),
                    models.Opportunity.title.ilike("%associate%"),
                    models.Opportunity.title.ilike("%graduate%"),
                )
            ).count()

            cache = db.query(models.DashboardStatsCache).first()
            if cache:
                cache.total_jobs = total
                cache.internships = internships
                cache.freshers_jobs = freshers
                cache.updated_at = datetime.utcnow()
            else:
                db.add(models.DashboardStatsCache(
                    total_jobs=total,
                    internships=internships,
                    freshers_jobs=freshers,
                    updated_at=datetime.utcnow()
                ))
            db.commit()
            logger.info(f"[Task] refresh_dashboard_cache_task: total={total}, interns={internships}, freshers={freshers}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Task] refresh_dashboard_cache_task failed: {e}")


# ─── Scheduler start/stop ────────────────────────────────────────────────────

def start_scheduler():
    """Starts the background scheduler and registers all jobs."""
    if not scheduler.running:
        logger.info("Starting CareerLens AI scheduler with all job tasks...")

        refresh_hours = int(os.environ.get("REFRESH_INTERVAL_HOURS", "6"))

        # 1. Auto-collector: every 6 hours (configurable via REFRESH_INTERVAL_HOURS)
        scheduler.add_job(
            auto_collector_task,
            trigger=IntervalTrigger(hours=refresh_hours),
            id="auto_collector",
            replace_existing=True,
            max_instances=1,
        )

        # 2. Real API scrape: every 12 hours
        scheduler.add_job(
            real_api_scrape_task,
            trigger=IntervalTrigger(hours=12),
            id="real_api_scrape",
            replace_existing=True,
            max_instances=1,
        )

        # 3. Expire stale jobs: every 24 hours at 3am IST
        scheduler.add_job(
            expire_stale_jobs_task,
            trigger=CronTrigger(hour=21, minute=30, timezone="UTC"),  # 3am IST
            id="expire_stale_jobs",
            replace_existing=True,
            max_instances=1,
        )

        # 4. Freshness verification: every hour
        scheduler.add_job(
            freshness_verification_task,
            trigger=IntervalTrigger(hours=1),
            id="freshness_verification",
            replace_existing=True,
            max_instances=1,
        )

        # 5. Dashboard cache refresh: every 2 hours
        scheduler.add_job(
            refresh_dashboard_cache_task,
            trigger=IntervalTrigger(hours=2),
            id="dashboard_cache_refresh",
            replace_existing=True,
            max_instances=1,
        )

        # 6. Learning resource reseed: every 7 days
        scheduler.add_job(
            reseed_learning_task,
            trigger=IntervalTrigger(days=7),
            id="reseed_learning",
            replace_existing=True,
            max_instances=1,
        )

        scheduler.start()

        logger.info("Scheduler started. Registered jobs:")
        for job in scheduler.get_jobs():
            logger.info(f"  -> {job.id}: next run at {job.next_run_time}")
    else:
        logger.warning("Scheduler is already running.")


def stop_scheduler():
    """Stops the background scheduler."""
    if scheduler.running:
        logger.info("Stopping CareerLens scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
    else:
        logger.warning("Scheduler is not running.")
