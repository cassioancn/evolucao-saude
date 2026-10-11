import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

try:
    import streamlit as st
except ImportError:
    st = None

Base = declarative_base()

def get_database_url() -> str:
    # 1. Try Streamlit secrets
    try:
        if st is not None and hasattr(st, "secrets") and "database" in st.secrets and "url" in st.secrets["database"]:
            return st.secrets["database"]["url"]
    except Exception:
        pass
    
    # 2. Try environment variable
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url
    
    # 3. Fallback: hardcoded Neon URL provided by user
    return "postgresql://neondb_owner:npg_HepmsqXj3ri0@ep-small-salad-b4pp29nh-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_database_url()
        # SQLAlchemy requires postgresql:// instead of postgres://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        
        # Configure connection pool suitable for Neon Serverless
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,      # Pings the DB to detect dropped serverless connections
            pool_recycle=300,        # Recycles connections every 5 minutes
            pool_size=5,
            max_overflow=10
        )
    return _engine

def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)

@contextmanager
def get_db():
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
