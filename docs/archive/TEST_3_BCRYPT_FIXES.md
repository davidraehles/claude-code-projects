# 3 Different Approaches to Fix Bcrypt Password Hashing

## The Problem
Error: "password cannot be longer than 72 bytes" for a 15-byte password ("testpassword123")

This suggests the error is NOT about the password length, but about HOW bcrypt is being called.

---

## Angle 1: Explicitly Specify Bcrypt Variant

**Theory**: passlib's bcrypt might be using the wrong backend or variant.

**Fix**:
```python
def hash_password(password: str) -> str:
    """Hash a password using bcrypt with explicit variant."""
    import hashlib
    from passlib.hash import bcrypt

    # Use explicit bcrypt variant (2b is modern, 2a is compatible)
    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        password = hashlib.sha256(password_bytes).hexdigest()

    # Explicitly specify bcrypt variant and rounds
    return bcrypt.using(ident="2b", rounds=12).hash(password)
```

**What this changes**: Uses `bcrypt.using()` to create a configured hasher with explicit parameters.

---

## Angle 2: Add Explicit Bcrypt Dependency

**Theory**: passlib[bcrypt] might not be installing bcrypt correctly, or wrong version.

**Fix**: Update `requirements.txt`:
```txt
# Before
passlib[bcrypt]==1.7.4

# After
bcrypt==4.0.1  # Explicit bcrypt package
passlib[bcrypt]==1.7.4
```

**Then use**:
```python
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import hashlib
    from passlib.hash import bcrypt

    password_bytes = password.encode('utf-8')

    if len(password_bytes) > 72:
        password = hashlib.sha256(password_bytes).hexdigest()

    return bcrypt.hash(password)
```

**What this changes**: Ensures bcrypt 4.x is installed explicitly.

---

## Angle 3: Use Native Bcrypt Library

**Theory**: passlib wrapper is causing issues. Use bcrypt library directly.

**Fix**: Update `requirements.txt`:
```txt
bcrypt==4.0.1
```

**And change the code**:
```python
def hash_password(password: str) -> str:
    """Hash a password using native bcrypt library."""
    import hashlib
    import bcrypt as bcrypt_lib

    password_bytes = password.encode('utf-8')

    # bcrypt has 72-byte limit
    if len(password_bytes) > 72:
        # Pre-hash with SHA-256 for long passwords
        password = hashlib.sha256(password_bytes).hexdigest()
        password_bytes = password.encode('utf-8')

    # Generate salt and hash
    salt = bcrypt_lib.gensalt(rounds=12)
    hashed = bcrypt_lib.hashpw(password_bytes, salt)

    # Return as string (bcrypt returns bytes)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using native bcrypt."""
    import bcrypt as bcrypt_lib

    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt_lib.checkpw(password_bytes, hashed_bytes)
```

**What this changes**: Bypasses passlib entirely, uses bcrypt library directly.

---

## Recommendation

**Try Angle 2 first** (explicit bcrypt dependency):
- Simplest change
- Keeps using passlib (consistent with rest of codebase)
- Just ensures correct bcrypt version is installed

If that doesn't work, **try Angle 3** (native bcrypt):
- Most reliable - uses bcrypt directly
- No wrapper overhead
- Clear control over salt generation and hashing

---

## Next Steps

1. Implement Angle 2 first
2. Deploy and test
3. If still fails, implement Angle 3
4. If still fails, check Railway logs for actual error source
