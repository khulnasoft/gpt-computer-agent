""
Database session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from ..config.settings import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    ""
    Dependency function to get DB session.
    """
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()

def init_db():
    ""
    Initialize the database by creating all tables.
    """
    from ..models.user import User, RefreshToken
    Base.metadata.create_all(bind=engine)

    # Create first superuser if no users exist
    db = SessionLocal()
    try:
        from ..services.user import create_first_superuser
        create_first_superuser(db)
    finally:
        db.close()
