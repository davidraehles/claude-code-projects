"""
Pydantic schemas for Waitlist API validation.

Defines request/response models for waitlist signup, verification, and status checks.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class WaitlistStatus(str, Enum):
    """Waitlist entry status enum."""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    INVITED = "INVITED"
    ONBOARDED = "ONBOARDED"


class WaitlistCreate(BaseModel):
    """Schema for joining the waitlist."""
    email: EmailStr = Field(..., description="User email address")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional marketing attribution data"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "metadata": {
                    "source": "landing_page",
                    "campaign": "launch"
                }
            }
        }
    )


class WaitlistVerify(BaseModel):
    """Schema for email verification."""
    token: str = Field(..., description="Verification token from email")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123-def456-ghi789"
            }
        }
    )


class WaitlistStatusRequest(BaseModel):
    """Schema for checking waitlist status."""
    email: EmailStr = Field(..., description="User email address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com"
            }
        }
    )


class WaitlistResponse(BaseModel):
    """Schema for waitlist responses."""
    id: int = Field(..., description="Waitlist entry ID")
    email: str = Field(..., description="User email")
    status: WaitlistStatus = Field(..., description="Current status")
    position: Optional[int] = Field(None, description="Approximate queue position")
    created_at: datetime = Field(..., description="Creation timestamp")
    verified_at: Optional[datetime] = Field(None, description="Email verification timestamp")
    invited_at: Optional[datetime] = Field(None, description="Invitation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "status": "PENDING",
                "position": 42,
                "created_at": "2025-12-07T22:00:00Z",
                "verified_at": None,
                "invited_at": None
            }
        }
    )
