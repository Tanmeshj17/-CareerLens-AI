"""
CareerLens AI — Programmatic SEO Router (Phase 3 Controlled Expansion)
Provides dynamic, database-driven metadata, category statistics,
and automated XML sitemaps strictly for high-density, qualified opportunities.
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text
from datetime import datetime

try:
    from app import models, database
    from app.database import get_db
except ImportError:
    from .. import models, database
    from ..database import get_db

router = APIRouter(prefix="/api/seo", tags=["Programmatic SEO"])

# ── Global SEO Minimum Threshold ──────────────────────────────
# Minimum number of active listings required for a category to be indexed / served
SEO_MIN_ACTIVE_LISTINGS = 5

# ── 1. Qualified Roles Configuration ──────────────────────────
ROLE_SLUG_CONFIG: Dict[str, Dict[str, Any]] = {
    "software-engineer": {
        "title_name": "Software Engineer",
        "search_pattern": "%Software Engineer%",
        "h1": "Software Engineer Job Openings & Internships",
        "description": "Explore active Software Engineering job openings and internships. Discover current vacancies, hiring employers, experience requirements, and direct application links across India and Remote.",
        "skills": ["Data Structures", "Algorithms", "Python", "Java", "C++", "System Design", "Git", "REST APIs"],
        "related_roles": [
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "frontend-developer", "label": "Frontend Developer"},
            {"slug": "devops-engineer", "label": "DevOps Engineer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"},
            {"slug": "hyderabad", "label": "Hyderabad"},
            {"slug": "noida", "label": "Noida"}
        ]
    },
    "backend-developer": {
        "title_name": "Backend Developer",
        "search_pattern": "%Backend%",
        "h1": "Backend Developer Job Openings",
        "description": "Find active Backend Engineering roles across top technology employers. Browse current server-side, distributed systems, and API engineering vacancies.",
        "skills": ["Node.js", "Python", "Java", "Go", "PostgreSQL", "MongoDB", "Redis", "Microservices", "Docker"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "devops-engineer", "label": "DevOps Engineer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"},
            {"slug": "hyderabad", "label": "Hyderabad"}
        ]
    },
    "full-stack-developer": {
        "title_name": "Full Stack Developer",
        "search_pattern": "%Full Stack%",
        "h1": "Full Stack Developer Job Openings",
        "description": "Browse active Full Stack Developer positions. Explore current opportunities spanning modern frontend frameworks and scalable backend architectures.",
        "skills": ["React", "TypeScript", "Node.js", "Python", "PostgreSQL", "REST APIs", "AWS", "Docker"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "frontend-developer", "label": "Frontend Developer"},
            {"slug": "backend-developer", "label": "Backend Developer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"}
        ]
    },
    "frontend-developer": {
        "title_name": "Frontend Developer",
        "search_pattern": "%Frontend%",
        "h1": "Frontend Developer Job Openings",
        "description": "Discover current Frontend Engineering vacancies. Compare UI/UX engineering, React, TypeScript, and modern web application opportunities.",
        "skills": ["React", "JavaScript", "TypeScript", "HTML5", "CSS3", "Tailwind CSS", "Next.js", "Redux"],
        "related_roles": [
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "software-engineer", "label": "Software Engineer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "noida", "label": "Noida"}
        ]
    },
    "data-analyst": {
        "title_name": "Data Analyst",
        "search_pattern": "%Data Analyst%",
        "h1": "Data Analyst Jobs & Internships",
        "description": "Find active Data Analytics jobs and internships. Browse current openings requiring SQL, Python, business intelligence tools, and data modeling.",
        "skills": ["SQL", "Python", "Tableau", "Power BI", "Excel", "Data Modeling", "Statistics"],
        "related_roles": [
            {"slug": "machine-learning", "label": "Machine Learning Engineer"},
            {"slug": "software-engineer", "label": "Software Engineer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "noida", "label": "Noida"}
        ]
    },
    "machine-learning": {
        "title_name": "Machine Learning Engineer",
        "search_pattern": "%Machine Learning%",
        "h1": "Machine Learning & AI Job Openings",
        "description": "Browse active Machine Learning, Deep Learning, and AI Engineer openings across tech companies and AI laboratories.",
        "skills": ["Python", "PyTorch", "TensorFlow", "NLP", "Computer Vision", "LLMs", "MLOps", "Docker"],
        "related_roles": [
            {"slug": "data-analyst", "label": "Data Analyst"},
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "hyderabad", "label": "Hyderabad"}
        ]
    },
    "devops-engineer": {
        "title_name": "DevOps Engineer",
        "search_pattern": "%DevOps%",
        "h1": "DevOps & Cloud Infrastructure Jobs",
        "description": "Discover current DevOps, Site Reliability, and Cloud Infrastructure vacancies. Browse roles focused on CI/CD pipelines, Kubernetes, and cloud platforms.",
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "GitHub Actions", "Python"],
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"}
        ]
    }
}

# ── 2. Qualified Locations Configuration ──────────────────────
LOCATION_SLUG_CONFIG: Dict[str, Dict[str, Any]] = {
    "remote-india": {
        "location_name": "Remote (India)",
        "search_pattern": "%Remote%",
        "h1": "Remote Tech Jobs & Internships in India",
        "description": "Discover active remote tech jobs and internships across India. Browse current software engineering, data, and developer roles with work-from-anywhere flexibility.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"},
            {"slug": "frontend-developer", "label": "Frontend Developer"}
        ],
        "related_locations": [
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "pune", "label": "Pune"},
            {"slug": "hyderabad", "label": "Hyderabad"},
            {"slug": "noida", "label": "Noida"}
        ]
    },
    "bengaluru": {
        "location_name": "Bengaluru",
        "search_pattern": "%Bengaluru%",
        "h1": "Tech Jobs & Internships in Bengaluru",
        "description": "Explore current tech jobs and engineering vacancies in Bengaluru. Find software engineering, cloud, and product opportunities across leading technology companies in Bangalore.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "data-analyst", "label": "Data Analyst"},
            {"slug": "machine-learning", "label": "Machine Learning"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "hyderabad", "label": "Hyderabad"},
            {"slug": "pune", "label": "Pune"}
        ]
    },
    "pune": {
        "location_name": "Pune",
        "search_pattern": "%Pune%",
        "h1": "Tech Jobs & Engineering Openings in Pune",
        "description": "Browse active software developer and engineering jobs in Pune, Maharashtra. Find current full-time openings and internships across top technology employers.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "mumbai", "label": "Mumbai"}
        ]
    },
    "hyderabad": {
        "location_name": "Hyderabad",
        "search_pattern": "%Hyderabad%",
        "h1": "Tech Jobs & Engineering Openings in Hyderabad",
        "description": "Discover current technology and software development vacancies in Hyderabad. Explore opportunities across enterprise tech employers and fast-growing startups.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "machine-learning", "label": "Machine Learning"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"}
        ]
    },
    "noida": {
        "location_name": "Noida",
        "search_pattern": "%Noida%",
        "h1": "Tech Jobs & Engineering Openings in Noida (Delhi NCR)",
        "description": "Explore active software engineering, IT, and data analytics job openings in Noida and Delhi NCR. Browse current vacancies with direct application links.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "frontend-developer", "label": "Frontend Developer"},
            {"slug": "data-analyst", "label": "Data Analyst"}
        ],
        "related_locations": [
            {"slug": "remote-india", "label": "Remote India"},
            {"slug": "bengaluru", "label": "Bengaluru"}
        ]
    }
}

# ── 3. Qualified Companies Configuration ──────────────────────
COMPANY_SLUG_CONFIG: Dict[str, Dict[str, Any]] = {
    "databricks": {
        "company_name": "Databricks",
        "search_pattern": "%Databricks%",
        "h1": "Databricks Careers & Job Openings",
        "description": "Explore active career opportunities and engineering vacancies at Databricks. Browse current software engineering, data platform, and infrastructure roles with direct apply links.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "machine-learning", "label": "Machine Learning"}
        ],
        "related_locations": [
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "remote-india", "label": "Remote India"}
        ]
    },
    "paytm": {
        "company_name": "Paytm",
        "search_pattern": "%Paytm%",
        "h1": "Paytm Careers & Job Openings",
        "description": "Find current job vacancies and internships at Paytm. Discover software development, financial technology engineering, and backend roles across India.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"}
        ],
        "related_locations": [
            {"slug": "noida", "label": "Noida"},
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "remote-india", "label": "Remote India"}
        ]
    },
    "okta": {
        "company_name": "Okta",
        "search_pattern": "%Okta%",
        "h1": "Okta Careers & Engineering Job Openings",
        "description": "Explore current engineering vacancies and cloud security roles at Okta. Discover active software engineering, IAM, and infrastructure opportunities.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "devops-engineer", "label": "DevOps Engineer"}
        ],
        "related_locations": [
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "remote-india", "label": "Remote India"}
        ]
    },
    "stripe": {
        "company_name": "Stripe",
        "search_pattern": "%Stripe%",
        "h1": "Stripe Careers & Engineering Job Openings",
        "description": "Browse active engineering openings and developer opportunities at Stripe. Discover current software development, payments infrastructure, and backend roles.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "full-stack-developer", "label": "Full Stack Developer"}
        ],
        "related_locations": [
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "remote-india", "label": "Remote India"}
        ]
    },
    "microsoft": {
        "company_name": "Microsoft",
        "search_pattern": "%Microsoft%",
        "h1": "Microsoft Careers & Job Openings",
        "description": "Discover current engineering openings and career opportunities at Microsoft. Find software engineering, Azure cloud, and research roles.",
        "related_roles": [
            {"slug": "software-engineer", "label": "Software Engineer"},
            {"slug": "backend-developer", "label": "Backend Developer"},
            {"slug": "devops-engineer", "label": "DevOps Engineer"}
        ],
        "related_locations": [
            {"slug": "bengaluru", "label": "Bengaluru"},
            {"slug": "hyderabad", "label": "Hyderabad"},
            {"slug": "noida", "label": "Noida"}
        ]
    }
}


def _build_seo_response(
    category_type: str,
    slug: str,
    title_display: str,
    h1_text: str,
    description_seo: str,
    curated_skills: List[str],
    related_roles: List[Dict[str, str]],
    related_locations: List[Dict[str, str]],
    base_filter: list,
    db: Session
) -> Dict[str, Any]:
    """Helper function to execute database aggregations and build Schema.org response."""
    # 1. Total matching count
    total_count = db.query(func.count(models.Opportunity.id)).filter(*base_filter).scalar() or 0

    # 2. Enforce minimum listing threshold to prevent thin content indexing
    if total_count < SEO_MIN_ACTIVE_LISTINGS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category_type}/{slug}' does not currently meet the minimum active listing threshold ({SEO_MIN_ACTIVE_LISTINGS})."
        )

    # 3. Top Hiring Companies
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

    # 6. Latest Opportunities Sample (Top 20 active listings)
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

    title_seo = f"{title_display} (2026) | CareerLens AI"
    canonical_url = f"https://career-lens-ai-wheat.vercel.app/jobs/{category_type}/{slug}"

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
                    "url": opp["apply_url"] or canonical_url
                }
            }
            for idx, opp in enumerate(recent_opportunities[:10])
        ]
    }

    return {
        "category_type": category_type,
        "slug": slug,
        "role_name": title_display,
        "h1": h1_text,
        "meta_title": title_seo,
        "meta_description": description_seo,
        "canonical_url": canonical_url,
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


# ── Role SEO Endpoint ─────────────────────────────────────────
@router.get("/role/{slug}")
def get_role_seo_data(slug: str, db: Session = Depends(get_db)):
    clean_slug = slug.strip().lower()
    config = ROLE_SLUG_CONFIG.get(clean_slug)
    
    if not config:
        formatted_name = clean_slug.replace("-", " ").title()
        pattern = f"%{formatted_name}%"
        h1 = f"{formatted_name} Job Openings"
        desc = f"Explore active {formatted_name} job openings and internships on CareerLens AI."
        skills = ["Problem Solving", "System Architecture", "Git", "REST APIs"]
        roles = []
        locs = []
    else:
        formatted_name = config["title_name"]
        pattern = config["search_pattern"]
        h1 = config["h1"]
        desc = config["description"]
        skills = config.get("skills", [])
        roles = config.get("related_roles", [])
        locs = config.get("related_locations", [])

    base_filter = [
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        ),
        models.Opportunity.title.ilike(pattern)
    ]

    return _build_seo_response(
        category_type="role",
        slug=clean_slug,
        title_display=formatted_name + " Jobs & Internships",
        h1_text=h1,
        description_seo=desc,
        curated_skills=skills,
        related_roles=roles,
        related_locations=locs,
        base_filter=base_filter,
        db=db
    )


# ── Location SEO Endpoint ─────────────────────────────────────
@router.get("/location/{slug}")
def get_location_seo_data(slug: str, db: Session = Depends(get_db)):
    clean_slug = slug.strip().lower()
    config = LOCATION_SLUG_CONFIG.get(clean_slug)
    
    if not config:
        formatted_name = clean_slug.replace("-", " ").title()
        pattern = f"%{formatted_name}%"
        h1 = f"Tech Jobs & Openings in {formatted_name}"
        desc = f"Explore active technology jobs and internships in {formatted_name} on CareerLens AI."
        roles = []
        locs = []
    else:
        formatted_name = config["location_name"]
        pattern = config["search_pattern"]
        h1 = config["h1"]
        desc = config["description"]
        roles = config.get("related_roles", [])
        locs = config.get("related_locations", [])

    base_filter = [
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        ),
        models.Opportunity.location.ilike(pattern)
    ]

    return _build_seo_response(
        category_type="location",
        slug=clean_slug,
        title_display=f"Tech Jobs in {formatted_name}",
        h1_text=h1,
        description_seo=desc,
        curated_skills=["Software Engineering", "Full Stack", "Backend", "Data Analytics", "Cloud"],
        related_roles=roles,
        related_locations=locs,
        base_filter=base_filter,
        db=db
    )


# ── Company SEO Endpoint ──────────────────────────────────────
@router.get("/company/{slug}")
def get_company_seo_data(slug: str, db: Session = Depends(get_db)):
    clean_slug = slug.strip().lower()
    config = COMPANY_SLUG_CONFIG.get(clean_slug)
    
    if not config:
        formatted_name = clean_slug.replace("-", " ").title()
        pattern = f"%{formatted_name}%"
        h1 = f"{formatted_name} Careers & Job Openings"
        desc = f"Browse current job openings and vacancies at {formatted_name} on CareerLens AI."
        roles = []
        locs = []
    else:
        formatted_name = config["company_name"]
        pattern = config["search_pattern"]
        h1 = config["h1"]
        desc = config["description"]
        roles = config.get("related_roles", [])
        locs = config.get("related_locations", [])

    base_filter = [
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        ),
        models.Opportunity.company.ilike(pattern)
    ]

    return _build_seo_response(
        category_type="company",
        slug=clean_slug,
        title_display=f"{formatted_name} Careers & Jobs",
        h1_text=h1,
        description_seo=desc,
        curated_skills=["Software Engineering", "Distributed Systems", "Cloud", "Agile", "APIs"],
        related_roles=roles,
        related_locations=locs,
        base_filter=base_filter,
        db=db
    )


# ── Dynamic XML Sitemap Endpoint ──────────────────────────────
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

    base_active_filter = [
        models.Opportunity.is_active == True,
        or_(
            models.Opportunity.status == "ACTIVE",
            models.Opportunity.status == "Active",
            models.Opportunity.status.is_(None)
        )
    ]

    # 1. Qualified Roles
    for slug, config in ROLE_SLUG_CONFIG.items():
        count = db.query(func.count(models.Opportunity.id)).filter(
            *base_active_filter,
            models.Opportunity.title.ilike(config["search_pattern"])
        ).scalar() or 0
        if count >= SEO_MIN_ACTIVE_LISTINGS:
            xml_entries.append(f"""  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/jobs/role/{slug}</loc>
    <changefreq>daily</changefreq>
    <priority>0.85</priority>
  </url>""")

    # 2. Qualified Locations
    for slug, config in LOCATION_SLUG_CONFIG.items():
        count = db.query(func.count(models.Opportunity.id)).filter(
            *base_active_filter,
            models.Opportunity.location.ilike(config["search_pattern"])
        ).scalar() or 0
        if count >= SEO_MIN_ACTIVE_LISTINGS:
            xml_entries.append(f"""  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/jobs/location/{slug}</loc>
    <changefreq>daily</changefreq>
    <priority>0.85</priority>
  </url>""")

    # 3. Qualified Companies
    for slug, config in COMPANY_SLUG_CONFIG.items():
        count = db.query(func.count(models.Opportunity.id)).filter(
            *base_active_filter,
            models.Opportunity.company.ilike(config["search_pattern"])
        ).scalar() or 0
        if count >= SEO_MIN_ACTIVE_LISTINGS:
            xml_entries.append(f"""  <url>
    <loc>https://career-lens-ai-wheat.vercel.app/jobs/company/{slug}</loc>
    <changefreq>daily</changefreq>
    <priority>0.85</priority>
  </url>""")

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(xml_entries) + '\n</urlset>'

    return Response(content=xml_content, media_type="application/xml")


# ── Unified Generic Endpoint for Frontend Convenience ─────────
@router.get("/{category_type}/{slug}")
def get_generic_seo_data(category_type: str, slug: str, db: Session = Depends(get_db)):
    cat = category_type.strip().lower()
    if cat == "role":
        return get_role_seo_data(slug, db)
    elif cat == "location":
        return get_location_seo_data(slug, db)
    elif cat == "company":
        return get_company_seo_data(slug, db)
    else:
        raise HTTPException(status_code=404, detail="Invalid SEO category type")
