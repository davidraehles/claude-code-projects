# Database Migrations

This directory contains Alembic database migrations for the Multi-Agent Recipe & Meal Planning System.

## Overview

The project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema versioning and migrations. All schema changes should be managed through migrations to ensure consistency across development, staging, and production environments.

## Migration Files

Current migrations:

- **000_create_users_table.py**: Creates the `users` table with authentication and subscription fields
- **001_create_recipes_table.py**: Creates the `recipes` table with user relationships and indexing

## Setup

### 1. Configure Environment Variables

Copy `.env.example` to `.env` and configure your database connection:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=recipe_app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### View Migration History

```bash
alembic history
```

### Check Current Version

```bash
alembic current
```

### Upgrade to Latest Version

```bash
alembic upgrade head
```

### Upgrade to Specific Version

```bash
alembic upgrade 001
```

### Downgrade to Previous Version

```bash
alembic downgrade -1
```

### Downgrade to Specific Version

```bash
alembic downgrade 000
```

### Downgrade to Base (Empty Database)

```bash
alembic downgrade base
```

## Creating New Migrations

### Auto-generate Migration from Model Changes

```bash
alembic revision --autogenerate -m "Description of changes"
```

**Note**: Always review auto-generated migrations before applying them. Alembic may not detect all changes.

### Create Empty Migration

```bash
alembic revision -m "Description of changes"
```

Then edit the generated file in `migrations/versions/`.

## Migration Best Practices

1. **Always review migrations** before applying them to production
2. **Test migrations** in development/staging first
3. **Write both upgrade and downgrade** functions
4. **Keep migrations small and focused** - one logical change per migration
5. **Never edit applied migrations** - create a new migration instead
6. **Use descriptive names** for your migrations
7. **Test rollback procedures** to ensure downgrades work correctly

## Database Schema

### Users Table

Stores user accounts with authentication and subscription information:

- `id`: Primary key (BIGINT)
- `email`: User email (unique, indexed)
- `password_hash`: Bcrypt hashed password
- `country`: ISO 3166-1 alpha-2 country code
- `subscription_tier`: free | basic | premium
- `subscription_expires_at`: Subscription expiration timestamp
- `preferences`: JSONB field for user preferences
- `created_at`, `updated_at`, `deleted_at`: Timestamps

### Recipes Table

Stores harvested recipes with user ownership:

- `id`: Primary key (BIGINT)
- `user_id`: Foreign key to users (CASCADE delete)
- `title`: Recipe title
- `ingredients`: JSON array of ingredients
- `instructions`: Text instructions
- `prep_time`, `cook_time`, `servings`: Recipe metadata
- `nutrition`: JSON nutrition information
- `source_url`: Original recipe URL (unique)
- `source_type`: html | api | rss
- `duplicate_of_id`: Self-referential foreign key for duplicate detection
- `created_at`, `last_updated`: Timestamps

### Indexes

- `users.email` (unique)
- `users.subscription_expires_at`
- `recipes.user_id`
- `recipes.source_url`
- `recipes.source_type`
- `recipes.created_at`
- `recipes.duplicate_of_id`
- `recipes.title`

## Troubleshooting

### Connection Errors

If you get connection errors, verify:

1. Database is running: `pg_isready -h localhost -p 5432`
2. Environment variables are set correctly
3. Database exists: `psql -h localhost -U postgres -l | grep recipe_app`

### Create Database

If the database doesn't exist:

```bash
createdb -h localhost -U postgres recipe_app
```

Or using psql:

```sql
CREATE DATABASE recipe_app;
```

### Migration Conflicts

If you have migration conflicts or need to reset:

```bash
# Downgrade to base
alembic downgrade base

# Upgrade to latest
alembic upgrade head
```

## Environment-Specific Configuration

The `env.py` file automatically reads database configuration from environment variables, overriding the default settings in `alembic.ini`. This allows for environment-specific configuration without modifying configuration files.

**Priority**: Environment variables > alembic.ini

### Configuration Details

Database connection is configured via the following environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `recipe_app` |
| `TEST_DB_NAME` | Test database name (overrides DB_NAME) | None |

### Security Notes

1. **No Hardcoded Credentials**: The `alembic.ini` file contains only a placeholder URL (`driver://user:pass@localhost/dbname`). Actual database credentials are read from environment variables in `migrations/env.py`.

2. **Production Safety**: Always set environment variables explicitly in production. The default values are only intended for local development.

3. **Test Isolation**: Use `TEST_DB_NAME` to run tests against a separate database without affecting your development data.

### Usage Examples

#### Development (using defaults)
```bash
# Uses default values: postgres:postgres@localhost:5432/recipe_app
alembic upgrade head
```

#### Custom Configuration
```bash
# Set environment variables for custom database
export DB_USER=myuser
export DB_PASSWORD=mypassword
export DB_HOST=db.example.com
export DB_PORT=5432
export DB_NAME=mydb

alembic upgrade head
```

#### Testing
```bash
# Use a separate test database
export TEST_DB_NAME=recipe_app_test
alembic upgrade head
```

#### Production
```bash
# Set all environment variables explicitly (no defaults)
export DB_USER=prod_user
export DB_PASSWORD=secure_prod_password
export DB_HOST=prod-db.example.com
export DB_PORT=5432
export DB_NAME=production_db

alembic upgrade head
```

#### Docker Compose
The `infrastructure/docker-compose.yml` automatically passes environment variables to the API service, which runs migrations on startup:

```bash
cd infrastructure
docker compose up -d
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Project Data Model](../specs/002-multi-agent-recipe-app/data-model.md)
