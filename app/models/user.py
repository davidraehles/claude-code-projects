"""
SQLAlchemy ORM models for User entity.

Defines the database schema for users with authentication and preferences.
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TypeDecorator

from app.database import Base


# Database-agnostic JSON type (JSONB for PostgreSQL, JSON for others)
class JSONType(TypeDecorator):
    """
    JSON type that uses JSONB for PostgreSQL and JSON for other databases.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class User(Base):
    """
    User model representing a user in the system.

    Attributes:
        id: Primary key
        email: User email address (unique)
        password_hash: Hashed password (bcrypt)
        country: ISO 3166-1 alpha-2 country code (DE, AT, CH, etc.)
        subscription_tier: Subscription level (free, basic, premium)
        subscription_expires_at: Expiration date for paid subscriptions
        preferences: JSONB field for user preferences
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        deleted_at: Soft delete timestamp (for GDPR compliance)
    """

    __tablename__ = "users"

    # Primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Authentication
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # User metadata
    country = Column(String(2), nullable=False, comment="ISO 3166-1 alpha-2 country code")
    subscription_tier = Column(
        String(50),
        nullable=False,
        default="free",
        comment="Subscription level: free, basic, premium"
    )
    subscription_expires_at = Column(DateTime, nullable=True, index=True)

    # User preferences (flexible JSON field)
    preferences = Column(
        JSONType,
        nullable=True,
        comment="User preferences: language, theme, dietary preferences, etc."
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True, comment="Soft delete for GDPR compliance")

    # Relationships
    recipes = relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Recipe.user_id"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', country='{self.country}')>"

    def to_dict(self) -> dict:
        """
        Convert user to dictionary (excluding sensitive fields).

        Returns:
            dict: User data without password_hash
        """
        return {
            "id": self.id,
            "email": self.email,
            "country": self.country,
            "subscription_tier": self.subscription_tier,
            "subscription_expires_at": self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Define indexes
User.__table_args__ = (
    Index("idx_users_email", "email"),
    Index("idx_users_subscription_expires", "subscription_expires_at"),
)
