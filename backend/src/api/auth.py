"""
Authentication API endpoints for Todo AI Chatbot
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..models.user import User, UserRole
from sqlmodel import Session, select
from ..database import get_session
import os
import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for bearer token
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(password: str) -> str:
    """Hash a plain password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_SECRET", "todo-ai-chatbot-secret"), algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return user data."""
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET", "todo-ai-chatbot-secret"), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/signup")
async def signup_user(email: str, password: str, name: Optional[str] = None, session: Session = Depends(get_session)):
    """
    Register a new user account.
    """
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(password)

    # Create new user
    user = User(
        id=uuid.uuid4(),
        email=email,
        name=name,
        role=UserRole.USER,
        email_verified=False,
        password_hash=hashed_password,
        provider="credentials"
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return {
        "success": True,
        "message": "User created successfully",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/login")
async def login_user(email: str, password: str, session: Session = Depends(get_session)):
    """
    Authenticate an existing user.
    """
    # Find user by email
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout_user():
    """
    End the current user session.
    Note: In a real JWT implementation, this would typically involve blacklisting the token
    or relying on short-lived tokens with refresh token rotation.
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user profile information.
    """
    # Verify the token first
    user_data = verify_token(credentials.credentials)

    user_id = user_data.get("sub")

    # Get user from database
    from sqlmodel import Session
    from ..database import get_engine

    with Session(get_engine()) as session:
        user = session.get(User, uuid.UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "email_verified": user.email_verified
        }