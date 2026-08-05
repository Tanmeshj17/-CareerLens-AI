"""
Standalone runner: Immediately collect and seed 9,000+ India jobs into the database.
Usage: python run_collector_now.py
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import models, database
from app.auto_collector import run_auto_collection, generate_large_dataset, _insert_jobs, _expire_old_jobs

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("manual_collector")

# Ensure tables exist
models.Base.metadata.create_all(bind=database.engine)

db = database.SessionLocal()

try:
    before = db.query(models.Opportunity).filter(models.Opportunity.is_active == True).count()
    logger.info(f"=== BEFORE: {before} active jobs ===")

    # Backfill any records without is_active set
    from sqlalchemy import update as sql_update
    res = db.execute(
        sql_update(models.Opportunity)
        .where(
            (models.Opportunity.is_active == None) | (models.Opportunity.lifecycle_status == None)
        )
        .values(
            is_active=True,
            lifecycle_status="ACTIVE",
            apply_url_status="VALID"
        )
    )
    db.commit()
    logger.info(f"Backfilled {res.rowcount} rows without lifecycle status")

    # Expire stale jobs (>45 days)
    stale = _expire_old_jobs(db)
    logger.info(f"Marked {stale} stale jobs")

    # Generate 9k jobs
    TARGET = 9500  # slight overshoot for dedup buffer
    current = db.query(models.Opportunity).filter(models.Opportunity.is_active == True).count()
    needed = max(0, TARGET - current)
    logger.info(f"Current active: {current}, need to insert: {needed}")

    if needed > 0:
        curated = generate_large_dataset(needed + 1000)  # extra buffer
        logger.info(f"Generated {len(curated)} curated job records, inserting with dedup...")
        inserted = _insert_jobs(db, curated)
        logger.info(f"Inserted {inserted} new unique jobs")

    after = db.query(models.Opportunity).filter(models.Opportunity.is_active == True).count()
    interns = db.query(models.Opportunity).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.job_type.ilike("%intern%")
    ).count()
    freshers = db.query(models.Opportunity).filter(
        models.Opportunity.is_active == True,
        models.Opportunity.title.ilike("%fresher%")
    ).count()

    print(f"\n{'='*50}")
    print(f"✅ DONE! Total active jobs: {after}")
    print(f"   Internships:      {interns}")
    print(f"   Fresher roles:    {freshers}")
    print(f"   Entry+Intern%:    {((interns + freshers) * 100 // max(after,1))}%")
    print(f"{'='*50}")

finally:
    db.close()
