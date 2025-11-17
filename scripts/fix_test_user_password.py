"""
Fix the test user password hash in the database.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.user import User


def fix_test_user_password():
    """Update the test user's password hash to match 'testpassword123'."""
    db = SessionLocal()

    try:
        print("🔧 Fixing test user password...")

        # Find test user
        test_user = db.query(User).filter_by(email="test@example.com").first()
        if not test_user:
            print("❌ Test user not found. Run seed_test_data.py first.")
            return

        # Update password hash
        old_hash = test_user.password_hash
        new_hash = "$2b$12$8f0QVzCUAl4qwj8w1t7iMeD9prXxEZ6.nokFBxRKRnEU.gLY84YpO"
        test_user.password_hash = new_hash

        db.commit()

        print(f"✅ Updated test user password hash")
        print(f"   Email: {test_user.email}")
        print(f"   Old hash: {old_hash[:20]}...")
        print(f"   New hash: {new_hash[:20]}...")
        print(f"\n✅ Test user can now login with:")
        print(f"   Email: test@example.com")
        print(f"   Password: testpassword123")

    except Exception as e:
        db.rollback()
        print(f"❌ Error fixing password: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_test_user_password()
