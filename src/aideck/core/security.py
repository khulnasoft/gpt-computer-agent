"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    from sqlalchemy.orm import Session

    from ..config.settings import settings
    from ..db.session import get_db
    from ..models.user import User
except ImportError:
    # Fallback for environments without FastAPI/SQLAlchemy
    jwt = None
    CryptContext = None
    HTTPException = Exception
    status = None
    OAuth2PasswordBearer = None
    Session = None
    User = None
    settings = None
    get_db = None

# Password hashing
pwd_context = (
    CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None
)

# OAuth2 scheme
oauth2_scheme = (
    OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")
    if OAuth2PasswordBearer and settings
    else None
)


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
    if jwt is None or settings is None:
        return ""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire, "iss": settings.JWT_ISSUER, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new refresh token."""
    if jwt is None or settings is None:
        return ""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    data.update({"exp": expire, "iss": settings.JWT_ISSUER, "type": "refresh"})
    encoded_jwt = jwt.encode(
        data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode a JWT token."""
    if jwt is None or settings is None or HTTPException is None or status is None:
        return {}
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_iss": True, "require_iss": True},
            issuer=settings.JWT_ISSUER,
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    db: Session = Depends(get_db) if get_db else None,
    token: str = Depends(oauth2_scheme) if oauth2_scheme else None,
) -> User:
    """Get the current authenticated user."""
    if User is None or HTTPException is None or status is None:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if db is None:
        return None

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user."""
    if current_user is None or HTTPException is None or status is None:
        return None
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user") from None
    return current_user


def verify_password_reset_token(token: str) -> str | None:
    """Verify a password reset token and return the username if valid."""
    if jwt is None or settings is None:
        return None
    try:
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            return None
        username: str = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None
    return username
