# Password Hashing Bug - Root Cause Analysis

## The Mystery

**Test Password**: "testpassword123" (15 bytes)
**Error**: "password cannot be longer than 72 bytes"

**This doesn't make sense!** A 15-byte password shouldn't trigger a 72-byte limit error.

---

## Possible Causes

### 1. Railway Is Deploying OLD Code

**Evidence**:
- Code looks correct locally (commit 0a36ffa)
- Code is pushed to GitHub
- But error persists in deployment

**Check**:
- Is Railway connected to the correct branch (`claude/main`)?
- Is Railway building from latest commit?
- Check Railway deployment logs for commit hash

### 2. The Fix Is Actually Wrong

Our current fix:
```python
def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return bcrypt.hash(truncated_password)
```

**But** for a 15-byte password, this should work fine!

### 3. Error Is Coming From Elsewhere

Maybe the error is NOT from `hash_password()` at all!

**Check**:
- Is there password validation in Pydantic models?
- Is passlib configured elsewhere?
- Is there middleware intercepting?

---

## The REAL Fix

Based on passlib documentation, bcrypt.hash() should handle strings directly:

```python
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # For passwords under 72 bytes, bcrypt.hash() works directly
    # For longer passwords, we need to pre-hash or truncate

    # Option 1: Just use bcrypt directly (simplest)
    return bcrypt.hash(password)

    # Option 2: If we need to handle >72 byte passwords, use SHA-256 first
    # import hashlib
    # if len(password.encode('utf-8')) > 72:
    #     password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    # return bcrypt.hash(password)
```

**For "testpassword123" (15 bytes), Option 1 should work perfectly!**

---

## Next Steps

1. **Verify Railway deployment**:
   - Check Railway is deploying from `claude/main`
   - Check latest deployment shows commit `0a36ffa`
   - Check build logs for errors

2. **Simplify the fix**:
   - Remove truncation logic (it's unnecessary for normal passwords)
   - Just use `bcrypt.hash(password)` directly
   - Add SHA-256 pre-hashing only if needed for very long passwords

3. **Test locally first**:
   - Install passlib locally
   - Test the hash_password function
   - Verify it works for "testpassword123"

---

## Recommended Fix

```python
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # bcrypt has a 72-byte limit, but for normal passwords this is fine
    # If password is too long, pre-hash it

    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        # For very long passwords, use SHA-256 first
        import hashlib
        password = hashlib.sha256(password_bytes).hexdigest()

    return bcrypt.hash(password)
```

This handles both short and long passwords correctly!
