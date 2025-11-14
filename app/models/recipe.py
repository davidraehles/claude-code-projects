"""
SQLAlchemy ORM models for Recipe entity.

Defines the database schema for recipes with relationships and indexes
for efficient querying.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Recipe(Base):
    """
    Recipe model representing a recipe in the database.

    Attributes:
        id: Primary key
        title: Recipe title (unique per source)
        ingredients: JSON array of ingredients
        instructions: Recipe instructions
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        servings: Number of servings
        nutrition: JSON object with nutrition information
        source_url: Original source URL
        source_type: Type of source (html, api, rss)
        duplicate_of_id: References parent recipe if this is a duplicate
        created_at: Creation timestamp
        last_updated: Last update timestamp
    """

    __tablename__ = "recipes"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Core recipe data
    title = Column(String(255), nullable=False, index=True)
    ingredients = Column(JSON, nullable=False)
    instructions = Column(Text, nullable=False)

    # Timing information
    prep_time = Column(Integer, nullable=True, comment="Preparation time in minutes")
    cook_time = Column(Integer, nullable=True, comment="Cooking time in minutes")
    servings = Column(Integer, nullable=True)

    # Nutrition information
    nutrition = Column(JSON, nullable=True, comment="Nutrition per serving")

    # Source tracking
    source_url = Column(String(2000), nullable=False, unique=True, index=True)
    source_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="'html', 'api', or 'rss'"
    )

    # Duplicate management
    duplicate_of_id = Column(
        Integer,
        ForeignKey("recipes.id"),
        nullable=True,
        comment="References parent if this is a duplicate"
    )

    # Relationships
    duplicates = relationship(
        "Recipe",
        remote_side=[id],
        foreign_keys=[duplicate_of_id],
        backref="parent_recipe",
        cascade="all, delete-orphan"
    )

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, title='{self.title}', source_type='{self.source_type}')>"

    def to_dict(self) -> dict:
        """Convert recipe to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "servings": self.servings,
            "nutrition": self.nutrition,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "duplicate_of_id": self.duplicate_of_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


# Define indexes for common queries
__table_args__ = (
    Index("ix_recipes_source_url", "source_url"),
    Index("ix_recipes_source_type", "source_type"),
    Index("ix_recipes_created_at", "created_at"),
    Index("ix_recipes_duplicate_of_id", "duplicate_of_id"),
    # Composite index for finding non-duplicate recipes
    Index("ix_recipes_not_duplicate", "duplicate_of_id", "created_at"),
)

Recipe.__table_args__ = __table_args__
