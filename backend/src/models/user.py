"""
User model for Todo AI Chatbot
"""

from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from pydantic import EmailStr
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.USER)
    email_verified: bool = Field(default=False)
    password_hash: Optional[str] = Field(default=None)  # For email/password auth
    provider: str = Field(default="credentials")  # "credentials", "google", "github", etc.
    provider_id: Optional[str] = Field(default=None)  # ID from the provider
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Add indexes for common queries
    __table_args__ = (
        {"extend_existing": True},
    )