# Authentication utilities: JWT creation/verification and password hashing

from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# This secret should be set via environment variable in production
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev_secret_dont_use_in_prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Returns a hashed password."""
    return pwd_context.hash(password)

# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a plain password to a hash."""
    return pwd_context.verify(plain_password, hashed_password)

# PUBLIC_INTERFACE
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire}
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Optional[str]:
    """Decodes the JWT and returns the user email (subject) if valid."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# PUBLIC_INTERFACE
def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    """Dependency to get current user's email from JWT token."""
    email = decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email
