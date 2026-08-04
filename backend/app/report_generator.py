"""
Phase 9.0 Wave 4: Automated Dual-Format Report Generator
Generates reports in both Markdown (for GitHub) and JSON (for dashboards/automation).
"""
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.quality_engine import get_database_quality_stats, run_quality_audit
from app.platform_health import get_platform_health

ARTIFACTS_DIR = r"C:\Users\Tanmesh\.gemini\antigravity\brain\e2d8f92c-3118-4011-9680-49aa69e9ec1d\artifacts"


def _save(name: str, md: str, data: dict):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    md_path = os.path.join(ARTIFACTS_DIR, f"{name}.md")
    json_path = os.path.join(ARTIFACTS_DIR, f"{name}.json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, default=str)
    return md_path, json_path


def generate_data_quality_report(db: Session):
    stats = get_database_quality_stats(db)
    quality = run_quality_audit(db)
    now = datetime.utcnow().isoformat()

    md = f"""# Data Quality Report
_Generated: {now}_

## Opportunity Database

| Metric | Value |
|--------|-------|
| Total Opportunities | {stats['total_opportunities']:,} |
| Active | {stats['active_opportunities']:,} |
| Expired | {stats['expired_opportunities']:,} |
| Broken Lifecycle | {stats['broken_lifecycle']:,} |
| Stale | {stats['stale_opportunities']:,} |
| Verified Links | {stats['verified_links']:,} |
| Broken Links | {stats['broken_links']:,} |
| Missing Salary | {stats['missing_salary']:,} |
| Missing Skills | {stats['missing_skills']:,} |
| Missing Experience | {stats['missing_experience']:,} |
| Avg Confidence | {stats['avg_confidence']} |
| Avg Completeness | {stats['avg_completeness']} |
| Fresh (7d) % | {stats['fresh_pct']}% |

## Quality Score Distribution

| Band | Count |
|------|-------|
| 81-100 (Excellent) | {quality['score_distribution']['81-100']:,} |
| 61-80 (Good) | {quality['score_distribution']['61-80']:,} |
| 41-60 (Fair) | {quality['score_distribution']['41-60']:,} |
| 21-40 (Poor) | {quality['score_distribution']['21-40']:,} |
| 0-20 (Critical) | {quality['score_distribution']['0-20']:,} |

**Average Quality Score: {quality['avg_quality_score']}/100**
"""
    data = {"generated_at": now, "db_stats": stats, "quality_audit": quality}
    return _save("Data_Quality_Report", md, data)


def generate_platform_health_report(db: Session):
    health = get_platform_health(db)
    now = datetime.utcnow().isoformat()

    overall = health["overall_status"].upper()
    status_emoji = "✅" if overall == "HEALTHY" else ("⚠️" if overall == "DEGRADED" else "❌")

    subsystems = health.get("subsystems", {})
    db_h = subsystems.get("database", {})
    cache_h = subsystems.get("cache", {})
    coll_h = subsystems.get("collectors", {})
    res_h = subsystems.get("resources", {})

    md = f"""# Platform Health Report
_Generated: {now}_

## Overall Status: {status_emoji} {overall}

## Database
- **Status**: {db_h.get('status', 'N/A')}
- **Latency**: {db_h.get('latency_ms', 'N/A')} ms
- **Opportunity Count**: {db_h.get('opportunity_count', 'N/A'):,}

## Cache
- **Status**: {cache_h.get('status', 'N/A')}
- **Latency**: {cache_h.get('latency_ms', 'N/A')} ms

## Collectors
- **Status**: {coll_h.get('status', 'N/A')}
- **Total**: {coll_h.get('total', 0)} | **Active**: {coll_h.get('active', 0)} | **Degraded**: {coll_h.get('degraded', 0)} | **Paused**: {coll_h.get('paused', 0)}

## System Resources
- **CPU**: {res_h.get('cpu_pct', 'N/A')}%
- **RAM Used**: {res_h.get('ram_used_pct', 'N/A')}% ({res_h.get('ram_used_gb', 'N/A')} GB / {res_h.get('ram_total_gb', 'N/A')} GB)
- **Disk Free**: {res_h.get('disk_free_gb', 'N/A')} GB
"""
    data = {"generated_at": now, **health}
    return _save("Platform_Health_Report_9", md, data)


def generate_search_accuracy_report():
    """Load existing benchmark JSON and produce a Markdown version."""
    benchmark_path = os.path.join(ARTIFACTS_DIR, "Search_Accuracy_Benchmark.json")
    try:
        with open(benchmark_path) as f:
            bench = json.load(f)
    except FileNotFoundError:
        return None, None

    metrics = bench.get("metrics", {})
    now = datetime.utcnow().isoformat()

    md = f"""# Search Accuracy Report
_Generated: {now}_

## Key Metrics

| Metric | Value | Target |
|--------|-------|--------|
| Search Success Score | **{metrics.get('search_success_score', 0):.1f}/100** | ≥ 90 |
| Role Accuracy | {metrics.get('role_accuracy_pct', 0):.1f}% | ≥ 95% |
| Experience Accuracy | {metrics.get('experience_accuracy_pct', 0):.1f}% | ≥ 95% |
| Zero Result Rate | {metrics.get('zero_result_rate_pct', 0):.1f}% | ≤ 5% |
| Avg Response Time | {bench.get('avg_response_time_ms', 0):.1f} ms | ≤ 150 ms |

## Benchmark Run
- **Date**: {bench.get('benchmark_date', 'N/A')}
- **Queries Executed**: {bench.get('total_queries_run', 0)}
- **Results Evaluated**: {bench.get('total_results_evaluated', 0)}
"""
    data = {"generated_at": now, **bench}
    return _save("Search_Accuracy_Report_9", md, data)


def run_all_reports(db: Session):
    """Generate all automated reports."""
    results = {}
    results["data_quality"] = generate_data_quality_report(db)
    results["platform_health"] = generate_platform_health_report(db)
    results["search_accuracy"] = generate_search_accuracy_report()
    return results


if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    r = run_all_reports(db)
    db.close()
    print("Reports generated:")
    for k, v in r.items():
        if v:
            print(f"  [{k}] MD: {v[0]}  |  JSON: {v[1]}")
