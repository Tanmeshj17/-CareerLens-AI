import json
import os
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import CompanyRegistry
from app.database import SessionLocal

logger = logging.getLogger(__name__)

def load_company_registry(db: Session, force_reload: bool = False):
    """
    Loads company_registry.json into the database.
    Updates existing records or creates new ones.
    """
    registry_path = os.path.join(os.path.dirname(__file__), 'company_registry.json')
    if not os.path.exists(registry_path):
        logger.error(f"Registry not found: {registry_path}")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)

    loaded_count = 0
    updated_count = 0

    for company_name, config in registry_data.items():
        if company_name == "_meta":
            continue

        db_company = db.query(CompanyRegistry).filter(CompanyRegistry.company_name == company_name).first()
        if not db_company:
            db_company = CompanyRegistry(company_name=company_name)
            db.add(db_company)
            loaded_count += 1
        else:
            updated_count += 1

        db_company.ats_type = config.get("ats")
        db_company.ats_identifier = config.get("ats_identifier")
        db_company.source_url = config.get("career_url")
        db_company.industry = config.get("industry")
        db_company.company_size = config.get("company_size")
        db_company.country = config.get("country", "India")
        db_company.city = config.get("city")
        db_company.priority = config.get("priority", "medium")
        db_company.verified = config.get("verified", False)
        db_company.enabled = config.get("enabled", True)
        db_company.collector = config.get("collector")
        db_company.crawl_frequency = config.get("crawl_frequency", "12h")
        db_company.active = config.get("active", True)
        
    db.commit()
    logger.info(f"Registry Loaded: {loaded_count} new, {updated_count} updated.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    try:
        load_company_registry(db)
    finally:
        db.close()
