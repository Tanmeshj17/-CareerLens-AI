@echo off
set ENVIRONMENT=production
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/careerlens_prod
set EMAIL_API_KEY=re_fake_123
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
