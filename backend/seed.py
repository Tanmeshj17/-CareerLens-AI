"""
CareerLens AI — Phase 2 Seeding Script
Drops existing tables, recreates them with updated Phase 2 schema,
and seeds realistic data including required_skills, sources, and hashes.
"""
import os
import sys

# Ensure backend root directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from datetime import datetime, timedelta
import random
import hashlib

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, Opportunity, User, Application, Resume, ResumeProfile, JobMatchScore, OpportunitySource, RawJob
from app.auth import get_password_hash
from collectors.processors.trust_scorer import calculate_trust_score
from collectors.deduplicators.hash_deduplicator import generate_job_hash

OPPORTUNITIES = [
    # ─── Full-time Jobs ───
    {
        "title": "Senior Frontend Engineer (React)",
        "company": "Google",
        "location": "Mountain View, CA (Hybrid)",
        "job_type": "Full-time",
        "description": "Join Google's Core UI team building next-gen search experiences with React, TypeScript, and Web Components. You'll work on products used by 2B+ users daily.",
        "primary_source": "Official",
        "salary_range": "$165k - $245k",
        "apply_url": "https://careers.google.com/jobs/results/?q=frontend%20engineer",
        "required_skills": "React, TypeScript, Web Components, HTML, CSS, JavaScript"
    },
    {
        "title": "Backend Engineer — Payments Platform",
        "company": "Stripe",
        "location": "San Francisco, CA (Remote OK)",
        "job_type": "Full-time",
        "description": "Build and scale Stripe's global payments infrastructure processing $1T+ annually. Python, Go, Ruby stack with distributed systems experience required.",
        "primary_source": "Official",
        "salary_range": "$180k - $260k",
        "apply_url": "https://stripe.com/jobs/search?query=backend+engineer",
        "required_skills": "Python, Go, Ruby, API, Backend, PostgreSQL"
    },
    {
        "title": "Machine Learning Engineer — Feed Ranking",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "job_type": "Full-time",
        "description": "Design and deploy large-scale ML models for content ranking across Facebook and Instagram. PyTorch, distributed training, and recommendation systems expertise.",
        "primary_source": "LinkedIn",
        "salary_range": "$190k - $300k",
        "apply_url": "https://www.metacareers.com/jobs/?q=machine%20learning%20engineer",
        "required_skills": "PyTorch, Machine Learning, Python, Distributed Training, TensorFlow"
    },
    {
        "title": "Full Stack Developer",
        "company": "Shopify",
        "location": "Remote (Global)",
        "job_type": "Full-time",
        "description": "Work on Shopify's merchant dashboard powering 4M+ online stores. React, Ruby on Rails, GraphQL. Strong product sense and empathy for small business owners.",
        "primary_source": "Wellfound",
        "salary_range": "$130k - $190k",
        "apply_url": "https://www.shopify.com/careers/search?q=full+stack",
        "required_skills": "React, Ruby on Rails, Rails, Ruby, GraphQL, TypeScript"
    },
    {
        "title": "DevOps / SRE Engineer",
        "company": "Netflix",
        "location": "Los Gatos, CA",
        "job_type": "Full-time",
        "description": "Keep Netflix streaming for 230M+ subscribers. Kubernetes, AWS, Terraform, Chaos Engineering. Oncall rotation with freedom and responsibility culture.",
        "primary_source": "Official",
        "salary_range": "$200k - $340k",
        "apply_url": "https://jobs.netflix.com/search?q=sre",
        "required_skills": "Kubernetes, AWS, Terraform, DevOps, Docker, Linux"
    },
    {
        "title": "Data Engineer — Analytics Platform",
        "company": "Airbnb",
        "location": "San Francisco, CA (Hybrid)",
        "job_type": "Full-time",
        "description": "Build petabyte-scale data pipelines powering Airbnb's search, pricing, and trust & safety systems. Spark, Kafka, Hive, Presto stack.",
        "primary_source": "LinkedIn",
        "salary_range": "$170k - $250k",
        "apply_url": "https://careers.airbnb.com/positions/?query=data+engineer",
        "required_skills": "Spark, Kafka, Hadoop, Hive, Python, Data Engineering"
    },
    {
        "title": "iOS Engineer — Swift/SwiftUI",
        "company": "Apple",
        "location": "Cupertino, CA",
        "job_type": "Full-time",
        "description": "Build flagship iOS features used by 1B+ devices. Deep knowledge of Swift, UIKit/SwiftUI, Core Data, and performance optimization required.",
        "primary_source": "Official",
        "salary_range": "$175k - $280k",
        "apply_url": "https://jobs.apple.com/en-us/search?search=ios+engineer",
        "required_skills": "Swift, SwiftUI, iOS, Core Data, UIKit"
    },
    {
        "title": "Cloud Solutions Architect",
        "company": "Amazon Web Services",
        "location": "Seattle, WA (Hybrid)",
        "job_type": "Full-time",
        "description": "Help Fortune 500 companies migrate and optimize on AWS. Requires AWS certifications, strong communication skills, and hands-on cloud architecture experience.",
        "primary_source": "Official",
        "salary_range": "$155k - $230k",
        "apply_url": "https://www.amazon.jobs/en/search?base_query=solutions+architect",
        "required_skills": "AWS, Cloud, Python, Cloud Architecture, Terraform"
    },
    {
        "title": "Product Manager — AI/ML",
        "company": "Microsoft",
        "location": "Redmond, WA (Hybrid)",
        "job_type": "Full-time",
        "description": "Drive the product strategy for Copilot AI features across Microsoft 365. Requires 5+ years PM experience and strong understanding of LLMs and AI UX patterns.",
        "primary_source": "Official",
        "salary_range": "$160k - $240k",
        "apply_url": "https://careers.microsoft.com/us/en/search-results?keywords=product%20manager%20ai",
        "required_skills": "Product Management, Agile, Scrum, Product Strategy, JIRA"
    },
    {
        "title": "Cybersecurity Analyst",
        "company": "CrowdStrike",
        "location": "Austin, TX (Remote OK)",
        "job_type": "Full-time",
        "description": "Protect enterprises from advanced cyber threats. Incident response, threat hunting, SIEM/SOAR tools, and malware analysis. Security clearance preferred.",
        "primary_source": "Indeed",
        "salary_range": "$120k - $175k",
        "apply_url": "https://www.crowdstrike.com/careers/job-listing/",
        "required_skills": "Cybersecurity, SIEM, SOAR, Python, Linux"
    },
    {
        "title": "Blockchain Developer — Solidity",
        "company": "Coinbase",
        "location": "Remote (US)",
        "job_type": "Full-time",
        "description": "Build decentralized applications and smart contracts for Coinbase's DeFi products. Solidity, Ethereum, Layer 2 solutions, and security auditing experience.",
        "primary_source": "Wellfound",
        "salary_range": "$150k - $220k",
        "apply_url": "https://www.coinbase.com/careers/positions?query=blockchain",
        "required_skills": "Solidity, Ethereum, Smart Contracts, Blockchain, Go"
    },
    {
        "title": "UX Designer — Enterprise Products",
        "company": "Figma",
        "location": "San Francisco, CA (Hybrid)",
        "job_type": "Full-time",
        "description": "Design the tools that designers use. Work on Figma's enterprise collaboration features, design systems, and accessibility improvements.",
        "primary_source": "LinkedIn",
        "salary_range": "$140k - $200k",
        "apply_url": "https://www.figma.com/careers/#job-openings",
        "required_skills": "UI/UX, Figma, Product Design, Design Systems"
    },

    # ─── Internships ───
    {
        "title": "Software Engineering Intern — Summer 2025",
        "company": "Google",
        "location": "Mountain View, CA",
        "job_type": "Internship",
        "description": "12-week summer internship working on real Google products. Open to current CS/ECE students. Competitive stipend, housing, and mentorship provided.",
        "primary_source": "Official",
        "salary_range": "$10,500/month",
        "apply_url": "https://careers.google.com/jobs/results/?q=intern&employment_type=INTERN",
        "required_skills": "C++, Java, Python, JavaScript, Algorithms, Data Structures"
    },
    {
        "title": "Data Science Intern",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "job_type": "Internship",
        "description": "Work alongside Meta's data science team on experimentation, causal inference, and ML models for social impact. PhD or advanced degree students preferred.",
        "primary_source": "Official",
        "salary_range": "$9,800/month",
        "apply_url": "https://www.metacareers.com/jobs/?q=data%20science%20intern",
        "required_skills": "Data Science, Python, SQL, R, Machine Learning, Pandas"
    },
    {
        "title": "Cloud Engineering Intern",
        "company": "Amazon Web Services",
        "location": "Seattle, WA",
        "job_type": "Internship",
        "description": "Hands-on internship building and testing AWS cloud services. Exposure to EC2, Lambda, DynamoDB. Great for students passionate about distributed systems.",
        "primary_source": "Official",
        "salary_range": "$8,500/month",
        "apply_url": "https://www.amazon.jobs/en/search?base_query=intern+cloud",
        "required_skills": "AWS, Python, Cloud, Linux, Docker"
    },
    {
        "title": "Product Design Intern",
        "company": "Spotify",
        "location": "Stockholm, Sweden / NYC (Hybrid)",
        "job_type": "Internship",
        "description": "Design user experiences for 600M+ Spotify listeners. Portfolio review required. Figma, prototyping, and user research skills are a plus.",
        "primary_source": "LinkedIn",
        "salary_range": "$7,500/month",
        "apply_url": "https://www.lifeatspotify.com/jobs?query=intern+design",
        "required_skills": "UI/UX, Figma, Prototyping, Product Design, Communication"
    },
    {
        "title": "Machine Learning Research Intern",
        "company": "NVIDIA",
        "location": "Santa Clara, CA",
        "job_type": "Internship",
        "description": "Research and implement cutting-edge ML algorithms for GPU-accelerated computing. PyTorch, CUDA, and publications in top venues preferred.",
        "primary_source": "Official",
        "salary_range": "$11,000/month",
        "apply_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=intern+machine+learning",
        "required_skills": "PyTorch, CUDA, Python, Machine Learning, TensorFlow"
    },
    {
        "title": "Cybersecurity Intern",
        "company": "Palo Alto Networks",
        "location": "Santa Clara, CA (Hybrid)",
        "job_type": "Internship",
        "description": "Join the security operations team to help build next-gen firewall and SASE solutions. Great for students pursuing cybersecurity certifications.",
        "primary_source": "Indeed",
        "salary_range": "$7,000/month",
        "apply_url": "https://jobs.paloaltonetworks.com/en/search-jobs?q=intern",
        "required_skills": "Cybersecurity, Networking, Linux, Firewalls"
    },
    {
        "title": "Backend Engineering Intern — Python",
        "company": "Stripe",
        "location": "Remote (US)",
        "job_type": "Internship",
        "description": "Build APIs and services that power internet commerce. Work with Python, Go, and distributed databases. 12-week program with return offer potential.",
        "primary_source": "Official",
        "salary_range": "$9,000/month",
        "apply_url": "https://stripe.com/jobs/search?query=intern",
        "required_skills": "Python, Go, SQL, Backend, Git"
    },

    # ─── Part-time / Contract ───
    {
        "title": "Freelance Technical Writer",
        "company": "Vercel",
        "location": "Remote (Global)",
        "job_type": "Part-time",
        "description": "Write technical documentation, tutorials, and guides for Next.js and Vercel's developer platform. Strong writing skills and React/Node.js knowledge required.",
        "primary_source": "LinkedIn",
        "salary_range": "$60 - $90/hour",
        "apply_url": "https://vercel.com/careers",
        "required_skills": "React, Next.js, HTML, CSS, TypeScript, JavaScript"
    },
    {
        "title": "Contract Data Analyst",
        "company": "Uber",
        "location": "Chicago, IL (Remote OK)",
        "job_type": "Contract",
        "description": "6-month contract analyzing rider and driver data to improve marketplace efficiency. SQL, Python (Pandas), and Tableau/Looker experience required.",
        "primary_source": "Indeed",
        "salary_range": "$75 - $110/hour",
        "apply_url": "https://www.uber.com/us/en/careers/list/?query=data+analyst",
        "required_skills": "SQL, Python, Pandas, Tableau, Data Analysis"
    },

    # ─── India-focused roles ───
    {
        "title": "SDE-2 — Backend (Java/Spring Boot)",
        "company": "Flipkart",
        "location": "Bangalore, India",
        "job_type": "Full-time",
        "description": "Build microservices for India's largest e-commerce platform. Java, Spring Boot, Kafka, Redis. 3-5 years experience required.",
        "primary_source": "Naukri",
        "salary_range": "INR 25L - 45L",
        "apply_url": "https://www.flipkartcareers.com/#!/joblist",
        "required_skills": "Java, Spring Boot, Kafka, Redis, Backend, PostgreSQL"
    },
    {
        "title": "Data Engineer — Fresher",
        "company": "Tata Consultancy Services",
        "location": "Mumbai / Pune, India",
        "job_type": "Full-time",
        "description": "Join TCS Digital as a Data Engineer working on ETL pipelines, Azure Data Factory, and SQL Server. Open to 2024-2025 graduates.",
        "primary_source": "Naukri",
        "salary_range": "INR 7L - 12L",
        "apply_url": "https://ibegin.tcs.com/iBegin/jobs/search",
        "required_skills": "Data Engineering, SQL, Azure, Python, ETL"
    },
    {
        "title": "Software Development Intern",
        "company": "Razorpay",
        "location": "Bangalore, India",
        "job_type": "Internship",
        "description": "6-month internship building fintech APIs processing millions of transactions. Go, Python, PostgreSQL. Pre-final year students preferred.",
        "primary_source": "Cutshort",
        "salary_range": "INR 40k - 60k/month",
        "apply_url": "https://razorpay.com/careers/",
        "required_skills": "Go, Python, PostgreSQL, REST API, Git"
    },
    {
        "title": "AI/ML Intern",
        "company": "Infosys",
        "location": "Hyderabad / Mysore, India",
        "job_type": "Internship",
        "description": "Work on AI projects in NLP, computer vision, and recommendation systems. Python, TensorFlow/PyTorch. Final year students with ML coursework preferred.",
        "primary_source": "Naukri",
        "salary_range": "INR 25k - 40k/month",
        "apply_url": "https://www.infosys.com/careers/apply.html",
        "required_skills": "Python, Machine Learning, TensorFlow, PyTorch, NLTK"
    },
]

def seed_db():
    print("Dropping existing tables to refresh database schema...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    # ── 1. Test Users ──
    users_data = [
        {"email": "test@example.com", "full_name": "Test User", "password": "password123", "role": "user"},
        {"email": "admin@careerlens.ai", "full_name": "Admin User", "password": "admin123", "role": "admin"},
        {"email": "tanmesh@example.com", "full_name": "Tanmesh", "password": "tanmesh123", "role": "user"},
    ]

    created_users = []
    for u in users_data:
        user = User(
            email=u["email"],
            full_name=u["full_name"],
            hashed_password=get_password_hash(u["password"]),
            role=u["role"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        print(f"  ✅ User created: {u['email']} / {u['password']}")

    # ── 2. Opportunities with deduplication and sources ──
    print("Seeding opportunities...")
    for opp_data in OPPORTUNITIES:
        # Calculate fields
        trust = calculate_trust_score(opp_data["primary_source"])
        h = generate_job_hash(opp_data["title"], opp_data["company"], opp_data["location"])
        
        opp = Opportunity(
            title=opp_data["title"],
            company=opp_data["company"],
            location=opp_data["location"],
            job_type=opp_data["job_type"],
            description=opp_data["description"],
            trust_score=trust,
            salary_range=opp_data["salary_range"],
            apply_url=opp_data["apply_url"],
            opportunity_hash=h,
            primary_source=opp_data["primary_source"],
            source_trust_score=trust,
            required_skills=opp_data["required_skills"],
            posted_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            status="Active"
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)

        # Seed sources (for deduplication display)
        # Synthesize multiple sources for some opportunities to showcase deduplication
        sources = [opp_data["primary_source"]]
        if random.random() > 0.6:
            alternate_sources = ["Indeed" if opp_data["primary_source"] != "Indeed" else "LinkedIn", "Cutshort" if opp_data["primary_source"] != "Cutshort" else "Google"]
            sources.extend(alternate_sources[:random.randint(1, 2)])
            
        for src in sources:
            src_trust = calculate_trust_score(src)
            # Add a slight variation to the apply URL for alternate sources
            url = opp.apply_url
            if src != opp_data["primary_source"]:
                url = f"https://www.{src.lower().replace(' ', '')}.com/jobs?q={opp.title.replace(' ', '%20')}"
            
            opp_src = OpportunitySource(
                opportunity_id=opp.id,
                source_name=src,
                source_url=url,
                trust_score=src_trust,
                status="Active"
            )
            db.add(opp_src)
        db.commit()

    print(f"  ✅ {len(OPPORTUNITIES)} opportunities and source relationships seeded.")

    # ── 3. Sample Applications for test user ──
    test_user = created_users[0]
    opps = db.query(Opportunity).limit(5).all()
    statuses = ["Saved", "Applied", "Interview", "Applied", "Saved"]
    for opp, st in zip(opps, statuses):
        app = Application(
            user_id=test_user.id,
            opportunity_id=opp.id,
            status=st,
            applied_date=datetime.utcnow() - timedelta(days=random.randint(1, 14))
        )
        db.add(app)
    db.commit()
    print(f"  ✅ {len(opps)} sample applications created for {test_user.email}")

    # ── 4. Sample Resume & ResumeProfile for test user ──
    resumes_data = [
        {
            "filename": "Resume_Tanmesh_v3.pdf", 
            "ats_score": 87, 
            "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Node.js", "Express", "Git", "GitHub", "MongoDB", "SQL"],
            "certs": ["AWS Certified", "Terraform Associate"],
            "education": [{"degree": "B.Tech Computer Science", "institution": "State Technical Institute", "year": "2024"}],
            "experience": [
                {"role": "Frontend Developer Intern", "company": "Alpha Tech Solutions", "duration": "Jun 2023 - Dec 2023", "description": "Developed features using React, TailwindCSS, and JavaScript."}
            ],
            "projects": [
                {"title": "E-Commerce App", "description": "Built full-stack e-commerce store with React and Node.js."}
            ],
            "strengths": ["Strong Javascript and React expertise.", "Essential contact info listed.", "AWS credential verified."],
            "weaknesses": ["Missing Kubernetes and Docker knowledge.", "Lack of heavy backend framework metrics."],
            "suggestions": ["Add Docker/Kubernetes containerization to your next project.", "Quantify your frontend load time improvements (e.g., optimized React bundle by 25%)."]
        },
        {
            "filename": "Resume_DataEngineer.pdf", 
            "ats_score": 72, 
            "skills": ["Python", "SQL", "Pandas", "Spark", "Kafka", "Data Engineering", "PostgreSQL", "Linux"],
            "certs": [],
            "education": [{"degree": "B.S. Data Science", "institution": "Tech Academy", "year": "2023"}],
            "experience": [
                {"role": "Data Analyst", "company": "Retail Dynamics", "duration": "Jan 2023 - Present", "description": "Analyzed customer transaction patterns using SQL and Pandas."}
            ],
            "projects": [
                {"title": "ETL Log Pipe", "description": "Designed real-time log ingestion pipe using Kafka and Spark."}
            ],
            "strengths": ["Core Python/SQL data stack listed.", "Nice academic project on Spark."],
            "weaknesses": ["No cloud certifications listed.", "Missing orchestration tools like Airflow or dbt."],
            "suggestions": ["Obtain an AWS Certified Developer certification.", "List experience with Airflow/Prefect to show data engineering pipeline orchestrating capabilities."]
        }
    ]

    for r in resumes_data:
        # Base resume
        resume = Resume(
            user_id=test_user.id,
            filename=r["filename"],
            ats_score=r["ats_score"],
            skills_score=min(len(r["skills"]) * 8, 100),
            missing_skills="Docker, Kubernetes" if "Resume_Tanmesh" in r["filename"] else "Apache Airflow, dbt"
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # Profile details
        profile = ResumeProfile(
            user_id=test_user.id,
            uploaded_file=r["filename"],
            extracted_skills=r["skills"],
            extracted_projects=r["projects"],
            extracted_education=r["education"],
            extracted_certifications=r["certs"],
            extracted_experience=r["experience"],
            ats_score=r["ats_score"],
            strengths=r["strengths"],
            weaknesses=r["weaknesses"],
            suggestions=r["suggestions"]
        )
        db.add(profile)
        db.commit()
        
    print(f"  ✅ {len(resumes_data)} sample resume & profiles created")
    
    # ── 5. Seed Job Match Scores ──
    # Calculate match scores for Tanmesh's latest resume (Resume_Tanmesh_v3.pdf) vs seeded opportunities
    profile = db.query(ResumeProfile).filter(ResumeProfile.user_id == test_user.id, ResumeProfile.uploaded_file == "Resume_Tanmesh_v3.pdf").first()
    if profile:
        all_opps = db.query(Opportunity).all()
        # Seed match scores for first 10 opportunities
        for opp in all_opps[:10]:
            from app.match_engine import calculate_match
            score, matching, missing, level = calculate_match(
                profile.extracted_skills,
                opp.required_skills,
                opp.description
            )
            match_score = JobMatchScore(
                user_id=test_user.id,
                opportunity_id=opp.id,
                match_score=score,
                matching_skills=matching,
                missing_skills=missing,
                match_level=level
            )
            db.add(match_score)
        db.commit()
        print("  ✅ Match scores for top 10 opportunities seeded.")

    db.close()

if __name__ == "__main__":
    print("\n🚀 CareerLens AI — Resetting & Seeding Database (Phase 2)\n" + "─" * 40)
    seed_db()
    print("\n" + "─" * 40)
    print("✅ Database seeding complete!\n")
    print("Test accounts:")
    print("  📧 test@example.com    / password123")
    print("  📧 admin@careerlens.ai / admin123")
    print("  📧 tanmesh@example.com / tanmesh123")
    print()
