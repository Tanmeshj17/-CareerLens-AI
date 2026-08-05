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

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()

def jobs_task():
    logger.info("Executing scheduled General ATS Registry Runner...")
    try:
        from collectors.registry_runner import run_all_registry
        run_all_registry()
        logger.info("Scheduled Jobs Pipeline finished.")
    except Exception as e:
        logger.error(f"Scheduled Jobs Pipeline failed: {str(e)}")

def aggregator_task(name: str):
    logger.info(f"Executing scheduled Aggregator Collector: {name}...")
    try:
        from collectors.registry_runner import run_all_registry
        run_all_registry()
        logger.info(f"Scheduled {name} Collector finished.")
    except Exception as e:
        logger.error(f"Scheduled {name} Collector failed: {str(e)}")

def internships_task():
    logger.info("Executing scheduled Internships Pipeline...")
    try:
        logger.info("Scheduled Internships Pipeline finished.")
    except Exception as e:
        logger.error(f"Scheduled Internships Pipeline failed: {str(e)}")

def resources_task():
    logger.info("Executing scheduled Learning Resources Pipeline...")
    try:
        logger.info("Scheduled Resources Pipeline finished.")
    except Exception as e:
        logger.error(f"Scheduled Resources Pipeline failed: {str(e)}")

def insights_task():
    logger.info("Executing scheduled Insights Pipeline...")
    try:
        logger.info("Scheduled Insights Pipeline finished.")
    except Exception as e:
        logger.error(f"Scheduled Insights Pipeline failed: {str(e)}")

def validation_task():
    logger.info("Executing scheduled Expiry and Validation Pipeline...")
    try:
        logger.info("Scheduled Expiry and Validation finished.")
    except Exception as e:
        logger.error(f"Scheduled Expiry and Validation failed: {str(e)}")

def freshness_verification_task():
    """Tiered Link Validation and Archiving Engine."""
    logger.info("Executing Freshness Verification Engine...")
    try:
        from app.database import SessionLocal
        from app.models import Opportunity
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            archive_threshold = now - timedelta(days=30)
            stale_threshold = now - timedelta(days=7)
            
            archived_count = db.query(Opportunity).filter(
                Opportunity.status.in_(["ACTIVE", "STALE", "Active"]),
                Opportunity.posted_date < archive_threshold
            ).update({"status": "ARCHIVED"}, synchronize_session=False)
            
            db.commit()
            logger.info(f"Freshness Engine finished. Archived {archived_count} old opportunities.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Freshness Engine failed: {str(e)}")

def start_scheduler():
    """Starts the background scheduler and registers jobs."""
    if not scheduler.running:
        logger.info("Starting background scheduler...")
        
        interval_hours = int(os.environ.get("REFRESH_INTERVAL_HOURS", 6))
        
        # 1. Jobs pipeline: daily fallback
        scheduler.add_job(
            jobs_task,
            trigger=IntervalTrigger(hours=24),
            id="jobs_pipeline_job",
            replace_existing=True
        )
        
        # 2. Freshness verification: hourly
        scheduler.add_job(
            freshness_verification_task,
            trigger=IntervalTrigger(hours=1),
            id="freshness_verification_job",
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully.")
    else:
        logger.warning("Scheduler is already running.")

def stop_scheduler():
    """Stops the background scheduler."""
    if scheduler.running:
        logger.info("Stopping background scheduler...")
        scheduler.shutdown()
        logger.info("Background scheduler stopped.")
    else:
        logger.warning("Scheduler is not running.")
