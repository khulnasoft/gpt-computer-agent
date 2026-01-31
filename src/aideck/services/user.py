"""
User service for handling user-related operations.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> models.User | None:
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Get a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    """Get a list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, db_user: models.User, user_update: schemas.UserUpdate
) -> models.User:
    """Update user information."""
    user_data = user_update.dict(exclude_unset=True)

    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.utcnow()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> models.User:
    """Delete a user."""
    user = get_user(db, user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    db.delete(user)
    db.commit()
    return user


def authenticate(db: Session, username: str, password: str) -> models.User | None:
    """Authenticate a user."""
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_first_superuser(db: Session) -> models.User:
    """Create the first superuser if no users exist."""
    from ..config.settings import settings

    if db.query(models.User).count() == 0:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            username="admin",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin",
        )
        user = create_user(db, user_in)
        user.is_superuser = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return None
