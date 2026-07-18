from typing import Generator
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.config.settings import settings

connect_args = {}
# Use SQLite specific connect_args to avoid threading issues
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency to get a database session for FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis_client() -> redis.Redis:
    """
    Factory function to get a Redis client connected to the configured URL.
    """
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
