"""
SQLAlchemy ORM model for WaitlistEntry entity.

Defines the database schema for waitlist signups with status tracking and verification.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.models.user import JSONType


class WaitlistEntry(Base):
    """
    WaitlistEntry model representing a user waiting for early access.

    Attributes:
        id: Primary key
        email: User email address (unique)
        status: Current status (PENDING, VERIFIED, INVITED, ONBOARDED)
        verification_token: Token for email verification
        created_at: Signup timestamp
        verified_at: Verification timestamp
        invited_at: Invitation timestamp
    """

    __tablename__ = "waitlist_entries"

    # Primary key
    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )

    # Core fields
    email = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(
        String(20),
        nullable=False,
        default="PENDING",
        index=True,
        comment="PENDING, VERIFIED, INVITED, ONBOARDED"
    )
    verification_token = Column(String(255), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now(), index=True)
    verified_at = Column(DateTime, nullable=True, index=True)
    invited_at = Column(DateTime, nullable=True, index=True)

    # Metadata
    metadata_payload = Column(
        "metadata",
        JSONType,
        nullable=True,
        comment="Marketing attribution (source, campaign, etc.)"
    )

    def __repr__(self) -> str:
        return f"<WaitlistEntry(id={self.id}, email='{self.email}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """
        Convert waitlist entry to dictionary for API responses.
        """
        return {
            "id": self.id,
            "email": self.email,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "invited_at": self.invited_at.isoformat() if self.invited_at else None,
        }
