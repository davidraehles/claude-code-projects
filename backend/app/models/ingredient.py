"""
SQLAlchemy ORM models for Ingredient Intelligence System.

Defines database schema for ingredients, allergens, categories, and substitutions.
"""

from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Text, Integer, Float, Boolean,
    DateTime, ForeignKey, Index, JSON, Table
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.user import JSONType


class Allergen(Base):
    """
    Common food allergens (peanuts, dairy, gluten, etc.).

    Attributes:
        id: Primary key
        name: Allergen name (e.g., "peanuts", "dairy", "gluten")
        description: Detailed description
        severity: Default severity level (low, medium, high, severe)
        created_at: Creation timestamp
    """

    __tablename__ = "allergens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, default="medium", comment="low, medium, high, severe")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ingredients = relationship(
        "Ingredient",
        secondary="ingredient_allergens",
        back_populates="allergens"
    )

    def __repr__(self) -> str:
        return f"<Allergen(id={self.id}, name='{self.name}', severity='{self.severity}')>"


class IngredientCategory(Base):
    """
    Hierarchical ingredient categories (vegetables, proteins, grains, etc.).

    Supports nested categories (e.g., Vegetables > Leafy Greens > Spinach).

    Attributes:
        id: Primary key
        name: Category name
        parent_id: Parent category for hierarchical organization
        description: Category description
    """

    __tablename__ = "ingredient_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    parent_id = Column(BigInteger, ForeignKey("ingredient_categories.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    parent = relationship("IngredientCategory", remote_side=[id], backref="subcategories")
    ingredients = relationship("Ingredient", back_populates="category")

    def __repr__(self) -> str:
        return f"<IngredientCategory(id={self.id}, name='{self.name}')>"


class Ingredient(Base):
    """
    Core ingredient taxonomy with nutrition and metadata.

    Attributes:
        id: Primary key
        name: Display name
        normalized_name: Lowercase, singular form for matching
        category_id: Foreign key to category
        aliases: Alternative names/spellings (JSON array)
        base_unit: Standard unit (gram, ml, piece, etc.)
        unit_conversions: Conversion factors to base unit (JSON object)
        nutrition_per_100g: Nutrition info (JSON object)
        seasonal_availability: Months when in season (JSON array)
        storage_tips: Storage recommendations
        shelf_life_days: Average shelf life
        is_common: Is this commonly used?
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "ingredients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    normalized_name = Column(String(255), nullable=False, unique=True, index=True)
    category_id = Column(BigInteger, ForeignKey("ingredient_categories.id", ondelete="SET NULL"), nullable=True, index=True)

    # Metadata fields
    aliases = Column(JSONType, nullable=True, comment="List of alternative names")
    base_unit = Column(String(50), nullable=True, comment="gram, ml, piece, etc.")
    # Legacy compatibility: some tests and older code expect `unit` and `calories_per_unit`
    unit = Column(String(50), nullable=True, comment="Legacy unit field, use `base_unit` instead")
    calories_per_unit = Column(Float, nullable=True, comment="Calories per declared unit")
    unit_conversions = Column(JSONType, nullable=True, comment="Conversion factors to base unit")
    nutrition_per_100g = Column(JSONType, nullable=True, comment="Calories, protein, carbs, fat, fiber")
    seasonal_availability = Column(JSONType, nullable=True, comment="Months when in season")
    storage_tips = Column(Text, nullable=True)
    shelf_life_days = Column(Integer, nullable=True)
    is_common = Column(Boolean, default=True, index=True, comment="Commonly used ingredient")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("IngredientCategory", back_populates="ingredients")
    allergens = relationship(
        "Allergen",
        secondary="ingredient_allergens",
        back_populates="ingredients"
    )
    substitutions_from = relationship(
        "SubstitutionRule",
        foreign_keys="SubstitutionRule.ingredient_id",
        back_populates="ingredient"
    )
    substitutions_to = relationship(
        "SubstitutionRule",
        foreign_keys="SubstitutionRule.substitute_id",
        back_populates="substitute"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name='{self.name}', category='{self.category.name if self.category else None}')>"

    def to_dict(self) -> dict:
        """Convert ingredient to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "normalized_name": self.normalized_name,
            "category": self.category.name if self.category else None,
            "aliases": self.aliases,
            "base_unit": self.base_unit,
            "nutrition_per_100g": self.nutrition_per_100g,
            "seasonal_availability": self.seasonal_availability,
            "is_common": self.is_common,
            "allergens": [a.name for a in self.allergens] if self.allergens else [],
        }

    def __init__(self, *args, **kwargs):
        # Ensure normalized_name is populated for legacy tests and inserts
        if "normalized_name" not in kwargs and "name" in kwargs:
            kwargs["normalized_name"] = str(kwargs["name"]).lower()

        # Map legacy `unit` to `base_unit` when provided
        if "base_unit" not in kwargs and "unit" in kwargs:
            kwargs["base_unit"] = kwargs.get("unit")

        super().__init__(*args, **kwargs)


# Association table for ingredient-allergen many-to-many relationship
class IngredientAllergen(Base):
    """
    Links ingredients to allergens with optional severity override.
    """

    __tablename__ = "ingredient_allergens"

    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    allergen_id = Column(BigInteger, ForeignKey("allergens.id", ondelete="CASCADE"), primary_key=True)
    severity_override = Column(String(20), nullable=True, comment="Override allergen severity")

    def __repr__(self) -> str:
        return f"<IngredientAllergen(ingredient_id={self.ingredient_id}, allergen_id={self.allergen_id})>"


class SubstitutionRule(Base):
    """
    Ingredient substitution mappings and rules.

    Defines which ingredients can substitute for others with ratio and quality score.

    Attributes:
        id: Primary key
        ingredient_id: Original ingredient
        substitute_id: Substitute ingredient
        ratio: Substitution ratio (1.5 = use 150% of substitute)
        quality_score: How good is this substitution? (0-1 scale)
        notes: Usage notes and tips
        context: When is this appropriate? (JSON)
        is_vegan: Is this a vegan-friendly substitution?
        is_vegetarian: Is this vegetarian-friendly?
        is_gluten_free: Is this gluten-free?
        is_dairy_free: Is this dairy-free?
        created_at: Creation timestamp
    """

    __tablename__ = "substitution_rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    substitute_id = Column(BigInteger, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    ratio = Column(Float, nullable=False, default=1.0, comment="Substitution ratio")
    quality_score = Column(Float, nullable=True, comment="Quality score 0-1")
    notes = Column(Text, nullable=True, comment="Usage notes")
    context = Column(JSONType, nullable=True, comment="When is this appropriate?")

    # Dietary flags
    is_vegan = Column(Boolean, default=False)
    is_vegetarian = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    ingredient = relationship("Ingredient", foreign_keys=[ingredient_id], back_populates="substitutions_from")
    substitute = relationship("Ingredient", foreign_keys=[substitute_id], back_populates="substitutions_to")

    def __repr__(self) -> str:
        return f"<SubstitutionRule(id={self.id}, {self.ingredient_id} -> {self.substitute_id}, ratio={self.ratio})>"

    def to_dict(self) -> dict:
        """Convert substitution rule to dictionary."""
        return {
            "id": self.id,
            "ingredient": self.ingredient.name if self.ingredient else None,
            "substitute": self.substitute.name if self.substitute else None,
            "ratio": self.ratio,
            "quality_score": self.quality_score,
            "notes": self.notes,
            "context": self.context,
            "is_vegan": self.is_vegan,
            "is_vegetarian": self.is_vegetarian,
            "is_gluten_free": self.is_gluten_free,
            "is_dairy_free": self.is_dairy_free,
        }


# Indexes
Ingredient.__table_args__ = (
    Index("ix_ingredients_category", "category_id"),
    Index("ix_ingredients_common", "is_common"),
    Index("ix_ingredients_normalized", "normalized_name"),
)

SubstitutionRule.__table_args__ = (
    Index("ix_substitutions_ingredient", "ingredient_id"),
    Index("ix_substitutions_substitute", "substitute_id"),
    Index("ix_substitutions_quality", "quality_score"),
)
