# CareerLens AI (v1.0.0)

> **Data-Driven Career Intelligence & Autonomous Opportunity Acquisition Engine**

CareerLens AI is an end-to-end autonomous career intelligence platform engineered to eliminate job search opacity. It aggregates verified job opportunities directly from official corporate career ATS portals, scores role readiness using AI matching algorithms, curates targeted skill paths, and provides real-time data telemetry for job seekers and hiring trends.

---

## 🌟 Why CareerLens AI?

The modern job search landscape suffers from widespread ghost jobs, stale postings, third-party aggregator spam, and mismatched skill requirements. **CareerLens AI** addresses these problems at the root:

1. **Direct Official ATS Acquisition**: Collects job data straight from corporate Greenhouse, Lever, Workday, SmartRecruiters, and custom API endpoints—filtering out unverified aggregators.
2. **Explainable AI Matching**: Evaluates candidate readiness using multi-vector skill coverage, resume relevance, and experience scoring rather than black-box algorithms.
3. **Adaptive Pipeline Telemetry**: Continuously monitors collector health, source yields, link integrity status, and pipeline execution schedules in real time.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS 4, React Router 7, Material Symbols |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, Uvicorn, SQLAlchemy |
| **Database** | PostgreSQL 16, Alembic Migrations |
| **ETL & Scheduling** | Autonomous Collectors, APScheduler (Background Async Worker) |
| **Email Service** | Resend Transactional Email API |
| **Cloud Hosting** | Render (API & Worker & PostgreSQL), Vercel (Frontend SPA) |

---

## 🏗️ Architecture & Data Pipeline

```mermaid
flowchart TD
    subgraph Sources ["Official ATS Sources & APIs"]
        S1["Greenhouse ATS"]
        S2["Lever ATS"]
        S3["Workday & Portal APIs"]
    end

    subgraph Pipeline ["ETL & Acquisition Engine"]
        W["APScheduler Worker"] --> C1["Greenhouse Collector"]
        W --> C2["Lever Collector"]
        W --> C3["API Collector"]
        C1 --> Dedup["Normalization & Deduplication"]
        C2 --> Dedup
        C3 --> Dedup
    end

    subgraph Storage ["Database & Storage Layer"]
        Dedup --> DB[("PostgreSQL 16")]
    end

    subgraph API ["FastAPI Engine & Business Services"]
        DB <--> API_S["FastAPI Endpoints"]
        API_S --> Auth["JWT & Password Hashing"]
        API_S --> Matcher["AI Matching & Readiness Engine"]
        API_S --> Telemetry["Data Intelligence OS"]
    end

    subgraph Frontend ["React SPA Application"]
        API_S <--> ReactApp["Vite + React 19 Frontend"]
    end

    Sources --> Pipeline
```

---

## ⚡ Key Features

- 🎯 **Opportunities Hub**: Multi-filter job search (search text, location, job type, experience, relevance) with link integrity tracking and lifecycle status indicators.
- 📊 **Career Readiness Diagnostics**: Quantifies skill coverage %, resume alignment %, and experience compatibility score for targeted roles.
- 🚀 **Data Intelligence OS**: Telemetry dashboard providing health metrics, active alerts, source yield breakdown, and collector status tracking.
- 🎓 **Learn Skills & Resources Engine**: Market-backed skill recommendation paths with curated resources and certifications.
- 🔐 **Secure Authentication**: JWT session management, email verification via Resend, and password recovery.

---

## 🗄️ Database Schema & Key Entities

```mermaid
erDiagram
    USERS ||--o{ APPLICATIONS : owns
    USERS ||--o{ RESUMES : uploads
    OPPORTUNITIES ||--o{ APPLICATIONS : references
    COLLECTORS ||--o{ COLLECTOR_LOGS : records

    USERS {
        int id PK
        string email UK
        string password_hash
        boolean is_verified
        datetime created_at
    }

    OPPORTUNITIES {
        int id PK
        string title
        string company
        string location
        string apply_url
        string primary_source
        string status
        int trust_score
        datetime posted_date
    }

    APPLICATIONS {
        int id PK
        int user_id FK
        int opportunity_id FK
        string status
        datetime applied_date
    }
```

---

## 📂 Project Structure

```
CareerLens-AI/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers & endpoints
│   │   ├── core/         # Security, JWT, config & settings
│   │   ├── db/           # SQLAlchemy models & session
│   │   ├── services/     # Matching engine, email, intelligence
│   │   └── scheduler/    # APScheduler background ETL collector worker
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # Standardized UI system (Button, Input, Card, etc.)
│   │   ├── pages/        # Application view routes
│   │   ├── api.js        # API service client
│   │   └── index.css     # Design tokens & Tailwind styles
│   ├── vercel.json       # Vercel deployment configuration
│   └── package.json      # Node dependencies
├── render.yaml           # Render IaC infrastructure definition
├── LICENSE               # MIT Open Source License
└── README.md
```

---

## 💻 Local Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start local dev server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env

# Start local React dev server
npm run dev
```

Visit `http://localhost:5173` to access the application locally.

---

## ☁️ Production Deployment Guide

### Deploying to Render
1. Push your repository to GitHub.
2. Connect your repository to **Render**.
3. Render automatically provisions Web Service, Background Worker, and Managed PostgreSQL using `render.yaml`.
4. Configure production environment variables (`DATABASE_URL`, `SECRET_KEY`, `RESEND_API_KEY`).

### Deploying to Vercel
1. Connect frontend directory to **Vercel**.
2. Set Build Command to `npm run build` and Output Directory to `dist`.
3. Set Environment Variable `VITE_API_URL` to your Render API domain.

---

## 📑 API Overview

- `GET /health`: Platform health & database connectivity check.
- `POST /api/auth/register`: User account creation & email verification trigger.
- `POST /api/auth/login`: User authentication & JWT issuance.
- `GET /api/opportunities`: Search & filter opportunities with pagination.
- `GET /api/opportunities/{id}`: Detailed opportunity payload with match score breakdown.
- `GET /api/intelligence/collectors`: Telemetry & health metrics for Data Intelligence OS.

---

## 📄 License & Governance

This project is licensed under the [MIT License](LICENSE).
Contributions are welcome—see [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
