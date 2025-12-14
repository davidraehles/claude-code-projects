# Backend Scripts

Utility scripts for database seeding, testing, and maintenance.

## Test User Management

### Automatic Seeding on Startup

The application can automatically seed a test user on startup by setting the `SEED_TEST_USER` environment variable:

```bash
# Enable test user seeding
export SEED_TEST_USER=true

# Or set in Railway/Vercel
SEED_TEST_USER=true
```

**Test User Credentials:**
- Email: `test@example.com`
- Password: `testpassword123`
- Country: `US`

This is enabled automatically in development and can be enabled in production for testing environments.

### Manual Seeding

You can also manually run the seed script:

```bash
python scripts/seed_test_user.py
```

This script will:
- Create the test user if it doesn't exist
- Update the password if the user already exists
- Ensure the account is active (not soft-deleted)

## Other Scripts

- `seed_test_data.py` - Seeds recipes and meal plans for testing
- `seed_ingredients.py` - Seeds ingredient database
- `fix_test_user_password.py` - Resets test user password
- `test_waitlist_flow.py` - Tests waitlist functionality
- `verify_api_endpoints.py` - Verifies API health
- `verify_db_config.py` - Checks database configuration

## Environment Variables

- `SEED_TEST_USER` - Set to `true`, `1`, or `yes` to enable automatic test user seeding
- `APP_ENV` - Set to `development` or `production`
- `DATABASE_URL` - PostgreSQL connection string

## Usage in CI/CD

Add to your Railway or Vercel environment variables:

```env
SEED_TEST_USER=true
```

This ensures the test user is always available for integration tests and manual testing.
