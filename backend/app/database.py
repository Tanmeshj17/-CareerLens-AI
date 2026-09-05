import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("careerlens.database")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = None

if SQLALCHEMY_DATABASE_URL:
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

    if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        try:
            temp_engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_recycle=300,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5}
            )
            # Verify host resolution and database reachability
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine = temp_engine
            logger.info("Successfully connected to primary PostgreSQL database.")
        except Exception as pg_err:
            logger.warning(f"PostgreSQL connection failed ({pg_err}). Falling back to local embedded database.")
            engine = None

if engine is None:
    # High-availability SQLite fallback
    sqlite_url = "sqlite:///./careerlens.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )
    logger.info("Using embedded SQLite database engine for 100% availability.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
