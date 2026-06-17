# CareerLens AI 🔍

> **AI-Powered Job Intelligence, Internship Discovery, and Career Growth Platform**

Search Once. Learn Smart. Get Hired.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Real-time career metrics, AI insights, and activity feed |
| **Opportunities Hub** | Smart job/internship search with trust scores and filters |
| **Resume Analysis** | AI-powered ATS score, skills gap analysis, and optimization tips |
| **Application Tracker** | Drag-and-drop Kanban board for managing your pipeline |
| **Learn Skills** | Interactive career roadmaps with progress tracking |
| **Career Explorer** | Browse career paths with salary data and growth projections |
| **Interview Prep** | Question bank with mock interviews and timed sessions |
| **Certifications** | Discover and track industry certifications |
| **Free Resources** | Curated library of free learning materials |
| **Insights Dashboard** | Analytics and trends for your job search |
| **Profile Management** | Comprehensive settings and preference management |
| **Notifications** | Smart alerts for job matches and application updates |

## 🏗 Architecture

```
careerlens-ai/          → React + Vite frontend (SPA)
careerlens-backend/     → FastAPI + SQLAlchemy backend (REST API)
```

### Tech Stack

**Frontend:**
- React 19 + Vite 6
- React Router v7
- Tailwind CSS v4
- Material Symbols icons
- Inter + Geist typography

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- PostgreSQL (production) / SQLite (dev)
- JWT Authentication (python-jose + bcrypt)
- Gunicorn + Uvicorn workers

## 📦 Local Development

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (optional, uses SQLite by default)

### Backend Setup

```bash
cd careerlens-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run seed script (optional - creates test data)
python seed.py

# Start dev server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd careerlens-ai

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend runs at `http://localhost:5173` and the backend API at `http://localhost:8000`.

### Default Test Account
- **Email:** test@example.com
- **Password:** password123

## 🌐 Deployment

### Option 1: Render.com (Recommended)

1. Push both directories to a GitHub repository
2. Connect the repo to [Render](https://render.com)
3. Render will auto-detect the `render.yaml` blueprint and provision:
   - FastAPI backend web service
   - React static site
   - PostgreSQL database

### Option 2: Manual Deployment

**Backend:**
```bash
cd careerlens-backend

# Set environment variables (see .env.example)
export DATABASE_URL=postgresql://user:pass@host:5432/careerlens
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export FRONTEND_URL=https://your-frontend-domain.com

# Build and run with Docker
docker build -t careerlens-api .
docker run -p 8000:8000 --env-file .env careerlens-api
```

**Frontend:**
```bash
cd careerlens-ai

# Set the API URL
echo "VITE_API_URL=https://your-api-domain.com/api" > .env

# Build for production
npm run build

# Deploy the 'dist' folder to any static hosting:
# - Vercel, Netlify, Cloudflare Pages, GitHub Pages, etc.
```

### Environment Variables

#### Backend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key (generate with `secrets.token_hex(32)`) |
| `FRONTEND_URL` | ✅ | Frontend URL for CORS |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | JWT token lifetime (default: 30) |

#### Frontend (.env)
| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ✅ | Backend API base URL (e.g. `https://api.example.com/api`) |

## 📁 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | ❌ | Register new user |
| POST | `/api/auth/token` | ❌ | Login (get JWT) |
| GET | `/api/users/me` | ✅ | Get current user |
| GET | `/api/opportunities` | ❌ | List all opportunities |
| POST | `/api/opportunities` | ✅ | Create opportunity |
| GET | `/api/applications` | ✅ | Get user applications |
| POST | `/api/applications` | ✅ | Create application |
| PUT | `/api/applications/:id` | ✅ | Update application status |
| POST | `/api/resumes/analyze` | ✅ | Upload & analyze resume |
| GET | `/api/resumes` | ✅ | Get resume history |
| GET | `/api/health` | ❌ | Health check |

Full interactive API docs available at `/docs` (Swagger UI).

## 📄 License

MIT License
