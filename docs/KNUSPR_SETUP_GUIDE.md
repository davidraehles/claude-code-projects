# Knuspr Integration Setup Guide

Complete guide to setting up Knuspr credential management and grocery cart ordering.

## Overview

The Knuspr integration allows users to:
1. Securely store their Knuspr account credentials in the app
2. Automatically search for recipes' ingredients on Knuspr
3. Create shopping carts with optimized delivery slots
4. Place orders directly from meal plans

## Architecture

```
User Browser
    ↓
Frontend (Vercel)
  ├─ KnusprSetupModal: User enters credentials
  ├─ KnusprSettings: View/manage credentials
  └─ API calls to backend
    ↓
Backend (Railway)
  ├─ /api/v1/knuspr-credentials: Credential CRUD
  ├─ CredentialManager: Encryption/decryption
  ├─ KnusprMCPClient: Knuspr API wrapper
  ├─ CartOptimizerAgent: Orchestrates ordering
  └─ Database: Encrypted credential storage
    ↓
Knuspr API (MCP Tool)
  ├─ Product search
  ├─ Cart creation
  └─ Delivery slot management
```

## Setup Steps

### 1. Database Migration

Create the `knuspr_credentials` table in PostgreSQL:

```bash
# Using Alembic (recommended for production)
alembic revision --autogenerate -m "Add knuspr_credentials table"
alembic upgrade head

# Or manually run the migration
psql -U postgres -d recipe_db << EOF
CREATE TABLE knuspr_credentials (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    knuspr_email VARCHAR(255) NOT NULL,
    knuspr_password VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL DEFAULT 'cz',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_verified_at TIMESTAMP NULL,
    verification_error VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_knuspr_credentials_user_id (user_id),
    INDEX idx_knuspr_credentials_is_active (is_active),
    INDEX idx_knuspr_credentials_user_active (user_id, is_active)
);
EOF
```

### 2. Environment Configuration

Add encryption key to `.env` (production):

```bash
# Generate encryption key (one time, save securely)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
KNUSPR_ENCRYPTION_KEY=your-generated-key-here
```

For development, the system auto-generates a key if not provided.

### 3. Backend API Integration

The API endpoints are automatically registered:

```
POST   /api/v1/knuspr-credentials
  Save/update user's Knuspr credentials

  Request:
  {
    "knuspr_email": "user@knuspr.cz",
    "knuspr_password": "password123",
    "country": "cz",
    "test_connection": true
  }

  Response: 201 Created
  {
    "has_credentials": true,
    "is_active": true,
    "country": "cz",
    "knuspr_email": "u***@knuspr.cz",
    "last_verified_at": "2025-11-18T12:00:00"
  }

GET    /api/v1/knuspr-credentials
  Get credential status (no password)

  Response: 200 OK
  {
    "has_credentials": true,
    "is_active": true,
    "country": "cz",
    "knuspr_email": "u***@knuspr.cz"
  }

POST   /api/v1/knuspr-credentials/verify
  Test credentials with Knuspr API

  Response: 200 OK
  {
    "is_valid": true,
    "message": "Knuspr credentials verified successfully",
    "last_verified_at": "2025-11-18T12:00:00"
  }

DELETE /api/v1/knuspr-credentials
  Remove/deactivate credentials (soft delete)

  Response: 200 OK
  {
    "message": "Knuspr credentials deleted successfully",
    "success": true
  }
```

### 4. Frontend Components Integration

The components are ready to use. Add them to your settings/preferences page:

```tsx
import { KnusprSettings } from '@/components/knuspr/KnusprSettings';

export default function SettingsPage() {
  return (
    <div className="p-6">
      <KnusprSettings />
    </div>
  );
}
```

The component includes:
- Connection status display
- Credential setup modal
- Verification testing
- Secure removal

### 5. MCP Tool Setup (When Available)

Once Knuspr MCP tool is available, uncomment the actual API calls in:

**File**: `app/services/knuspr_mcp_client.py`

```python
# Replace mock implementations with actual MCP calls
# TODO: Call MCP tool to search products
client = MCPClient()
response = await client.search_products({
    "query": ingredient_name,
    "country": self.country.value,
    "max_results": max_results,
    "exact_match": exact_match,
    "session_token": self.session_token
})
```

**File**: `app/services/credential_manager.py`

```python
# Implement actual Knuspr authentication
client = KnusprMCPClient(
    login_email=email,
    login_password=password,
    country=country
)
success = await client.authenticate()
```

## User Flow

### Adding Knuspr Credentials

1. User navigates to Settings/Preferences
2. Clicks "Connect Knuspr Account"
3. Modal opens with form:
   - Country dropdown (CZ, SK, PL)
   - Email/phone input
   - Password input
   - Optional: Test connection checkbox
4. User submits credentials
5. Backend:
   - Validates inputs
   - Optionally tests with Knuspr API
   - Encrypts credentials
   - Stores in database
   - Returns masked status
6. Frontend displays connection status
7. User can now create shopping carts from meal plans

### Creating a Shopping Cart

1. User selects a meal plan
2. Clicks "Order Groceries"
3. System checks: User has Knuspr credentials?
   - If no → Prompt to add credentials
   - If yes → Continue
4. Cart optimizer:
   - Extracts ingredients from meal plan
   - Fetches user's Knuspr credentials
   - Searches Knuspr for products
   - Creates shopping cart
   - Fetches available delivery slots
   - Selects optimal slot
5. Frontend displays cart with:
   - Items grouped by section (produce, dairy, etc.)
   - Unavailable items with suggestions
   - Delivery slot options
   - Total price
   - "Proceed to Checkout" button
6. User reviews and clicks checkout
7. Cart sent to Knuspr for final order

## Security Considerations

### Data Protection

✅ **Encryption at Rest**
- Credentials encrypted with Fernet (symmetric encryption)
- Encryption key stored in environment variable
- Key never exposed in logs or responses

✅ **In Transit**
- HTTPS only in production
- JWT tokens for authentication
- Credentials never logged

✅ **API Responses**
- Passwords never included in any response
- Emails masked (u***@example.com)
- Only status/metadata returned

✅ **Database**
- Soft delete for GDPR compliance
- No permanent deletion
- Audit trail possible via `updated_at`

### Encryption Key Management

```bash
# Generate and secure key (one time)
python -c "from cryptography.fernet import Fernet; key = Fernet.generate_key().decode(); print(f'KNUSPR_ENCRYPTION_KEY={key}')"

# Store in:
# - Docker secrets (production)
# - GitHub encrypted secrets (CI/CD)
# - HashiCorp Vault (enterprise)
# - AWS KMS (AWS deployments)

# Never commit to git:
# Verify .env* files are in .gitignore
git check-ignore .env .env.local .env.*.local
```

### Credential Validation

Before using credentials, always verify:

```python
# In API endpoint
credential = await credential_manager.get_credentials(db, user_id)
if not credential:
    raise HTTPException(status_code=400, detail="Please add Knuspr credentials")

# Optionally verify with Knuspr API
is_valid = await credential_manager.verify_credentials(db, user_id)
if not is_valid:
    raise HTTPException(status_code=400, detail="Knuspr credentials are invalid")
```

## Testing

### Manual Testing

```bash
# 1. Register test user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","country":"cz"}'

# 2. Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | jq -r '.access_token')

# 3. Save credentials
curl -X POST http://localhost:8000/api/v1/knuspr-credentials \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "knuspr_email":"user@knuspr.cz",
    "knuspr_password":"password123",
    "country":"cz",
    "test_connection":false
  }'

# 4. Get status
curl -X GET http://localhost:8000/api/v1/knuspr-credentials \
  -H "Authorization: Bearer $TOKEN"

# 5. Verify credentials
curl -X POST http://localhost:8000/api/v1/knuspr-credentials/verify \
  -H "Authorization: Bearer $TOKEN"

# 6. Delete credentials
curl -X DELETE http://localhost:8000/api/v1/knuspr-credentials \
  -H "Authorization: Bearer $TOKEN"
```

### E2E Tests

Run Playwright tests:

```bash
# Install dependencies (first time)
npm install

# Run credential management tests
npx playwright test e2e/knuspr-credentials.spec.ts

# Run with UI
npx playwright test e2e/knuspr-credentials.spec.ts --ui

# Run specific test
npx playwright test e2e/knuspr-credentials.spec.ts -g "should add Knuspr"

# Run with trace
npx playwright test e2e/knuspr-credentials.spec.ts --trace on
```

### Unit Tests (Python)

```bash
# Test credential manager encryption
pytest app/services/test_credential_manager.py -v

# Test API endpoints
pytest app/api/v1/test_knuspr_credentials.py -v

# Test with coverage
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Issue: "Invalid Knuspr credentials"

**Cause**: Wrong email/password or Knuspr API unreachable

**Solution**:
1. Verify credentials work on Knuspr website
2. Check network connectivity to Knuspr API
3. Try disabling "test_connection" and verify manually later
4. Check server logs for detailed error

### Issue: "Failed to decrypt credentials"

**Cause**: Encryption key changed or corrupted

**Solution**:
1. Verify `KNUSPR_ENCRYPTION_KEY` hasn't changed
2. Check database for corrupted data
3. Re-save credentials with current key
4. Clear credentials cache in browser

### Issue: Credentials not persisting

**Cause**: Database migration not applied

**Solution**:
1. Run database migrations: `alembic upgrade head`
2. Verify `knuspr_credentials` table exists: `\dt knuspr_credentials`
3. Check table permissions: `\dp knuspr_credentials`

### Issue: CORS errors when saving credentials

**Cause**: Frontend and backend on different domains

**Solution**:
1. Check `CORS_ORIGINS` in backend `.env`
2. Add frontend URL to allowed origins
3. Verify credentials are sent with `Authorization` header
4. Check browser console for detailed error

## Production Deployment

### Pre-deployment Checklist

- [ ] Database migrations applied
- [ ] Encryption key generated and stored in vault
- [ ] CORS origins configured
- [ ] HTTPS enforced
- [ ] Logging configured (no credential leaks)
- [ ] E2E tests passing
- [ ] Load testing completed
- [ ] Security audit completed

### Deployment Steps

1. **Backend** (Railway):
   ```bash
   # Update app with new code
   git push origin main

   # Railway auto-deploys
   # Verify in Rails dashboard

   # Run migrations
   railway run alembic upgrade head
   ```

2. **Frontend** (Vercel):
   ```bash
   # Push code to main branch
   git push origin main

   # Vercel auto-deploys
   # Verify in Vercel dashboard
   ```

3. **Verify Deployment**:
   ```bash
   # Test credential API
   curl https://api.example.com/api/v1/knuspr-credentials \
     -H "Authorization: Bearer $TOKEN"

   # Check logs for errors
   railway logs
   ```

## API Documentation

Full API docs available at:
- Swagger UI: `https://api.example.com/api/docs`
- ReDoc: `https://api.example.com/api/redoc`

Search for "knuspr-credentials" endpoint in docs.

## Related Documentation

- [Knuspr MCP Client](./KNUSPR_MCP_CLIENT.md) - Knuspr API wrapper
- [Cart Optimizer Agent](./CART_OPTIMIZER_AGENT.md) - Meal plan → shopping cart
- [Ingredient Mapper](./INGREDIENT_MAPPER.md) - Recipe ingredient matching
- [Authentication](./AUTHENTICATION.md) - User auth system

## Support

For issues or questions:
1. Check logs: `railway logs` or browser console
2. Run E2E tests: `npx playwright test`
3. Check API docs: `/api/docs`
4. Open GitHub issue with detailed error message
