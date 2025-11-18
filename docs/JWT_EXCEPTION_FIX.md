# PyJWT Exception Handling Fix

**Date:** 2025-11-18
**Issue:** Recipe import/create features returning "Not authenticated" error
**Root Cause:** JWT exception handling using non-existent `jwt.JWTError`
**Status:** ✅ FIXED

---

## Problem Statement

Users attempting to import recipes from URLs were seeing:
```
Failed to import recipe
Not authenticated
```

But the real error was a backend crash, not an authentication failure.

---

## Root Cause Analysis

**The Bug:**
The backend code was trying to catch `jwt.JWTError`:
```python
except jwt.JWTError:
    raise HTTPException(status_code=401, detail="Could not validate credentials")
```

**The Issue:**
PyJWT 2.8.0 (in requirements.txt) does NOT have a `JWTError` exception class.

The correct exception names in PyJWT 2.8.0 are:
- `jwt.PyJWTError` - Base exception for all JWT errors
- `jwt.InvalidTokenError` - Invalid token format/signature
- `jwt.ExpiredSignatureError` - Token has expired
- `jwt.DecodeError` - Token decode failed

**The Result:**
When the code tried to reference `jwt.JWTError` at runtime, Python threw:
```
{"error":"Internal server error","message":"module 'jwt' has no attribute 'JWTError'"}
```

This caused the harvest endpoint to crash before it could validate the user's token, resulting in the frontend seeing a generic "Not authenticated" error.

---

## Solution Implemented

### Files Changed

**1. `/app/api/dependencies.py` (line 60)**
```diff
- except jwt.JWTError:
+ except (jwt.PyJWTError, jwt.InvalidTokenError):
```

**2. `/app/api/v1/auth.py` (line 164)**
```diff
- except jwt.JWTError:
+ except (jwt.PyJWTError, jwt.InvalidTokenError):
```

### Why This Works

- `jwt.PyJWTError` catches all JWT-related errors (base exception)
- `jwt.InvalidTokenError` catches token format/signature issues specifically
- Together they cover all cases where a token is invalid/malformed
- The code now properly handles JWT errors instead of crashing

---

## Verification

**Before Fix:**
```bash
$ curl -X POST https://api.example.com/api/v1/recipes/harvest \
  -H "Authorization: Bearer test_token" \
  -d '{"url": "...", "source_type": "html"}'

Response: {"error":"Internal server error","message":"module 'jwt' has no attribute 'JWTError'"}
```

**After Fix:**
```bash
# With invalid token:
Response: {"detail":"Could not validate credentials"}

# With valid token:
Response: {
  "success":true,
  "message":"Recipe harvest queued for https://...",
  "recipe":null
}
```

---

## Commits

- **Main Fix:** `7a4e4ac` - Correct PyJWT exception handling
- **Redeployment Trigger:** `d40c24f` - Trigger Railway redeployment

---

## PyJWT Exception Reference

For future reference, here are all exceptions available in PyJWT 2.8.0:

```python
jwt.PyJWTError              # Base exception
jwt.PyJWKError              # JWK-related errors
jwt.PyJWKClientError        # JWK Client errors
jwt.PyJWKSetError           # JWK Set errors
jwt.DecodeError             # Decoding failures
jwt.ExpiredSignatureError   # Token expired
jwt.ImmatureSignatureError  # Token used before iat
jwt.InvalidAlgorithmError   # Invalid algorithm
jwt.InvalidAudienceError    # Invalid audience claim
jwt.InvalidIssuedAtError    # Invalid iat claim
jwt.InvalidIssuerError      # Invalid issuer claim
jwt.InvalidKeyError         # Invalid key
jwt.InvalidSignatureError   # Invalid signature
jwt.InvalidTokenError       # Generic invalid token
jwt.MissingRequiredClaimError  # Missing required claim
```

**To catch all JWT errors, use:**
```python
except (jwt.PyJWTError, jwt.InvalidTokenError):
    # Handle error
```

---

## Lessons Learned

1. **Always test with actual library versions** - Don't assume exception names
2. **Check library documentation** - PyJWT changed exception names in recent versions
3. **Use base exceptions for broad catching** - `PyJWTError` is the base exception
4. **Test authenticated endpoints** - The bug only surfaced when JWT validation ran

---

**Fixed By:** Claude Code
**Status:** Production verified ✅
