import logging
import time
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import concurrent.futures

from app.database import SessionLocal
from app.models import CompanyRegistry, RawJob, CollectorHealth
from collectors.collector_intelligence import update_collector_record

from .ats_engine.greenhouse import GreenhouseCollector
from .ats_engine.lever import LeverCollector
from .ats_engine.workday import WorkdayCollector
from .ats_engine.taleo import TaleoCollector
from .ats_engine.smartrecruiters import SmartRecruitersCollector
from .ats_engine.icims import ICIMSCollector
from .ats_engine.jobvite import JobviteCollector
from .ats_engine.eightfold import EightfoldCollector
from .ats_engine.successfactors import SuccessFactorsCollector
from .ats_engine.darwinbox import DarwinboxCollector
from .ats_engine.oracle_recruiting import OracleCollector
from .ats_engine.teamtailor import TeamtailorCollector
from .ats_engine.recruitee import RecruiteeCollector
from .ats_engine.bamboohr import BambooHRCollector
from .ats_engine.rippling import RipplingCollector
from .ats_engine.avature import AvatureCollector

logger = logging.getLogger("registry_runner")

ATS_MAP = {
    "greenhouse": GreenhouseCollector,
    "lever": LeverCollector,
    "workday": WorkdayCollector,
    "taleo": TaleoCollector,
    "smartrecruiters": SmartRecruitersCollector,
    "icims": ICIMSCollector,
    "jobvite": JobviteCollector,
    "eightfold": EightfoldCollector,
    "successfactors": SuccessFactorsCollector,
    "darwinbox": DarwinboxCollector,
    "oracle": OracleCollector,
    "teamtailor": TeamtailorCollector,
    "recruitee": RecruiteeCollector,
    "bamboohr": BambooHRCollector,
    "rippling": RipplingCollector,
    "avature": AvatureCollector
}

class RegistryRunner:
    def __init__(self, db: Session, concurrency: int = 5):
        self.db = db
        self.concurrency = concurrency
        self.priority_queue = []
        self.retry_queue = []
        self.results_pool = []

    def load_queue(self, ats_type: str = None, priority: str = None):
        query = self.db.query(CompanyRegistry).filter(
            CompanyRegistry.enabled == True,
            CompanyRegistry.ats_type != "custom"
        )
        if ats_type:
            query = query.filter(CompanyRegistry.ats_type == ats_type)
        if priority:
            query = query.filter(CompanyRegistry.priority == priority)
            
        companies = query.all()
        # Sort by priority: high, medium, low
        priority_map = {"high": 1, "medium": 2, "low": 3}
        self.priority_queue = sorted(companies, key=lambda c: priority_map.get(c.priority, 99))
        logger.info(f"Loaded {len(self.priority_queue)} companies into priority queue.")

    def run_company(self, company: CompanyRegistry) -> Dict[str, Any]:
        """Runs the collection for a single company."""
        start_time = time.time()
        ats_class = ATS_MAP.get(company.ats_type)
        if not ats_class:
            return {"company": company.company_name, "status": "error", "error": f"Unknown ATS: {company.ats_type}"}

        try:
            # Instantiate collector
            if company.ats_type == "workday":
                # Special init for workday
                tenant = company.ats_identifier or ""
                site = "External"
                if "myworkdayjobs.com/en-US/" in str(company.source_url):
                    site = company.source_url.split("/en-US/")[1].split("/")[0]
                collector = ats_class(company.company_name, tenant, site)
            else:
                collector = ats_class(company.company_name, company.ats_identifier)

            # Fetch
            raw_data = collector.fetch_jobs()
            if not raw_data:
                return {"company": company.company_name, "status": "empty", "jobs": []}

            parsed_jobs = []
            for raw_job in raw_data:
                parsed = collector.parse_job(raw_job)
                normalized = collector.normalize(parsed)
                parsed_jobs.append(normalized)

            duration = time.time() - start_time
            return {
                "company": company.company_name,
                "status": "success",
                "jobs": parsed_jobs,
                "duration": duration,
                "health": collector.health_score
            }
        except Exception as e:
            return {"company": company.company_name, "status": "error", "error": str(e)}

    def execute(self):
        """Executes the priority queue."""
        logger.info(f"Starting collection... (concurrency={self.concurrency})")
        
        if self.concurrency <= 1:
            # Sequential execution for safety (PostgreSQL/SQLAlchemy concurrency fix)
            for company in self.priority_queue:
                try:
                    result = self.run_company(company)
                    self._handle_result(company, result)
                except Exception as exc:
                    logger.error(f"{company.company_name} generated an exception: {exc}")
                    self.retry_queue.append(company)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                future_to_company = {executor.submit(self.run_company, c): c for c in self.priority_queue}
                for future in concurrent.futures.as_completed(future_to_company):
                    company = future_to_company[future]
                    try:
                        result = future.result()
                        self._handle_result(company, result)
                    except Exception as exc:
                        logger.error(f"{company.company_name} generated an exception: {exc}")
                        self.retry_queue.append(company)

        # Basic saving for now (Validation pipeline will process these later)
        self.db.commit()
        self._store_raw_jobs()
        logger.info(f"Registry Run Complete. {len(self.results_pool)} total jobs collected. {len(self.retry_queue)} failures.")

    def _handle_result(self, company, result):
        telemetry = {"status": result["status"], "duration_ms": result.get("duration", 0) * 1000}
        if result["status"] == "success":
            jobs = result["jobs"]
            self.results_pool.extend(jobs)
            telemetry["jobs_count"] = len(jobs)
            telemetry["active_jobs"] = len(jobs)
            logger.info(f"[{company.ats_type}] {company.company_name}: Collected {len(jobs)} jobs")
            company.last_checked = datetime.utcnow()
            company.active_jobs = len(jobs)
            company.total_jobs_ever = (company.total_jobs_ever or 0) + len(jobs)
        elif result["status"] == "error":
            telemetry["error"] = result.get("error", "")
            logger.warning(f"[{company.ats_type}] {company.company_name}: Error - {result['error']}")
            self.retry_queue.append(company)
        else:
            logger.info(f"[{company.ats_type}] {company.company_name}: No jobs found")
            company.last_checked = datetime.utcnow()
            company.active_jobs = 0

        # ── Emit to Collector Intelligence
        collector_name = f"{company.ats_type}_{company.company_name}".lower().replace(" ", "_")
        try:
            update_collector_record(
                self.db,
                collector_name=collector_name,
                ats_type=company.ats_type or "",
                run_result=telemetry,
                company_name=company.company_name,
            )
        except Exception as intel_err:
            logger.warning(f"Collector intelligence update failed for {company.company_name}: {intel_err}")

    def _store_raw_jobs(self):
        if not self.results_pool:
            return
        logger.info(f"Storing {len(self.results_pool)} raw jobs to DB...")
        for job_dict in self.results_pool:
            raw = RawJob(
                title=job_dict.get("title", ""),
                company=job_dict.get("company", ""),
                location=job_dict.get("location", ""),
                job_type=job_dict.get("job_type", ""),
                description=job_dict.get("description", ""),
                apply_url=job_dict.get("apply_url", ""),
                source=job_dict.get("source", ""),
                ats_type=job_dict.get("source", ""),
                source_url=job_dict.get("source_url", ""),
                raw_data=job_dict.get("raw_data", "")
            )
            self.db.add(raw)
        self.db.commit()

def run_all_registry():
    db = SessionLocal()
    try:
        runner = RegistryRunner(db)
        runner.load_queue()
        runner.execute()
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_all_registry()
