"""SQLAlchemy models for user authentication."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    @property
    def is_authenticated(self) -> bool:
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self) -> bool:
        """Return True if the user is anonymous."""
        return False

    def get_id(self) -> str:
        """Return the user ID as a string."""
        return str(self.id)

class RefreshToken(Base):
    """Refresh token model for JWT token refresh."""
    # ... rest of RefreshToken implementation ...

class RefreshToken(Base):
    ""
    Refresh token model for JWT token refresh.
    """
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<RefreshToken {self.token[:10]}...>"
