import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file (if running locally without Docker)
load_dotenv()

# Enforce PostgreSQL via env variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required and must point to a PostgreSQL database. SQLite fallback is no longer supported.")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("SQLite is no longer supported for CareerLens AI. You must configure a PostgreSQL DATABASE_URL.")

engine = create_engine(

        SQLALCHEMY_DATABASE_URL, 
        pool_size=100, 
        max_overflow=200,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
