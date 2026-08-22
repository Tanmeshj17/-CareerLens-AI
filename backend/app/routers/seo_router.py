"""
CareerLens AI — Programmatic SEO Router
Provides dynamic, aggregation-driven metadata, category statistics,
and database-generated XML sitemaps strictly for high-density, verified opportunities.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text
from datetime import datetime
import re

try:
    from app import models, database
    from app.database import get_db
except ImportError:
    from .. import models, database
    from ..database import get_db

router = APIRouter(prefix="/api/seo", tags=["Programmatic SEO"])

# ── Global SEO Minimum Threshold ──────────────────────────────
# Configurable minimum number of active listings required for a category to be indexed / served
SEO_MIN_ACTIVE_LISTINGS = 5

# Canonical Supported Slugs & Configurations (Mapped to verified database patterns)
ROLE_SLUG_CONFIG: Dict[str, Dict[str, Any]] = {
    "software-engineer": {
        "title_name": "Software Engineer",
        "search_pattern": "%Software Engineer%",
        "h1": "Software Engineer Jobs & Internships",
        "description": "Explore verified Software Engineering job openings and internships. Discover current vacancies, top hiring companies, experience requirements, and direct application links across India and Remote.",
        "skills": ["Data Structures", "Algorithms", "Python", "Java", "C++", "System Design", "Git", "REST APIs"],
        "related_roles": [
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "frontend-developer", "label": "Frontend Developer"},
            {"slug": "product-manager", "label": "Product Manager"},
            {"slug": "devops-engineer", "label": "DevOps Engineer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "noida", "label": "Noida"},
            {"slug": "pune", "label": "Pune"},
            {"slug": "hyderabad", "label": "Hyderabad"}
        ]
    },
    "backend-developer": {
        "title_name": "Backend Developer",
        "search_pattern": "%Backend%",
        "h1": "Backend Developer Jobs & Openings",
        "description": "Find active Backend Engineering roles across top technology employers. Browse verified server-side, distributed systems, and API engineering vacancies.",
        "skills": ["Node.js", "Python", "Java", "Go", "PostgreSQL", "MongoDB", "Redis", "Microservices", "Docker"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "devops-engineer", "label": "DevOps Engineer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "hyderabad", "label": "Hyderabad"}
        ]
    },
    "full-stack-developer": {
        "title_name": "Full Stack Developer",
        "search_pattern": "%Full Stack%",
        "h1": "Full Stack Developer Jobs & Openings",
        "description": "Browse active Full Stack Developer positions. Explore opportunities spanning modern frontend frameworks and scalable backend architectures.",
        "skills": ["React", "TypeScript", "Node.js", "Python", "PostgreSQL", "REST APIs", "AWS", "Docker"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "frontend-developer", "label": "Frontend Developer"},
            {"slug": "backend-developer", "label": "Backend Developer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"}
        ]
    },
    "frontend-developer": {
        "title_name": "Frontend Developer",
        "search_pattern": "%Frontend%",
        "h1": "Frontend Developer Jobs & Openings",
        "description": "Discover verified Frontend Engineering vacancies. Compare UI/UX engineering, React, TypeScript, and modern web application opportunities.",
        "skills": ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind CSS", "Next.js", "Redux"],
        "related_roles": [
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "software-engineer", "label": "Software Engineer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"}
        ]
    },
    "product-manager": {
        "title_name": "Product Manager",
        "search_pattern": "%Product Manager%",
        "h1": "Product Manager Jobs & Openings",
        "description": "Explore verified Product Management openings. Discover Associate PM, Technical PM, and Senior Product Manager roles at leading tech companies.",
        "skills": ["Product Strategy", "Roadmapping", "Agile", "User Research", "Data Analytics", "SQL", "A/B Testing"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "data-analyst", "label": "Data Analyst"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "mumbai", "label": "Mumbai"}
        ]
    },
    "data-analyst": {
        "title_name": "Data Analyst",
        "search_pattern": "%Data Analyst%",
        "h1": "Data Analyst Jobs & Internships",
        "description": "Find verified Data Analytics jobs and internships. Browse openings requiring SQL, Python, business intelligence tools, and data visualization.",
        "skills": ["SQL", "Python", "Tableau", "Power BI", "Excel", "Data Modeling", "Statistics"],
        "related_roles": [
            {"slug": "data-scientist", "label": "Data Scientist"},
            {"slug": "software-engineer", "label": "Software Engineer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "noida", "label": "Noida"}
        ]
    },
    "data-scientist": {
        "title_name": "Data Scientist",
        "search_pattern": "%Data Scientist%",
        "h1": "Data Scientist Jobs & Openings",
        "description": "Explore verified Data Science and Machine Learning roles. Discover career opportunities in statistical modeling, predictive analytics, and AI.",
        "skills": ["Python", "Machine Learning", "R", "SQL", "TensorFlow", "PyTorch", "Pandas", "Statistics"],
        "related_roles": [
            {"slug": "machine-learning", "label": "Machine Learning Engineer"},
            {"slug": "data-analyst", "label": "Data Analyst"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"}
        ]
    },
    "machine-learning": {
        "title_name": "Machine Learning Engineer",
        "search_pattern": "%Machine Learning%",
        "h1": "Machine Learning Engineer Jobs",
        "description": "Browse active Machine Learning, Deep Learning, and AI Engineer openings across innovative tech companies.",
        "skills": ["Python", "PyTorch", "TensorFlow", "NLP", "Computer Vision", "LLMs", "MLOps", "Docker"],
        "related_roles": [
            {"slug": "data-scientist", "label": "Data Scientist"},
            {"slug": "software-engineer", "label": "Software Engineer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"}
        ]
    },
    "devops-engineer": {
        "title_name": "DevOps Engineer",
        "search_pattern": "%DevOps%",
        "h1": "DevOps & Cloud Infrastructure Jobs",
        "description": "Discover verified DevOps, Site Reliability, and Cloud Infrastructure vacancies. Browse roles focused on CI/CD, Kubernetes, and AWS.",
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "GitHub Actions", "Python"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"}
        ]
    },
    "security-engineer": {
        "title_name": "Security Engineer",
        "search_pattern": "%Security Engineer%",
        "h1": "Security Engineer Jobs & Openings",
        "description": "Explore verified Cybersecurity, Application Security, and Cloud Security Engineer opportunities at top tech organizations.",
        "skills": ["Application Security", "Penetration Testing", "Cloud Security", "Vulnerability Management", "Python", "Network Security"],
        "related_roles": [
            {"slug": "devops-engineer", "label": "DevOps Engineer"},
            {"slug": "software-engineer", "label": "Software Engineer"}
        ],
        "related_locations": [
            {"slug": "remote", "label": "Remote"},
            {"slug": "bengaluru", "label": "Bengaluru"}
        ]
    }
}


@router.get("/role/{slug}")
def get_role_seo_data(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Returns aggregated SEO metadata, live count, top hiring employers,
    location distribution, and initial listings for a role landing page.
    Enforces SEO_MIN_ACTIVE_LISTINGS threshold.
    """
    clean_slug = slug.strip().lower()
    config = ROLE_SLUG_CONFIG.get(clean_slug)
    
    if not config:
        # Check if slug can be dynamically matched
        formatted_name = clean_slug.replace("-", " ").title()
        pattern = f"%{formatted_name}%"
    else:
        formatted_name = config["title_name"]
        pattern = config["search_pattern"]

    # Active filter matching existing main.py standard
    base_filter = [
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        ),
        models.Opportunity.title.ilike(pattern)
    ]

    # 1. Total matching count
    total_count = db.query(func.count(models.Opportunity.id)).filter(*base_filter).scalar() or 0

    # 2. Enforce minimum listing threshold to prevent thin content indexing
    if total_count < SEO_MIN_ACTIVE_LISTINGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' does not currently meet the minimum active listing threshold ({SEO_MIN_ACTIVE_LISTINGS})."
        )

    # 3. Top Hiring Companies for this role
    top_companies_query = db.query(
        models.Opportunity.company,
        func.count(models.Opportunity.id).label("count")
    ).filter(*base_filter)\
     .group_by(models.Opportunity.company)\
     .order_by(func.count(models.Opportunity.id).desc())\
     .limit(8)\
     .all()

    top_companies = [{"name": c[0], "count": c[1]} for c in top_companies_query if c[0]]

    # 4. Location Distribution
    location_query = db.query(
        models.Opportunity.location,
        func.count(models.Opportunity.id).label("count")
    ).filter(*base_filter)\
     .group_by(models.Opportunity.location)\
     .order_by(func.count(models.Opportunity.id).desc())\
     .limit(6)\
     .all()

    locations = [{"name": l[0], "count": l[1]} for l in location_query if l[0]]

    # 5. Job Type Distribution
    job_type_query = db.query(
        models.Opportunity.job_type,
        func.count(models.Opportunity.id).label("count")
    ).filter(*base_filter)\
     .group_by(models.Opportunity.job_type)\
     .order_by(func.count(models.Opportunity.id).desc())\
     .all()

    job_types = [{"name": j[0] or "Full-time", "count": j[1]} for j in job_type_query if j[0]]

    # 6. Latest Opportunities Sample (Top 20 high-quality verified listings)
    opportunities_query = db.query(models.Opportunity)\
        .filter(*base_filter)\
        .order_by(models.Opportunity.posted_date.desc(), models.Opportunity.id.desc())\
        .limit(20)\
        .all()

    recent_opportunities = []
    for opp in opportunities_query:
        recent_opportunities.append({
            "id": opp.id,
            "title": opp.title,
            "company": opp.company,
            "location": opp.location,
            "job_type": opp.job_type or "Full-time",
            "posted_date": opp.posted_date.isoformat() if opp.posted_date else None,
            "trust_score": opp.trust_score,
            "apply_url": opp.verified_apply_url or opp.apply_url,
            "required_skills": opp.required_skills,
            "is_india_job": opp.is_india_job
        })

    # Metadata & Schema
    title_seo = f"{formatted_name} Jobs & Internships (2026) | CareerLens AI"
    description_seo = (
        config["description"] if config else 
        f"Explore {total_count}+ verified {formatted_name} job openings and internships. Discover current vacancies, top hiring companies, and direct apply links on CareerLens AI."
    )
    h1_text = config["h1"] if config else f"{formatted_name} Jobs & Internships"
    curated_skills = config.get("skills", ["Problem Solving", "System Architecture", "Git", "REST APIs"]) if config else []
    related_roles = config.get("related_roles", []) if config else []
    related_locations = config.get("related_locations", []) if config else []

    # Schema.org ItemList JSON-LD
    schema_item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": h1_text,
        "description": description_seo,
        "numberOfItems": len(recent_opportunities),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "item": {
                    "@type": "JobPosting",
                    "title": opp["title"],
                    "hiringOrganization": {
                        "@type": "Organization",
                        "name": opp["company"]
                    },
                    "jobLocation": {
                        "@type": "Place",
                        "address": opp["location"] or "Remote, India"
                    },
                    "datePosted": opp["posted_date"] or datetime.utcnow().isoformat(),
                    "employmentType": "FULL_TIME" if "Full" in str(opp["job_type"]) else "INTERN",
                    "directApply": True if opp["apply_url"] else False,
                    "url": opp["apply_url"] or f"https://career-lens-ai-wheat.vercel.app/jobs/role/{clean_slug}"
                }
            }
            for idx, opp in enumerate(recent_opportunities[:10])
        ]
    }

    return {
        "slug": clean_slug,
        "role_name": formatted_name,
        "h1": h1_text,
        "meta_title": title_seo,
        "meta_description": description_seo,
        "canonical_url": f"https://career-lens-ai-wheat.vercel.app/jobs/role/{clean_slug}",
        "total_active_listings": total_count,
        "last_updated": datetime.utcnow().isoformat(),
        "top_companies": top_companies,
        "top_locations": locations,
        "job_types": job_types,
        "skills": curated_skills,
        "related_roles": related_roles,
        "related_locations": related_locations,
        "opportunities": recent_opportunities,
        "schema_json_ld": schema_item_list
    }


@router.get("/sitemap.xml", response_class=Response)
def get_dynamic_sitemap(db: Session = Depends(get_db)):
    """
    Generates a real-time, dynamic XML sitemap containing only qualified,
    indexable pages meeting the SEO_MIN_ACTIVE_LISTINGS threshold.
    """
    xml_entries = [
        """  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""",
        """  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/app/opportunities</loc>
    <changefreq>hourly</changefreq>
    <priority>0.9</priority>
  </url>""",
        """  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/app/resume</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""",
        """  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/app/learn</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""",
        """  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/app/careers</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""",
        """  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/app/resources</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""
    ]

    # Evaluate each configured role slug dynamically against database threshold
    for slug, config in ROLE_SLUG_CONFIG.items():
        base_filter = [
            models.Opportunity.is_active == True,
            or_(
                models.Opportunity.status == "ACTIVE",
                models.Opportunity.status == "Active",
                models.Opportunity.status.is_(None)
            ),
            models.Opportunity.title.ilike(config["search_pattern"])
        ]
        count = db.query(func.count(models.Opportunity.id)).filter(*base_filter).scalar() or 0
        if count >= SEO_MIN_ACTIVE_LISTINGS:
            xml_entries.append(f"""  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/jobs/role/{slug}</loc>
    <changefreq>daily</changefreq>
    <priority>0.85</priority>
  </url>""")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(xml_entries) + '\n</urlset>'

    return Response(content=xml_content, media_type="application/xml")
