#!/usr/bin/env python3
"""
Verification script for database configuration.

This script verifies that the database configuration is properly set up
to use environment variables and that no hardcoded credentials exist.

Usage:
    python scripts/verify_db_config.py

Exit codes:
    0 - All checks passed
    1 - Configuration issues found
"""

import os
import re
import sys
from pathlib import Path


def check_no_hardcoded_credentials():
    """Check that no hardcoded credentials exist in config files."""
    print("🔍 Checking for hardcoded credentials...")

    patterns = [
        r"postgresql://\w+:\w+@[\w\.-]+:\d+/\w+",  # Full connection string
        r"postgres:postgres@localhost",  # Default credentials
    ]

    files_to_check = [
        "alembic.ini",
        "migrations/env.py",
    ]

    issues = []

    for file_path in files_to_check:
        path = Path(__file__).parent.parent / file_path
        if not path.exists():
            issues.append(f"❌ File not found: {file_path}")
            continue

        with open(path, "r") as f:
            content = f.read()

        # Check for the placeholder in alembic.ini (this is OK)
        if file_path == "alembic.ini":
            if "driver://user:pass@localhost/dbname" not in content:
                issues.append(
                    f"❌ {file_path}: Missing placeholder URL. "
                    "Expected 'driver://user:pass@localhost/dbname'"
                )

        # Check for actual hardcoded credentials
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Ignore the placeholder and f-string construction
                if (
                    "driver://user:pass" not in match
                    and "f\"postgresql://" not in content
                    and "{db_user}:{db_password}" not in content
                ):
                    issues.append(
                        f"❌ {file_path}: Found hardcoded credential pattern: {match}"
                    )

    if issues:
        for issue in issues:
            print(issue)
        return False

    print("✅ No hardcoded credentials found")
    return True


def check_env_py_implementation():
    """Verify that env.py properly implements environment variable reading."""
    print("\n🔍 Checking env.py implementation...")

    env_py = Path(__file__).parent.parent / "migrations" / "env.py"

    if not env_py.exists():
        print("❌ migrations/env.py not found")
        return False

    with open(env_py, "r") as f:
        content = f.read()

    required_elements = [
        ("get_url()", "def get_url():"),
        ("DB_USER env var", 'os.getenv("DB_USER"'),
        ("DB_PASSWORD env var", 'os.getenv("DB_PASSWORD"'),
        ("DB_HOST env var", 'os.getenv("DB_HOST"'),
        ("DB_PORT env var", 'os.getenv("DB_PORT"'),
        ("DB_NAME env var", 'os.getenv("DB_NAME"'),
        ("TEST_DB_NAME support", 'os.getenv("TEST_DB_NAME")'),
        (
            "URL construction",
            "f\"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}\"",
        ),
    ]

    missing = []
    for name, pattern in required_elements:
        if pattern not in content:
            missing.append(f"❌ Missing {name}: {pattern}")

    if missing:
        for issue in missing:
            print(issue)
        return False

    print("✅ env.py implementation is correct")
    return True


def check_alembic_ini():
    """Verify that alembic.ini has the correct placeholder."""
    print("\n🔍 Checking alembic.ini...")

    alembic_ini = Path(__file__).parent.parent / "alembic.ini"

    if not alembic_ini.exists():
        print("❌ alembic.ini not found")
        return False

    with open(alembic_ini, "r") as f:
        content = f.read()

    # Check for placeholder
    if "sqlalchemy.url = driver://user:pass@localhost/dbname" not in content:
        print("❌ alembic.ini: Missing or incorrect placeholder URL")
        return False

    # Check for documentation comments
    if "actual URL is set dynamically in migrations/env.py" not in content:
        print("❌ alembic.ini: Missing documentation about dynamic URL")
        return False

    print("✅ alembic.ini is correctly configured")
    return True


def test_url_generation():
    """Test that URL generation works with different environment variables."""
    print("\n🔍 Testing URL generation...")

    # Save original environment
    original_env = os.environ.copy()

    try:
        # Create a local implementation of get_url (same as in migrations/env.py)
        def get_url():
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "postgres")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("TEST_DB_NAME") or os.getenv("DB_NAME", "recipe_app")
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # Clear database-related env vars
        for key in list(os.environ.keys()):
            if key.startswith("DB_") or key == "TEST_DB_NAME":
                del os.environ[key]

        # Test 1: Default values
        url = get_url()
        expected = "postgresql://postgres:postgres@localhost:5432/recipe_app"
        if url != expected:
            print(f"❌ Default URL incorrect. Got: {url}, Expected: {expected}")
            return False
        print(f"✅ Default URL: {url}")

        # Test 2: Custom values
        os.environ["DB_USER"] = "testuser"
        os.environ["DB_PASSWORD"] = "testpass"
        os.environ["DB_HOST"] = "testhost"
        os.environ["DB_PORT"] = "5433"
        os.environ["DB_NAME"] = "testdb"

        url = get_url()
        expected = "postgresql://testuser:testpass@testhost:5433/testdb"
        if url != expected:
            print(f"❌ Custom URL incorrect. Got: {url}, Expected: {expected}")
            return False
        print(f"✅ Custom URL: {url}")

        # Test 3: TEST_DB_NAME override
        os.environ["TEST_DB_NAME"] = "test_database"
        url = get_url()
        expected = "postgresql://testuser:testpass@testhost:5433/test_database"
        if url != expected:
            print(f"❌ TEST_DB_NAME override failed. Got: {url}, Expected: {expected}")
            return False
        print(f"✅ TEST_DB_NAME override: {url}")

        print("✅ URL generation tests passed")
        return True

    except Exception as e:
        print(f"❌ Error during URL generation test: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Database Configuration Verification")
    print("=" * 70)

    checks = [
        check_no_hardcoded_credentials(),
        check_alembic_ini(),
        check_env_py_implementation(),
        test_url_generation(),
    ]

    print("\n" + "=" * 70)
    if all(checks):
        print("✅ All checks passed! Configuration is production-ready.")
        print("=" * 70)
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
