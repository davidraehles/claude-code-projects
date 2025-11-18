# Bcrypt Password Hashing Fix - Root Cause & Solution

## The Problem

Password registration was failing with error:
```
"password cannot be longer than 72 bytes, truncate manually if necessary"
```

**For a 15-byte password!** ("testpassword123")

## Root Cause

The issue was NOT about password length - it was about how passlib's bcrypt was being called.

**Original code**:
```python
return bcrypt.hash(password)
```

This was calling passlib's bcrypt.hash() without explicit configuration, which was causing internal issues with how bcrypt was handling the password.

## The Solution (Angle 2)

**Two changes**:

### 1. Add explicit bcrypt dependency to requirements.txt

```txt
bcrypt==4.0.1
passlib[bcrypt]==1.7.4
```

This ensures bcrypt 4.x is installed correctly as passlib's backend.

### 2. Use configured bcrypt hasher

```python
def hash_password(password: str) -> str:
    """Hash a password using bcrypt with explicit variant."""
    import hashlib

    # bcrypt has a 72-byte limit on password length
    # For passwords exceeding this, pre-hash with SHA-256
    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        # Use SHA-256 to create a fixed-length hash that's under 72 bytes
        password = hashlib.sha256(password_bytes).hexdigest()

    # Use explicit bcrypt configuration with variant 2b and 12 rounds
    return bcrypt.using(ident="2b", rounds=12).hash(password)
```

**Key change**: `bcrypt.using(ident="2b", rounds=12).hash(password)` instead of `bcrypt.hash(password)`

This explicitly configures the bcrypt hasher with:
- `ident="2b"` - Modern bcrypt variant
- `rounds=12` - 12 rounds of hashing (good security/performance balance)

## Why This Worked

`bcrypt.using()` creates a configured hasher object that properly handles the password string, avoiding the internal errors that were occurring with the unconfigured `bcrypt.hash()` call.

## Verification

Full authentication flow tested successfully:

✅ **Registration**: Creates user and returns JWT tokens
```bash
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","country":"US"}'
```

✅ **Login**: Verifies password and returns new JWT tokens
```bash
curl -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

✅ **Authenticated requests**: JWT tokens work correctly
```bash
curl -X GET https://claude-code-projects-production.up.railway.app/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

## Commit

```
a4b4b9d - fix: Add explicit bcrypt dependency and use configured hasher (Angle 2)
```

## Production Backend URL

```
https://claude-code-projects-production.up.railway.app
```

Ready to link with Vercel frontend!
