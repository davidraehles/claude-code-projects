"""
Models package for the recipe application.

Exports all SQLAlchemy models for easy import.
"""

from app.models.user import User
from app.models.recipe import Recipe

__all__ = ["User", "Recipe"]
