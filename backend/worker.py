"""
CareerLens AI — Standalone Scheduler Worker

This script runs the APScheduler jobs independently of the FastAPI API process.
In production, deploy this as a separate Background Worker (e.g., on Render).

Usage:
    python worker.py

Environment variables required:
    DATABASE_URL   — PostgreSQL connection string

The worker does NOT serve HTTP requests. It only runs the ETL jobs.
"""
import sys
import os
import logging
import time

# Ensure the app directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("worker")

from dotenv import load_dotenv
load_dotenv()

def main():
    logger.info("=" * 60)
    logger.info("CareerLens AI Scheduler Worker starting up...")
    logger.info("=" * 60)

    try:
        from scheduler import start_scheduler, scheduler
        start_scheduler()
        logger.info("Scheduler started. Running jobs in background.")
        logger.info("Jobs registered:")
        for job in scheduler.get_jobs():
            logger.info(f"  - {job.id}: next run at {job.next_run_time}")
    except ImportError as e:
        logger.error(f"Failed to import scheduler module: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        sys.exit(1)

    # Block the main thread indefinitely — let APScheduler run in background threads
    try:
        while True:
            time.sleep(60)
            logger.debug("Worker heartbeat — scheduler still running")
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker shutting down...")
        try:
            from scheduler import stop_scheduler
            stop_scheduler()
        except Exception:
            pass
        logger.info("Worker stopped cleanly.")


if __name__ == "__main__":
    main()
