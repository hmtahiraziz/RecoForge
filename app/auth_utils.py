"""
Authentication utilities for admin user management.
Includes password hashing, JWT token handling, and RBAC utilities.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from models import AdminUser, AdminRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def authenticate_admin_user(email: str, password: str, db) -> Optional[AdminUser]:
    """Authenticate an admin user with email and password."""
    from sqlalchemy import select
    
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        return None
    if not verify_password(password, admin_user.password_hash):
        return None
    return admin_user

def check_role_permission(user_role: AdminRole, required_role: AdminRole) -> bool:
    """Check if user role has permission for required role."""
    role_hierarchy = {
        AdminRole.VIEWER: 1,
        AdminRole.EDITOR: 2,
        AdminRole.SUPERADMIN: 3
    }
    
    return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

def require_role(required_role: AdminRole):
    """Decorator to require specific role for GraphQL resolvers."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This will be used in GraphQL resolvers with current_user context
            # The actual implementation will be in the GraphQL resolvers
            return func(*args, **kwargs)
        return wrapper
    return decorator
