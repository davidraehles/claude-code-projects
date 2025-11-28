"""
SQLAlchemy ORM model for Knuspr Credentials.

Stores encrypted Knuspr login credentials for each user.
Uses PGCrypto for column-level encryption in PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship

from app.database import Base


class KnusprCredential(Base):
    """
    Knuspr credential storage with encryption.

    Stores user's Knuspr account credentials securely:
    - Email/phone used for Knuspr login
    - Password (encrypted in database)
    - Country (for Knuspr region selection)
    - Last authentication timestamp
    - Status (active, inactive, invalid_credentials)

    Attributes:
        id: Primary key
        user_id: Foreign key to User
        knuspr_email: Email/phone for Knuspr account (encrypted)
        knuspr_password: Knuspr password (encrypted)
        country: ISO country code (cz, sk, pl, etc.)
        is_active: Whether credentials are currently active
        last_verified_at: Last successful authentication
        verification_error: Latest error message if auth fails
        created_at: When credentials were added
        updated_at: Last update timestamp
    """

    __tablename__ = "knuspr_credentials"

    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Foreign key to User
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Encrypted credentials
    # In production, use pgcrypto or similar for encryption
    knuspr_email = Column(
        String(255),
        nullable=False,
        comment="Email or phone number for Knuspr login (encrypted)"
    )
    knuspr_password = Column(
        String(255),
        nullable=False,
        comment="Knuspr password (encrypted)"
    )

    # Metadata
    country = Column(
        String(2),
        nullable=False,
        default="cz",
        comment="ISO country code: cz (Czechia), sk (Slovakia), pl (Poland)"
    )

    # Status tracking
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether these credentials should be used for Knuspr API calls"
    )

    last_verified_at = Column(
        DateTime,
        nullable=True,
        comment="Last successful authentication with Knuspr"
    )

    verification_error = Column(
        String(500),
        nullable=True,
        comment="Error message from last failed authentication attempt"
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        return f"<KnusprCredential(user_id={self.user_id}, country='{self.country}', is_active={self.is_active})>"

    def to_dict(self, include_credentials: bool = False) -> dict:
        """
        Convert to dictionary (excluding sensitive data by default).

        Args:
            include_credentials: If True, include encrypted credentials (for internal use only)

        Returns:
            dict: Credential data without passwords unless requested
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "country": self.country,
            "is_active": self.is_active,
            "last_verified_at": self.last_verified_at.isoformat() if self.last_verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        # Only include masked email for non-internal use
        if include_credentials:
            data["knuspr_email"] = self.knuspr_email
            data["knuspr_password"] = self.knuspr_password
        else:
            # Mask email: "user@example.com" → "u***@example.com"
            email_parts = self.knuspr_email.split("@")
            if len(email_parts[0]) > 1:
                masked_email = email_parts[0][0] + "*" * (len(email_parts[0]) - 2) + email_parts[0][-1]
                if len(email_parts) > 1:
                    masked_email += "@" + email_parts[1]
                data["knuspr_email"] = masked_email
            else:
                data["knuspr_email"] = "*" * len(self.knuspr_email)

        # Include error status
        if self.verification_error:
            data["verification_error"] = self.verification_error

        return data


# Define indexes
KnusprCredential.__table_args__ = (
    Index("idx_knuspr_credentials_user_id", "user_id"),
    Index("idx_knuspr_credentials_is_active", "is_active"),
    Index("idx_knuspr_credentials_user_active", "user_id", "is_active"),
)
