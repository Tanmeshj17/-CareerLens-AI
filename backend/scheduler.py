import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from etl.pipeline_jobs import run_jobs_pipeline
from etl.pipeline_internships import run_internships_pipeline
from etl.pipeline_resources import run_resources_pipeline
from etl.pipeline_insights import run_insights_pipeline, refresh_dashboard_cache
from etl.validator import run_expiry_and_validation, run_link_audit

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()

def jobs_task():
    logger.info("Executing scheduled General ATS Pipeline...")
    try:
        # Run standard ATS and Company collectors (excluding aggregators)
        # Assuming we don't pass collector_names, but wait, run_jobs_pipeline() without args runs ALL. 
        # Actually, let's keep it running ALL as a daily fallback, or just standard.
        res = run_jobs_pipeline()
        logger.info(f"Scheduled Jobs Pipeline finished. Status: {res.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled Jobs Pipeline failed: {str(e)}")

def aggregator_task(name: str):
    logger.info(f"Executing scheduled Aggregator Pipeline: {name}...")
    try:
        res = run_jobs_pipeline(pipeline_name=f"{name}_pipeline", collector_names=[name])
        logger.info(f"Scheduled {name} Pipeline finished. Status: {res.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled {name} Pipeline failed: {str(e)}")

def internships_task():
    logger.info("Executing scheduled Internships Pipeline...")
    try:
        res = run_internships_pipeline()
        logger.info(f"Scheduled Internships Pipeline finished. Status: {res.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled Internships Pipeline failed: {str(e)}")

def resources_task():
    logger.info("Executing scheduled Resources Pipeline...")
    try:
        res = run_resources_pipeline()
        logger.info(f"Scheduled Resources Pipeline finished. Status: {res.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled Resources Pipeline failed: {str(e)}")

def insights_task():
    logger.info("Executing scheduled Insights Pipeline...")
    try:
        res = run_insights_pipeline()
        logger.info(f"Scheduled Insights Pipeline finished. Status: {res.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled Insights Pipeline failed: {str(e)}")

def validation_task():
    logger.info("Executing scheduled Expiry and Validation Pipeline...")
    try:
        res = run_expiry_and_validation()
        logger.info(f"Scheduled Expiry and Validation finished. Status: {res.get('status')}")
    except Exception as e:
        logger.error(f"Scheduled Expiry and Validation failed: {str(e)}")

def link_audit_task():
    logger.info("Executing scheduled Link Integrity Audit (Phase 8.55)...")
    try:
        res = run_link_audit(limit=2000)
        logger.info(f"Link Audit finished. Status: {res.get('status')} | Total: {res.get('total_audited')} | By status: {res.get('by_status')}")
    except Exception as e:
        logger.error(f"Link Audit failed: {str(e)}")

def freshness_verification_task():
    """Phase 11.3.8: Tiered Link Validation and Archiving Engine."""
    logger.info("Executing Phase 11.3.8 Freshness Verification Engine...")
    try:
        from app.database import SessionLocal
        from app.link_validator import run_tier_validation
        from app.models import Opportunity
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        try:
            # 1. Archive old jobs (>30 days) and stale jobs (>7 days)
            now = datetime.utcnow()
            archive_threshold = now - timedelta(days=30)
            stale_threshold = now - timedelta(days=7)
            
            # Archive > 30 days
            archived_count = db.query(Opportunity).filter(
                Opportunity.status.in_(["ACTIVE", "STALE"]),
                Opportunity.first_seen < archive_threshold
            ).update({"status": "ARCHIVED", "lifecycle_status": "ARCHIVED"}, synchronize_session=False)
            
            # Stale > 7 days
            stale_count = db.query(Opportunity).filter(
                Opportunity.status == "ACTIVE",
                Opportunity.first_seen >= archive_threshold,
                Opportunity.first_seen < stale_threshold
            ).update({"status": "STALE", "lifecycle_status": "STALE"}, synchronize_session=False)
            
            db.commit()
            logger.info(f"Archived {archived_count} jobs, marked {stale_count} as STALE.")
            
            # 2. Run Tiered Link Validation
            validated_count = run_tier_validation(db)
            logger.info(f"Tiered Link Validation finished. Validated {validated_count} URLs.")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Freshness Engine failed: {str(e)}")

def company_health_task():
    """Phase 8.6: Nightly company health scoring + hiring snapshots."""
    logger.info("Executing Phase 8.6 Company Health Engine...")
    try:
        from app.company_health import run_company_health_engine
        run_company_health_engine()
        logger.info("Company Health Engine finished.")
    except Exception as e:
        logger.error(f"Company Health Engine failed: {str(e)}")

def dashboard_cache_task():
    logger.info("Executing scheduled Dashboard Cache Refresh...")
    try:
        res = refresh_dashboard_cache()
        logger.info(f"Scheduled Dashboard Cache Refresh finished. Success: {res}")
    except Exception as e:
        logger.error(f"Scheduled Dashboard Cache Refresh failed: {str(e)}")

def start_scheduler():
    """Starts the background scheduler and registers jobs."""
    if not scheduler.running:
        logger.info("Starting background scheduler...")
        
        interval_hours = int(os.environ.get("REFRESH_INTERVAL_HOURS", 6))
        
        # 1. Jobs pipeline (ATS + Company Careers): daily fallback
        scheduler.add_job(
            jobs_task,
            trigger=IntervalTrigger(hours=24),
            id="jobs_pipeline_job",
            replace_existing=True
        )
        
        # Aggregator Specific Schedules (Phase 8.3)
        scheduler.add_job(lambda: aggregator_task("Internshala"), trigger=IntervalTrigger(hours=3), id="agg_internshala", replace_existing=True)
        scheduler.add_job(lambda: aggregator_task("Unstop"), trigger=IntervalTrigger(hours=4), id="agg_unstop", replace_existing=True)
        scheduler.add_job(lambda: aggregator_task("FoundIt"), trigger=IntervalTrigger(hours=6), id="agg_foundit", replace_existing=True)
        scheduler.add_job(lambda: aggregator_task("Instahyre"), trigger=IntervalTrigger(hours=10), id="agg_instahyre", replace_existing=True)
        scheduler.add_job(lambda: aggregator_task("Wellfound"), trigger=IntervalTrigger(hours=12), id="agg_wellfound", replace_existing=True)
        
        # 2. Internships pipeline: based on 3 hours
        scheduler.add_job(
            internships_task,
            trigger=IntervalTrigger(hours=3),
            id="internships_pipeline_job",
            replace_existing=True
        )
        
        # 3. Learning resources: weekly (Sunday midnight)
        scheduler.add_job(
            resources_task,
            trigger=CronTrigger(day_of_week="sun", hour=0, minute=0),
            id="resources_pipeline_job",
            replace_existing=True
        )
        
        # 4. Insights regeneration: daily at 2 AM
        scheduler.add_job(
            insights_task,
            trigger=CronTrigger(hour=2, minute=0),
            id="insights_pipeline_job",
            replace_existing=True
        )
        
        # 5. Expiry & validation: daily at 3 AM
        scheduler.add_job(
            validation_task,
            trigger=CronTrigger(hour=3, minute=0),
            id="validation_pipeline_job",
            replace_existing=True
        )
        
        # 6. Dashboard Cache Refresh: Every 15 minutes
        scheduler.add_job(
            dashboard_cache_task,
            trigger=IntervalTrigger(minutes=15),
            id="dashboard_cache_job",
            replace_existing=True
        )

        # 5. Tiered validation and archiving (hourly)
        # We run it hourly, and the tier logic inside checks if X hours have passed for each tier.
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

def update_interval(hours: int):
    """Updates the interval for jobs and internships pipelines."""
    if scheduler.running:
        logger.info(f"Updating scheduler interval to {hours} hours...")
        scheduler.reschedule_job("jobs_pipeline_job", trigger=IntervalTrigger(hours=hours))
        scheduler.reschedule_job("internships_pipeline_job", trigger=IntervalTrigger(hours=hours, start_date=datetime.now() + timedelta(minutes=30)))
        logger.info("Scheduler interval updated.")
    else:
        logger.warning("Cannot update interval: Scheduler is not running.")

# To support timedelta and datetime inside start_scheduler
from datetime import datetime, timedelta
