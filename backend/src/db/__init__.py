# Legacy compatibility layer for tests expecting `src.db`.
from app import models  # noqa: F401

__all__ = ["models"]
