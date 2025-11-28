#!/usr/bin/env python3
"""
Seed test user for development and testing.

This script creates a test user in the database for authentication testing.
Can be run locally or in production (Railway) environment.

Usage:
    python scripts/seed_test_user.py
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.user import User
from app.api.v1.auth import hash_password


def seed_test_user():
    """Create test user if it doesn't exist."""

    # Test user credentials
    TEST_EMAIL = "test@example.com"
    TEST_PASSWORD = "testpassword123"
    TEST_COUNTRY = "US"

    print("🌱 Seeding test user...")
    print(f"   Email: {TEST_EMAIL}")
    print(f"   Password: {TEST_PASSWORD}")
    print(f"   Country: {TEST_COUNTRY}")
    print()

    db: Session = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == TEST_EMAIL).first()

        if existing_user:
            print(f"ℹ️  Test user already exists (ID: {existing_user.id})")
            print("   Updating password to ensure it matches test credentials...")

            # Update password to match test credentials
            existing_user.password_hash = hash_password(TEST_PASSWORD)
            existing_user.country = TEST_COUNTRY
            existing_user.deleted_at = None  # Ensure account is not soft-deleted

            db.commit()
            print("✅ Test user password updated successfully!")
        else:
            # Create new test user
            print("📝 Creating new test user...")

            new_user = User(
                email=TEST_EMAIL,
                password_hash=hash_password(TEST_PASSWORD),
                country=TEST_COUNTRY,
                subscription_tier="free",
                preferences={}
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            print(f"✅ Test user created successfully! (ID: {new_user.id})")

        print()
        print("🎉 Test user is ready for authentication!")
        print()
        print("Test credentials:")
        print(f"   Email:    {TEST_EMAIL}")
        print(f"   Password: {TEST_PASSWORD}")
        print()

    except Exception as e:
        print(f"❌ Error seeding test user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Test User Seeding Script")
    print("=" * 60)
    print()

    seed_test_user()

    print("=" * 60)
