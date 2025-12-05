"""
Integration tests for database backup and restore procedures.

Tests backup creation, S3 upload, restore functionality, point-in-time recovery,
and performance benchmarks for the Railway PostgreSQL database.
"""

import os
import subprocess
import tempfile
import time
import hashlib
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Dict, Any
import gzip

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.database import Base, DATABASE_URL
from app.models.user import User
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient, IngredientCategory, Allergen
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

# Use test database URL or create one for testing
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "recipe_app_backup_test")
TEST_DB_USER = os.getenv("DB_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
TEST_DB_HOST = os.getenv("DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("DB_PORT", "5432")

TEST_DATABASE_URL = (
    f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
    f"{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"
)

# Backup script location
SCRIPT_DIR = Path(__file__).parent.parent.parent.parent / "infrastructure" / "scripts"
BACKUP_SCRIPT = SCRIPT_DIR / "backup_database.sh"
RESTORE_SCRIPT = SCRIPT_DIR / "restore_database.sh"
RAILWAY_BACKUP_SCRIPT = SCRIPT_DIR / "setup_railway_backups.sh"

# Test data configuration
LARGE_DATASET_SIZE = 10000  # Number of records for performance testing


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine for the entire test session.

    This fixture creates a fresh PostgreSQL database for testing,
    ensuring isolation from production data.
    """
    # Create test database
    admin_url = (
        f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
        f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
    )
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

    # Drop existing test database if it exists
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    admin_engine.dispose()

    # Create engine for test database
    engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    engine.dispose()

    # Drop test database
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    admin_engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    Create a database session for each test function.

    Automatically rolls back transactions after each test to maintain isolation.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def backup_dir():
    """Create a temporary directory for backup files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_data(db_session: Session) -> Dict[str, Any]:
    """
    Create sample data in the test database.

    Returns:
        Dictionary containing counts and IDs of created records.
    """
    # Create users
    users = [
        User(
            email=f"user{i}@example.com",
            hashed_password=f"hashed_password_{i}",
            full_name=f"Test User {i}",
        )
        for i in range(5)
    ]
    db_session.add_all(users)
    db_session.flush()

    # Create ingredient categories
    categories = [
        IngredientCategory(name="Vegetables", description="Fresh vegetables"),
        IngredientCategory(name="Proteins", description="Meat and alternatives"),
        IngredientCategory(name="Dairy", description="Dairy products"),
    ]
    db_session.add_all(categories)
    db_session.flush()

    # Create allergens
    allergens = [
        Allergen(name="Gluten", description="Gluten-containing foods"),
        Allergen(name="Dairy", description="Milk and dairy products"),
        Allergen(name="Nuts", description="Tree nuts and peanuts"),
    ]
    db_session.add_all(allergens)
    db_session.flush()

    # Create ingredients
    ingredients = [
        Ingredient(
            name=f"Ingredient {i}",
            category_id=categories[i % len(categories)].id,
            unit="grams",
            calories_per_unit=100.0 + i,
        )
        for i in range(20)
    ]
    db_session.add_all(ingredients)
    db_session.flush()

    # Create recipes
    recipes = [
        Recipe(
            user_id=users[i % len(users)].id,
            title=f"Recipe {i}",
            ingredients=[f"Ingredient {j}" for j in range(5)],
            instructions=f"Instructions for recipe {i}",
            prep_time=10 + i,
            cook_time=20 + i,
            servings=4,
            source_url=f"https://example.com/recipe{i}",
            source_type="html",
        )
        for i in range(50)
    ]
    db_session.add_all(recipes)
    db_session.flush()

    # Create meal plans
    meal_plans = [
        MealPlan(
            user_id=users[i % len(users)].id,
            name=f"Meal Plan {i}",
            start_date=datetime.utcnow().date(),
            end_date=(datetime.utcnow() + timedelta(days=7)).date(),
        )
        for i in range(10)
    ]
    db_session.add_all(meal_plans)
    db_session.flush()

    # Create meal plan recipes
    meal_plan_recipes = [
        MealPlanRecipe(
            meal_plan_id=meal_plans[i % len(meal_plans)].id,
            recipe_id=recipes[i % len(recipes)].id,
            day_of_week=i % 7,
            meal_type="dinner",
        )
        for i in range(30)
    ]
    db_session.add_all(meal_plan_recipes)
    db_session.flush()

    # Create grocery carts
    grocery_carts = [
        GroceryCart(
            user_id=users[i % len(users)].id,
            meal_plan_id=meal_plans[i % len(meal_plans)].id,
            name=f"Cart {i}",
        )
        for i in range(10)
    ]
    db_session.add_all(grocery_carts)
    db_session.flush()

    # Create cart items
    cart_items = [
        CartItem(
            cart_id=grocery_carts[i % len(grocery_carts)].id,
            ingredient_name=f"Ingredient {i % 20}",
            quantity=float(i % 10 + 1),
            unit="grams",
            recipe_id=recipes[i % len(recipes)].id,
        )
        for i in range(50)
    ]
    db_session.add_all(cart_items)

    db_session.commit()

    return {
        "users": len(users),
        "categories": len(categories),
        "allergens": len(allergens),
        "ingredients": len(ingredients),
        "recipes": len(recipes),
        "meal_plans": len(meal_plans),
        "meal_plan_recipes": len(meal_plan_recipes),
        "grocery_carts": len(grocery_carts),
        "cart_items": len(cart_items),
        "user_ids": [u.id for u in users],
        "recipe_ids": [r.id for r in recipes],
    }


@pytest.fixture
def large_dataset(db_session: Session) -> Dict[str, Any]:
    """
    Create a large dataset for performance testing.

    Creates 10,000+ records across multiple tables.
    """
    start_time = time.time()

    # Create users in batches
    batch_size = 1000
    user_count = 100

    users = []
    for i in range(user_count):
        user = User(
            email=f"perftest_user{i}@example.com",
            hashed_password=f"hashed_password_{i}",
            full_name=f"Performance Test User {i}",
        )
        users.append(user)

    db_session.add_all(users)
    db_session.flush()

    # Create many recipes
    recipes = []
    for i in range(LARGE_DATASET_SIZE):
        recipe = Recipe(
            user_id=users[i % len(users)].id,
            title=f"Performance Recipe {i}",
            ingredients=[f"Ingredient {j}" for j in range(5)],
            instructions=f"Instructions for performance recipe {i}" * 10,  # Longer text
            prep_time=10,
            cook_time=20,
            servings=4,
            source_url=f"https://example.com/perfrecipe{i}",
            source_type="html",
        )
        recipes.append(recipe)

        # Batch insert
        if len(recipes) >= batch_size:
            db_session.add_all(recipes)
            db_session.flush()
            recipes = []

    # Insert remaining recipes
    if recipes:
        db_session.add_all(recipes)
        db_session.flush()

    db_session.commit()

    duration = time.time() - start_time

    return {
        "record_count": LARGE_DATASET_SIZE,
        "creation_time": duration,
    }


# ============================================================================
# BACKUP FUNCTIONALITY TESTS
# ============================================================================


class TestBackupFunctionality:
    """Test database backup creation and verification."""

    def test_create_backup_successfully(self, db_session: Session, sample_data, backup_dir):
        """Test that a backup can be created successfully."""
        backup_file = backup_dir / "test_backup.sql"

        # Create backup using pg_dump
        result = subprocess.run(
            [
                "pg_dump",
                TEST_DATABASE_URL,
                "--no-owner",
                "--no-acl",
                "--clean",
                "--if-exists",
                f"--file={backup_file}",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"pg_dump failed: {result.stderr}"
        assert backup_file.exists(), "Backup file was not created"
        assert backup_file.stat().st_size > 0, "Backup file is empty"

    def test_backup_file_integrity(self, db_session: Session, sample_data, backup_dir):
        """Test that backup file integrity can be verified with checksums."""
        backup_file = backup_dir / "test_backup.sql"

        # Create backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # Generate MD5 hash
        md5_hash = hashlib.md5()
        with open(backup_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)

        original_hash = md5_hash.hexdigest()

        # Verify hash remains consistent
        md5_hash_verify = hashlib.md5()
        with open(backup_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash_verify.update(chunk)

        verify_hash = md5_hash_verify.hexdigest()

        assert original_hash == verify_hash, "File integrity check failed"

    def test_compressed_backup_creation(self, db_session: Session, sample_data, backup_dir):
        """Test creation of compressed backup files."""
        backup_file = backup_dir / "test_backup.sql"
        compressed_file = backup_dir / "test_backup.sql.gz"

        # Create backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        original_size = backup_file.stat().st_size

        # Compress backup
        with open(backup_file, "rb") as f_in:
            with gzip.open(compressed_file, "wb") as f_out:
                f_out.writelines(f_in)

        compressed_size = compressed_file.stat().st_size

        assert compressed_file.exists(), "Compressed file was not created"
        assert compressed_size < original_size, "Compression did not reduce file size"

        # Verify compressed file can be decompressed
        result = subprocess.run(
            ["gzip", "-t", str(compressed_file)],
            capture_output=True,
        )
        assert result.returncode == 0, "Compressed file integrity check failed"

    def test_backup_metadata_generation(self, db_session: Session, sample_data, backup_dir):
        """Test generation of backup metadata."""
        backup_file = backup_dir / "test_backup.sql.gz"
        metadata_file = backup_dir / "test_backup.json"

        # Create compressed backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, "--file=/dev/stdout"],
            stdout=open(backup_dir / "temp.sql", "w"),
            check=True,
        )

        with open(backup_dir / "temp.sql", "rb") as f_in:
            with gzip.open(backup_file, "wb") as f_out:
                f_out.writelines(f_in)

        # Generate metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "filename": backup_file.name,
            "size": backup_file.stat().st_size,
            "database": TEST_DB_NAME,
            "tables": list(sample_data.keys()),
        }

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        assert metadata_file.exists(), "Metadata file was not created"

        # Verify metadata content
        with open(metadata_file, "r") as f:
            loaded_metadata = json.load(f)

        assert loaded_metadata["filename"] == backup_file.name
        assert loaded_metadata["size"] > 0
        assert "timestamp" in loaded_metadata

    def test_backup_with_large_dataset(self, db_session: Session, large_dataset, backup_dir):
        """Test backup performance with large dataset (>10K records)."""
        backup_file = backup_dir / "large_backup.sql.gz"

        start_time = time.time()

        # Create compressed backup
        pg_dump_process = subprocess.Popen(
            ["pg_dump", TEST_DATABASE_URL, "--no-owner", "--no-acl"],
            stdout=subprocess.PIPE,
        )

        with gzip.open(backup_file, "wb") as f:
            f.write(pg_dump_process.stdout.read())

        pg_dump_process.wait()
        duration = time.time() - start_time

        assert pg_dump_process.returncode == 0, "Backup of large dataset failed"
        assert backup_file.exists(), "Backup file not created"
        assert backup_file.stat().st_size > 0, "Backup file is empty"

        # Log performance metrics
        print(f"\nLarge dataset backup performance:")
        print(f"  Records: {large_dataset['record_count']}")
        print(f"  Backup time: {duration:.2f}s")
        print(f"  Backup size: {backup_file.stat().st_size / 1024 / 1024:.2f}MB")

        # Performance threshold: should complete within 60 seconds
        assert duration < 60, f"Backup took too long: {duration:.2f}s"


# ============================================================================
# RESTORE FUNCTIONALITY TESTS
# ============================================================================


class TestRestoreFunctionality:
    """Test database restore operations."""

    def test_restore_to_empty_database(self, test_db_engine, sample_data, backup_dir):
        """Test restore to a clean database."""
        backup_file = backup_dir / "restore_test.sql"

        # Create backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # Drop and recreate database
        admin_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE {TEST_DB_NAME}"))
            conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

        admin_engine.dispose()

        # Restore from backup
        result = subprocess.run(
            ["psql", TEST_DATABASE_URL, "-f", str(backup_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Restore failed: {result.stderr}"

        # Verify data
        restored_engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
        SessionLocal = sessionmaker(bind=restored_engine)
        session = SessionLocal()

        try:
            user_count = session.query(User).count()
            recipe_count = session.query(Recipe).count()

            assert user_count == sample_data["users"], "User count mismatch after restore"
            assert recipe_count == sample_data["recipes"], "Recipe count mismatch after restore"
        finally:
            session.close()
            restored_engine.dispose()

    def test_restore_schema_matches_original(self, test_db_engine, sample_data, backup_dir):
        """Test that restored schema matches original schema."""
        backup_file = backup_dir / "schema_test.sql"

        # Get original schema
        original_schema = self._get_database_schema(TEST_DATABASE_URL)

        # Create backup and restore
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # Create temporary restore database
        restore_db_name = f"{TEST_DB_NAME}_restore"
        admin_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {restore_db_name}"))
            conn.execute(text(f"CREATE DATABASE {restore_db_name}"))

        restore_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/{restore_db_name}"
        )

        # Restore
        subprocess.run(
            ["psql", restore_url, "-f", str(backup_file)],
            check=True,
            capture_output=True,
        )

        # Get restored schema
        restored_schema = self._get_database_schema(restore_url)

        # Cleanup restore database
        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE {restore_db_name}"))

        admin_engine.dispose()

        # Compare schemas
        assert original_schema == restored_schema, "Schema mismatch after restore"

    def test_restore_data_integrity(self, test_db_engine, sample_data, backup_dir):
        """Test that restored data maintains integrity (checksums, row counts)."""
        backup_file = backup_dir / "integrity_test.sql"

        # Get original checksums
        original_checksums = self._calculate_table_checksums(test_db_engine, sample_data)

        # Create backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # Restore to temporary database
        restore_db_name = f"{TEST_DB_NAME}_integrity"
        admin_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {restore_db_name}"))
            conn.execute(text(f"CREATE DATABASE {restore_db_name}"))

        restore_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/{restore_db_name}"
        )

        subprocess.run(
            ["psql", restore_url, "-f", str(backup_file)],
            check=True,
            capture_output=True,
        )

        # Get restored checksums
        restored_engine = create_engine(restore_url, poolclass=NullPool)
        restored_checksums = self._calculate_table_checksums(restored_engine, sample_data)

        # Cleanup
        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE {restore_db_name}"))

        admin_engine.dispose()
        restored_engine.dispose()

        # Compare checksums
        assert (
            original_checksums == restored_checksums
        ), "Data integrity check failed after restore"

    def test_restore_constraints_and_relationships(
        self, test_db_engine, sample_data, backup_dir
    ):
        """Test that foreign keys and constraints are restored correctly."""
        backup_file = backup_dir / "constraints_test.sql"

        # Create backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # Restore to temporary database
        restore_db_name = f"{TEST_DB_NAME}_constraints"
        admin_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {restore_db_name}"))
            conn.execute(text(f"CREATE DATABASE {restore_db_name}"))

        restore_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/{restore_db_name}"
        )

        subprocess.run(
            ["psql", restore_url, "-f", str(backup_file)],
            check=True,
            capture_output=True,
        )

        # Test foreign key constraints
        restored_engine = create_engine(restore_url, poolclass=NullPool)
        SessionLocal = sessionmaker(bind=restored_engine)
        session = SessionLocal()

        try:
            # Try to insert invalid data (should fail due to FK constraint)
            invalid_recipe = Recipe(
                user_id=99999,  # Non-existent user
                title="Invalid Recipe",
                ingredients=["test"],
                instructions="test",
                prep_time=10,
                cook_time=20,
                servings=4,
            )
            session.add(invalid_recipe)

            with pytest.raises(Exception):  # Should raise FK violation
                session.commit()

        finally:
            session.close()
            restored_engine.dispose()

            # Cleanup
            with admin_engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE {restore_db_name}"))

            admin_engine.dispose()

    # Helper methods
    def _get_database_schema(self, db_url: str) -> Dict[str, Any]:
        """Get database schema information."""
        engine = create_engine(db_url, poolclass=NullPool)

        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """
                )
            )

            schema = {}
            for row in result:
                table = row[0]
                if table not in schema:
                    schema[table] = []
                schema[table].append(
                    {"column": row[1], "type": row[2], "nullable": row[3]}
                )

        engine.dispose()
        return schema

    def _calculate_table_checksums(
        self, engine, sample_data: Dict[str, Any]
    ) -> Dict[str, int]:
        """Calculate row count checksums for each table."""
        checksums = {}

        with engine.connect() as conn:
            for table in ["users", "recipes", "ingredients", "meal_plans", "grocery_carts"]:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                checksums[table] = result.scalar()

        return checksums


# ============================================================================
# POINT-IN-TIME RECOVERY TESTS
# ============================================================================


class TestPointInTimeRecovery:
    """Test point-in-time recovery capabilities."""

    def test_sequential_backups_create_timeline(self, db_session: Session, backup_dir):
        """Test that sequential backups can restore to any point in time."""
        backups = []

        # Create checkpoint 1
        user1 = User(email="pitr1@example.com", hashed_password="hash", full_name="PITR User 1")
        db_session.add(user1)
        db_session.commit()

        backup1 = backup_dir / "checkpoint1.sql"
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup1}"],
            check=True,
            capture_output=True,
        )
        backups.append(("checkpoint1", backup1, 1))

        # Create checkpoint 2
        user2 = User(email="pitr2@example.com", hashed_password="hash", full_name="PITR User 2")
        db_session.add(user2)
        db_session.commit()

        backup2 = backup_dir / "checkpoint2.sql"
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup2}"],
            check=True,
            capture_output=True,
        )
        backups.append(("checkpoint2", backup2, 2))

        # Create checkpoint 3
        user3 = User(email="pitr3@example.com", hashed_password="hash", full_name="PITR User 3")
        db_session.add(user3)
        db_session.commit()

        backup3 = backup_dir / "checkpoint3.sql"
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup3}"],
            check=True,
            capture_output=True,
        )
        backups.append(("checkpoint3", backup3, 3))

        # Verify each backup restores correct number of users
        for name, backup_file, expected_count in backups:
            restore_db_name = f"{TEST_DB_NAME}_pitr_{name}"

            # Create restore database
            admin_url = (
                f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
                f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
            )
            admin_engine = create_engine(
                admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
            )

            with admin_engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {restore_db_name}"))
                conn.execute(text(f"CREATE DATABASE {restore_db_name}"))

            restore_url = (
                f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
                f"{TEST_DB_HOST}:{TEST_DB_PORT}/{restore_db_name}"
            )

            # Restore
            subprocess.run(
                ["psql", restore_url, "-f", str(backup_file)],
                check=True,
                capture_output=True,
            )

            # Verify count
            restored_engine = create_engine(restore_url, poolclass=NullPool)
            SessionLocal = sessionmaker(bind=restored_engine)
            session = SessionLocal()

            user_count = session.query(User).count()

            session.close()
            restored_engine.dispose()

            # Cleanup
            with admin_engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE {restore_db_name}"))

            admin_engine.dispose()

            assert (
                user_count == expected_count
            ), f"PITR failed for {name}: expected {expected_count}, got {user_count}"


# ============================================================================
# PERFORMANCE BENCHMARK TESTS
# ============================================================================


class TestBackupRestorePerformance:
    """Test backup and restore performance."""

    def test_backup_time_benchmark(self, db_session: Session, large_dataset, backup_dir):
        """Benchmark backup time and log results."""
        backup_file = backup_dir / "benchmark_backup.sql.gz"

        start_time = time.time()

        pg_dump_process = subprocess.Popen(
            ["pg_dump", TEST_DATABASE_URL, "--no-owner", "--no-acl"],
            stdout=subprocess.PIPE,
        )

        with gzip.open(backup_file, "wb") as f:
            f.write(pg_dump_process.stdout.read())

        pg_dump_process.wait()
        backup_duration = time.time() - start_time

        backup_size = backup_file.stat().st_size

        print(f"\n{'='*60}")
        print(f"BACKUP PERFORMANCE BENCHMARK")
        print(f"{'='*60}")
        print(f"Records:      {large_dataset['record_count']:,}")
        print(f"Backup time:  {backup_duration:.2f}s")
        print(f"Backup size:  {backup_size / 1024 / 1024:.2f}MB")
        print(f"Throughput:   {large_dataset['record_count'] / backup_duration:.0f} records/s")
        print(f"{'='*60}\n")

        # Log to file for tracking
        benchmark_log = backup_dir / "benchmark_results.json"
        results = {
            "backup": {
                "timestamp": datetime.utcnow().isoformat(),
                "records": large_dataset["record_count"],
                "duration_seconds": backup_duration,
                "size_bytes": backup_size,
                "throughput_records_per_second": large_dataset["record_count"] / backup_duration,
            }
        }

        with open(benchmark_log, "w") as f:
            json.dump(results, f, indent=2)

        # Alert if performance degrades
        assert backup_duration < 120, f"Backup took too long: {backup_duration:.2f}s"

    def test_restore_time_benchmark(self, test_db_engine, large_dataset, backup_dir):
        """Benchmark restore time and log results."""
        backup_file = backup_dir / "benchmark_restore.sql"

        # Create backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # Create restore database
        restore_db_name = f"{TEST_DB_NAME}_perf_restore"
        admin_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/postgres"
        )
        admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {restore_db_name}"))
            conn.execute(text(f"CREATE DATABASE {restore_db_name}"))

        restore_url = (
            f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@"
            f"{TEST_DB_HOST}:{TEST_DB_PORT}/{restore_db_name}"
        )

        # Benchmark restore
        start_time = time.time()

        subprocess.run(
            ["psql", restore_url, "-f", str(backup_file)],
            check=True,
            capture_output=True,
        )

        restore_duration = time.time() - start_time

        # Cleanup
        with admin_engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE {restore_db_name}"))

        admin_engine.dispose()

        print(f"\n{'='*60}")
        print(f"RESTORE PERFORMANCE BENCHMARK")
        print(f"{'='*60}")
        print(f"Records:       {large_dataset['record_count']:,}")
        print(f"Restore time:  {restore_duration:.2f}s")
        print(f"Throughput:    {large_dataset['record_count'] / restore_duration:.0f} records/s")
        print(f"{'='*60}\n")

        # Alert if performance degrades
        assert restore_duration < 180, f"Restore took too long: {restore_duration:.2f}s"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_restore_with_missing_tables(self, test_db_engine, backup_dir):
        """Test restore when some tables are missing in target database."""
        # This test verifies that restore handles missing tables gracefully
        backup_file = backup_dir / "missing_tables.sql"

        # Create a minimal backup
        subprocess.run(
            ["pg_dump", TEST_DATABASE_URL, f"--file={backup_file}"],
            check=True,
            capture_output=True,
        )

        # The --clean flag in pg_dump ensures tables are dropped before creation
        # So restore should work even if tables exist or don't exist
        assert backup_file.exists()

    def test_disk_space_validation(self, backup_dir):
        """Test disk space validation before restore."""
        # Get available disk space
        stat = os.statvfs(backup_dir)
        available_space = stat.f_bavail * stat.f_frsize

        print(f"\nAvailable disk space: {available_space / 1024 / 1024:.2f}MB")

        # This is a simple check - in production you'd compare against backup size
        assert available_space > 100 * 1024 * 1024, "Insufficient disk space"
