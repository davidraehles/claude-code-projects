"""
Test setup utilities for handling database connections during testing.

This module provides utilities to handle database setup for tests,
falling back to SQLite when PostgreSQL is not available.
"""

import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def setup_test_database():
    """
    Setup test database connection.

    If PostgreSQL is not available, configure the app to use SQLite for testing.
    This allows tests to run without requiring a PostgreSQL server.
    """
    try:
        # Try to import and test PostgreSQL connection
        from sqlalchemy import create_engine
        from sqlalchemy.exc import OperationalError

        # Test if PostgreSQL is available
        try:
            test_engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
            with test_engine.connect() as conn:
                pass  # Connection successful
            print("✅ PostgreSQL is available, using PostgreSQL for tests")
            return True
        except (OperationalError, ImportError):
            print("⚠️ PostgreSQL not available, falling back to SQLite for tests")

            # Configure environment to use SQLite for testing
            os.environ["DB_USER"] = ""
            os.environ["DB_PASSWORD"] = ""
            os.environ["DB_HOST"] = ""
            os.environ["DB_PORT"] = ""
            os.environ["DB_NAME"] = "test.db"
            os.environ["DATABASE_URL"] = "sqlite:///test.db"

            # Also update the app database configuration
            from app.database import engine, Base

            # Create SQLite engine
            sqlite_engine = create_engine("sqlite:///test.db")
            Base.metadata.create_all(bind=sqlite_engine)

            print("✅ SQLite database setup complete")
            return True

    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return False

def cleanup_test_database():
    """
    Cleanup test database after tests complete.
    """
    try:
        # Remove SQLite database file if it exists
        db_path = Path("test.db")
        if db_path.exists():
            db_path.unlink()
            print("✅ Test database cleaned up")
    except Exception as e:
        print(f"⚠️ Error cleaning up test database: {e}")

if __name__ == "__main__":
    print("Setting up test database...")
    success = setup_test_database()
    if success:
        print("Test database setup completed successfully!")
    else:
        print("Test database setup failed!")
        sys.exit(1)