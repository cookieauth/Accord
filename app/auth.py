# app/auth.py

from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app import crud, models
from app.models import User

import logging

logger = logging.getLogger(__name__)

# Secret key for JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)

def hash_pw(password: str) -> str:
    """
    Hashes a plain password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate_user(username: str, password: str) -> Optional[models.User]:
    """
    Authenticates a user by username and password.
    """
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.User)
            .where(models.User.username == username)
        )
        user = result.scalars().first()
        if not user:
            logger.warning(f"Authentication failed for non-existent user: {username}")
            return None
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed for user: {username} due to incorrect password")
            return None
        logger.info(f"User authenticated successfully: {username}")
        return user

async def get_current_user(request: Request) -> models.User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Assuming the token is in the format "Bearer <token>"
        token_parts = token.split(" ")
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(token_parts[1], SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with crud.async_session() as session:
        result = await session.execute(
            select(models.User)
            .options(
                selectinload(models.User.notifications),
                selectinload(models.User.department)  # Eagerly load department
            )
            .where(models.User.username == username)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return user

def has_permission(required_roles: List[str]):
    """
    Dependency to check if the current user has at least one of the required roles.
    """
    role_hierarchy = {
        "admin": 3,
        "hr": 2,
        "department": 1,
        "user": 0,
    }

    async def permission_dependency(current_user: User = Depends(get_current_user)):
        # Check if the user's role is in the required_roles list
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )
        return current_user

    return permission_dependency