from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import CompanyRegistry, Opportunity, HiringIntelligenceCompanySnapshot, HiringIntelligenceGlobalSnapshot
from sqlalchemy import func

def run_company_health_engine():
    """
    Phase 8.6: Company Health Engine & Hiring Intelligence
    Updates CompanyRegistry health_score based on fresh jobs, link quality, etc.
    Generates Daily Snapshots.
    """
    db = SessionLocal()
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    try:
        companies = db.query(CompanyRegistry).all()
        
        global_today = 0
        global_week = 0
        global_month = 0
        global_expired = 0
        global_broken = 0
        total_confidence = 0
        total_freshness = 0
        active_count = 0
        
        for comp in companies:
            # Get all jobs for this company
            jobs = db.query(Opportunity).filter(Opportunity.company == comp.company_name).all()
            if not jobs:
                comp.health_score = 50
                continue
                
            active_jobs = [j for j in jobs if j.lifecycle_status in ["NEW", "ACTIVE"]]
            expired_jobs = [j for j in jobs if j.lifecycle_status == "EXPIRED"]
            broken_jobs = [j for j in jobs if j.lifecycle_status == "BROKEN"]
            
            # 1. Health Score Calculation
            base_score = 100
            
            # Penalize for broken links (heavy penalty)
            if jobs:
                broken_ratio = len(broken_jobs) / len(jobs)
                base_score -= (broken_ratio * 40)
                
            # Penalize for expired jobs laying around
            if jobs:
                expired_ratio = len(expired_jobs) / len(jobs)
                base_score -= (expired_ratio * 20)
                
            # Reward for recent activity
            jobs_this_month = [j for j in active_jobs if j.first_seen and j.first_seen >= month_start]
            if jobs_this_month:
                base_score = min(100, base_score + 10)
                
            comp.health_score = int(max(0, min(100, base_score)))
            
            # 2. Hiring Intelligence Snapshot
            jobs_today = [j for j in active_jobs if j.first_seen and j.first_seen >= today_start]
            jobs_this_week = [j for j in active_jobs if j.first_seen and j.first_seen >= week_start]
            
            velocity = "Stable"
            if len(jobs_this_week) > 20: velocity = "High"
            elif len(jobs_this_week) < 2: velocity = "Low"
            
            trend = "Flat"
            if len(jobs_today) > (len(jobs_this_week) / 7.0): trend = "Up"
            elif len(jobs_today) < (len(jobs_this_week) / 7.0) * 0.5: trend = "Down"
            
            comp_snap = db.query(HiringIntelligenceCompanySnapshot).filter(
                HiringIntelligenceCompanySnapshot.company_name == comp.company_name,
                HiringIntelligenceCompanySnapshot.snapshot_date >= today_start
            ).first()
            
            if not comp_snap:
                comp_snap = HiringIntelligenceCompanySnapshot(
                    company_name=comp.company_name,
                    snapshot_date=today_start
                )
                db.add(comp_snap)
                
            comp_snap.jobs_today = len(jobs_today)
            comp_snap.jobs_this_week = len(jobs_this_week)
            comp_snap.hiring_velocity = velocity
            comp_snap.hiring_trend = trend
            comp_snap.company_hiring_score = len(jobs_this_month) * 2 + comp.health_score
            
            # Accumulate globals
            global_today += len(jobs_today)
            global_week += len(jobs_this_week)
            global_month += len(jobs_this_month)
            global_expired += len([j for j in jobs if j.lifecycle_status == "EXPIRED" and j.last_checked and j.last_checked >= today_start])
            global_broken += len([j for j in jobs if j.lifecycle_status == "BROKEN" and j.last_checked and j.last_checked >= today_start])
            
            for j in active_jobs:
                active_count += 1
                total_confidence += j.confidence_score or 0
                if j.last_seen:
                    age_days = (now - j.last_seen).days
                    total_freshness += max(0, 100 - age_days)

        # 3. Global Snapshot
        g_snap = db.query(HiringIntelligenceGlobalSnapshot).filter(
            HiringIntelligenceGlobalSnapshot.snapshot_date >= today_start
        ).first()
        
        if not g_snap:
            g_snap = HiringIntelligenceGlobalSnapshot(snapshot_date=today_start)
            db.add(g_snap)
            
        g_snap.jobs_today = global_today
        g_snap.jobs_this_week = global_week
        g_snap.jobs_this_month = global_month
        g_snap.expired_today = global_expired
        g_snap.broken_today = global_broken
        g_snap.average_confidence = int(total_confidence / active_count) if active_count else 0
        g_snap.average_freshness = int(total_freshness / active_count) if active_count else 0
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Company Health Engine error: {e}")
    finally:
        db.close()
