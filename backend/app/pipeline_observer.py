"""
Phase 11.4 T12: Pipeline Observability
Context manager and metrics recorder for pipeline runs.
Records duration, throughput, error rates, memory usage.
"""
import time
import uuid
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy.orm import Session

logger = logging.getLogger("pipeline_observer")


class PipelineTimer:
    """
    Context manager that wraps a pipeline run and records metrics.

    Usage:
        with PipelineTimer("main_etl", db) as timer:
            timer.record_collector("greenhouse", collected=50, inserted=30)
            timer.record_error("lever", "Timeout after 30s")
    """

    def __init__(self, pipeline_name: str, db: Optional[Session] = None):
        self.pipeline_name = pipeline_name
        self.db = db
        self.run_id = str(uuid.uuid4())[:8]
        self.started_at = datetime.utcnow()
        self._start_time = time.time()
        self._metrics: Dict[str, Any] = {
            "collectors_run": 0,
            "collectors_ok": 0,
            "collectors_failed": 0,
            "collectors_zero_result": 0,
            "collectors_slow": 0,
            "total_collected": 0,
            "total_inserted": 0,
            "total_updated": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "total_broken_links": 0,
        }
        self._collector_durations: list = []
        self._errors: list = []
        self._status = "RUNNING"

    def record_collector(
        self,
        name: str,
        collected: int = 0,
        inserted: int = 0,
        updated: int = 0,
        duplicates: int = 0,
        broken_links: int = 0,
        duration_seconds: float = 0.0,
        failed: bool = False,
        error: Optional[str] = None,
    ):
        """Record metrics for a single collector run."""
        self._metrics["collectors_run"] += 1
        self._metrics["total_collected"] += collected
        self._metrics["total_inserted"] += inserted
        self._metrics["total_updated"] += updated
        self._metrics["total_duplicates"] += duplicates
        self._metrics["total_broken_links"] += broken_links

        if failed:
            self._metrics["collectors_failed"] += 1
            self._metrics["total_errors"] += 1
            if error:
                self._errors.append(f"{name}: {error}")
        else:
            self._metrics["collectors_ok"] += 1

        if collected == 0 and not failed:
            self._metrics["collectors_zero_result"] += 1

        if duration_seconds > 30:
            self._metrics["collectors_slow"] += 1

        self._collector_durations.append(duration_seconds)

    def record_error(self, source: str, message: str):
        """Record a pipeline-level error."""
        self._metrics["total_errors"] += 1
        self._errors.append(f"{source}: {message}")

    def get_metrics(self) -> Dict[str, Any]:
        """Return current accumulated metrics."""
        elapsed = time.time() - self._start_time
        total_inserted = self._metrics["total_inserted"]
        rps = round(total_inserted / elapsed, 2) if elapsed > 0 and total_inserted > 0 else 0.0
        return {
            **self._metrics,
            "duration_seconds": round(elapsed, 2),
            "rows_per_second": rps,
        }

    def __enter__(self):
        logger.info(f"Pipeline '{self.pipeline_name}' started (run_id={self.run_id})")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self._start_time
        completed_at = datetime.utcnow()

        if exc_type is not None:
            self._status = "FAILED"
            self._errors.append(f"PIPELINE ERROR: {exc_val}")
            logger.error(f"Pipeline '{self.pipeline_name}' FAILED after {elapsed:.1f}s: {exc_val}")
        else:
            ok = self._metrics["collectors_ok"]
            total = self._metrics["collectors_run"]
            self._status = "SUCCESS" if ok == total else "PARTIAL" if ok > 0 else "FAILED"

        total_inserted = self._metrics["total_inserted"]
        rps = round(total_inserted / elapsed, 2) if elapsed > 0 and total_inserted > 0 else 0.0

        logger.info(
            f"Pipeline '{self.pipeline_name}' {self._status} | "
            f"{elapsed:.1f}s | "
            f"{self._metrics['collectors_ok']}/{self._metrics['collectors_run']} collectors OK | "
            f"{total_inserted} inserted | {rps} rows/s"
        )

        # Persist to DB if session provided
        if self.db:
            self._save_to_db(completed_at, elapsed, rps)

        return False  # Don't suppress exceptions

    def _save_to_db(self, completed_at: datetime, duration: float, rps: float):
        """Persist the pipeline run metrics to PipelineRunMetrics table."""
        try:
            from app.models import PipelineRunMetrics
            error_summary = " | ".join(self._errors[:5]) if self._errors else None

            # Get memory usage if psutil is available
            peak_memory = None
            try:
                import psutil, os
                proc = psutil.Process(os.getpid())
                peak_memory = round(proc.memory_info().rss / 1024 / 1024, 1)
            except ImportError:
                pass

            record = PipelineRunMetrics(
                pipeline_name=self.pipeline_name,
                run_id=self.run_id,
                started_at=self.started_at,
                completed_at=completed_at,
                duration_seconds=round(duration, 2),
                collectors_run=self._metrics["collectors_run"],
                collectors_ok=self._metrics["collectors_ok"],
                collectors_failed=self._metrics["collectors_failed"],
                collectors_zero_result=self._metrics["collectors_zero_result"],
                collectors_slow=self._metrics["collectors_slow"],
                total_collected=self._metrics["total_collected"],
                total_inserted=self._metrics["total_inserted"],
                total_updated=self._metrics["total_updated"],
                total_duplicates=self._metrics["total_duplicates"],
                total_errors=self._metrics["total_errors"],
                total_broken_links=self._metrics["total_broken_links"],
                rows_per_second=rps,
                peak_memory_mb=peak_memory,
                status=self._status,
                error_summary=error_summary,
            )
            self.db.add(record)
            self.db.commit()
            logger.info(f"Pipeline metrics saved (run_id={self.run_id})")
        except Exception as e:
            logger.error(f"Failed to save pipeline metrics: {e}")
            self.db.rollback()


def get_pipeline_metrics(db: Session, pipeline_name: Optional[str] = None, limit: int = 20) -> list:
    """
    Return recent pipeline run metrics.
    """
    from app.models import PipelineRunMetrics
    q = db.query(PipelineRunMetrics)
    if pipeline_name:
        q = q.filter(PipelineRunMetrics.pipeline_name == pipeline_name)
    runs = q.order_by(PipelineRunMetrics.started_at.desc()).limit(limit).all()

    result = []
    for r in runs:
        result.append({
            "id": r.id,
            "pipeline_name": r.pipeline_name,
            "run_id": r.run_id,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "duration_seconds": r.duration_seconds,
            "status": r.status,
            "collectors_run": r.collectors_run,
            "collectors_ok": r.collectors_ok,
            "collectors_failed": r.collectors_failed,
            "total_inserted": r.total_inserted,
            "total_duplicates": r.total_duplicates,
            "rows_per_second": r.rows_per_second,
            "peak_memory_mb": r.peak_memory_mb,
            "error_summary": r.error_summary,
        })
    return result


def generate_pipeline_observability_report(db: Session) -> str:
    """Generate a markdown pipeline observability report."""
    runs = get_pipeline_metrics(db, limit=10)
    now = datetime.utcnow()

    lines = [
        "# Pipeline Observability Report",
        f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        f"**Last {len(runs)} Pipeline Runs:**",
        "",
        "| Run | Pipeline | Status | Duration | Collectors | Inserted | Rows/s | Memory |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for r in runs:
        status_icon = "✅" if r["status"] == "SUCCESS" else "⚠️" if r["status"] == "PARTIAL" else "❌"
        duration = f"{r['duration_seconds']:.1f}s" if r["duration_seconds"] else "—"
        collectors = f"{r['collectors_ok']}/{r['collectors_run']}"
        memory = f"{r['peak_memory_mb']}MB" if r["peak_memory_mb"] else "—"
        started = r["started_at"][:16] if r["started_at"] else "—"
        lines.append(
            f"| {r['run_id']} | {r['pipeline_name']} | {status_icon} {r['status']} | "
            f"{duration} | {collectors} | {r['total_inserted']:,} | {r['rows_per_second']} | {memory} |"
        )

    if not runs:
        lines.append("| — | No runs recorded yet | — | — | — | — | — | — |")

    return "\n".join(lines)
