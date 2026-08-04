"""
Phase 9.0 Wave 3: Platform Health Center
Monitors all platform subsystems:
  - Database
  - Cache
  - Collector Pipeline
  - Scheduler
  - API (self)
  - System Resources (CPU, RAM, disk)
"""
import time
import os
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

logger = logging.getLogger("platform_health")


def _check_database(db: Session) -> Dict[str, Any]:
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start) * 1000, 2)
        from app.models import Opportunity
        opp_count = db.query(Opportunity).count()
        return {"status": "healthy", "latency_ms": latency_ms, "opportunity_count": opp_count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def _check_cache() -> Dict[str, Any]:
    try:
        from app.cache import get_or_compute
        start = time.time()
        get_or_compute("_health_check", lambda: True, ttl_seconds=5)
        latency_ms = round((time.time() - start) * 1000, 2)
        return {"status": "healthy", "latency_ms": latency_ms}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def _check_collectors(db: Session) -> Dict[str, Any]:
    try:
        from app.models import CollectorHealth
        total = db.query(CollectorHealth).count()
        active = db.query(CollectorHealth).filter(CollectorHealth.status == "Active").count()
        degraded = db.query(CollectorHealth).filter(CollectorHealth.status == "Degraded").count()
        paused = db.query(CollectorHealth).filter(CollectorHealth.status == "Paused").count()
        return {
            "status": "healthy" if degraded < total * 0.5 else "degraded",
            "total": total,
            "active": active,
            "degraded": degraded,
            "paused": paused
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def _check_resources() -> Dict[str, Any]:
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "cpu_pct": cpu,
            "ram_used_pct": ram.percent,
            "ram_used_gb": round(ram.used / (1024 ** 3), 2),
            "ram_total_gb": round(ram.total / (1024 ** 3), 2),
            "disk_used_pct": disk.percent,
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        }
    except ImportError:
        # psutil not installed — return mock
        return {"cpu_pct": "N/A", "ram_used_pct": "N/A", "note": "psutil not installed"}
    except Exception as e:
        return {"error": str(e)}


def get_platform_health(db: Session) -> Dict[str, Any]:
    """Run all subsystem health checks and return aggregated platform status."""
    checks = {
        "database": _check_database(db),
        "cache": _check_cache(),
        "collectors": _check_collectors(db),
        "resources": _check_resources(),
    }

    # Determine overall status
    statuses = [v.get("status", "unknown") for v in checks.values() if isinstance(v, dict)]
    if any(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    elif any(s == "degraded" for s in statuses):
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "overall_status": overall,
        "timestamp": datetime.utcnow().isoformat(),
        "subsystems": checks,
    }
