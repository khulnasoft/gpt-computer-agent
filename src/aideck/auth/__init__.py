"""
Authentication and authorization module for the GPT Computer Agent.
"""

from datetime import datetime, timedelta
from typing import Optional

try:
    from fastapi import HTTPException, status
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for environments without FastAPI
    jwt = None
    CryptContext = None
    BaseModel = object
    Field = None
    HTTPException = Exception
    status = None

from ..config.settings import settings

# Password hashing
pwd_context = (
    CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None
)

# Token configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if BaseModel is not None:

    class Token(BaseModel):
        """Token response model."""

        access_token: str
        token_type: str = "bearer"

    class TokenData(BaseModel):
        """Token data model."""

        username: str | None = None

    class User(BaseModel):
        """User model."""

        username: str
        email: str | None = None
        full_name: str | None = None
        disabled: bool = False

    class UserInDB(User):
        """User model for database storage."""

        hashed_password: str

else:
    # Fallback classes for environments without dependencies
    Token = None
    TokenData = None
    User = None
    UserInDB = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    if pwd_context is None:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    if pwd_context is None:
        return ""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new access token."""
    if jwt is None:
        return ""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> User | None:
    """Verify a JWT token and return the user if valid."""
    if jwt is None or HTTPException is None or status is None:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# In a real application, you would store users in a database
# This is just for demonstration purposes
fake_users_db = {}


def get_user(username: str) -> UserInDB | None:
    """Get a user by username."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
