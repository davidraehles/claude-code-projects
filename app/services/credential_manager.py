"""
Knuspr Credential Manager

Handles secure storage and retrieval of Knuspr credentials:
- Encryption/decryption of sensitive data
- Credential validation
- Authentication testing
- Secure deletion

Uses Fernet (symmetric encryption) for credentials.
In production, consider using AWS KMS, HashiCorp Vault, or similar.
"""

import logging
from typing import Optional
from datetime import datetime
from cryptography.fernet import Fernet
import os
import json

from sqlalchemy.orm import Session

from app.models.knuspr_credential import KnusprCredential
from app.services.knuspr_mcp_client import KnusprMCPClient, KnusprCountry

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Manages encryption, storage, and validation of Knuspr credentials.

    Uses Fernet symmetric encryption for sensitive data.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize credential manager.

        Args:
            encryption_key: Fernet key for encryption (generated if not provided)
                           In production, load from secure vault
        """
        if encryption_key is None:
            # Generate new key (use environment variable in production)
            encryption_key = os.getenv(
                "KNUSPR_ENCRYPTION_KEY",
                Fernet.generate_key().decode()
            )

        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        logger.info("CredentialManager initialized")

    def encrypt(self, data: str) -> str:
        """
        Encrypt a string using Fernet.

        Args:
            data: Plain text to encrypt

        Returns:
            Encrypted string (base64-encoded)
        """
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a Fernet-encrypted string.

        Args:
            encrypted_data: Base64-encoded encrypted data

        Returns:
            Decrypted plain text string

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    async def save_credentials(
        self,
        db: Session,
        user_id: int,
        knuspr_email: str,
        knuspr_password: str,
        country: str = "cz",
        test_connection: bool = True
    ) -> KnusprCredential:
        """
        Save Knuspr credentials securely.

        Workflow:
        1. Encrypt email and password
        2. Test credentials (optional)
        3. Store in database
        4. Return credential object

        Args:
            db: Database session
            user_id: User ID
            knuspr_email: Email or phone for Knuspr
            knuspr_password: Knuspr password
            country: Country code (cz, sk, pl)
            test_connection: If True, validate credentials with Knuspr API

        Returns:
            KnusprCredential object

        Raises:
            ValueError: If credentials are invalid
            RuntimeError: If database operation fails
        """
        logger.info(f"Saving Knuspr credentials for user {user_id}")

        # Validate inputs
        if not knuspr_email or not knuspr_password:
            raise ValueError("Email and password are required")

        if len(knuspr_password) < 6:
            raise ValueError("Password appears to be invalid (too short)")

        # Test credentials if requested
        if test_connection:
            is_valid = await self._test_credentials(
                knuspr_email,
                knuspr_password,
                country
            )
            if not is_valid:
                raise ValueError("Invalid Knuspr credentials - authentication failed")

        # Encrypt sensitive data
        encrypted_email = self.encrypt(knuspr_email)
        encrypted_password = self.encrypt(knuspr_password)

        # Check if credentials already exist for this user
        existing = db.query(KnusprCredential).filter(
            KnusprCredential.user_id == user_id
        ).first()

        if existing:
            # Update existing credentials
            logger.info(f"Updating existing credentials for user {user_id}")
            existing.knuspr_email = encrypted_email
            existing.knuspr_password = encrypted_password
            existing.country = country
            existing.is_active = True
            existing.verification_error = None
            existing.last_verified_at = datetime.utcnow()
            credential = existing
        else:
            # Create new credentials
            logger.info(f"Creating new credentials for user {user_id}")
            credential = KnusprCredential(
                user_id=user_id,
                knuspr_email=encrypted_email,
                knuspr_password=encrypted_password,
                country=country,
                is_active=True,
                last_verified_at=datetime.utcnow()
            )
            db.add(credential)

        # Persist to database
        try:
            db.commit()
            db.refresh(credential)
            logger.info(f"Credentials saved successfully for user {user_id}")
            return credential
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save credentials: {str(e)}")
            raise RuntimeError(f"Failed to save credentials: {str(e)}")

    async def get_credentials(
        self,
        db: Session,
        user_id: int
    ) -> Optional[tuple[str, str, str]]:
        """
        Retrieve and decrypt Knuspr credentials for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Tuple of (email, password, country) or None if not found

        Raises:
            RuntimeError: If decryption fails
        """
        credential = db.query(KnusprCredential).filter(
            KnusprCredential.user_id == user_id,
            KnusprCredential.is_active == True
        ).first()

        if not credential:
            logger.debug(f"No active credentials found for user {user_id}")
            return None

        try:
            email = self.decrypt(credential.knuspr_email)
            password = self.decrypt(credential.knuspr_password)
            return (email, password, credential.country)
        except Exception as e:
            logger.error(f"Failed to decrypt credentials for user {user_id}: {str(e)}")
            raise RuntimeError(f"Failed to decrypt credentials: {str(e)}")

    async def verify_credentials(
        self,
        db: Session,
        user_id: int
    ) -> bool:
        """
        Test credentials with Knuspr API to verify they're still valid.

        Updates credential record with verification status.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            credentials = await self.get_credentials(db, user_id)
            if not credentials:
                return False

            email, password, country = credentials

            # Test with Knuspr API
            is_valid = await self._test_credentials(email, password, country)

            # Update credential record
            credential = db.query(KnusprCredential).filter(
                KnusprCredential.user_id == user_id,
                KnusprCredential.is_active == True
            ).first()

            if credential:
                if is_valid:
                    credential.last_verified_at = datetime.utcnow()
                    credential.verification_error = None
                    logger.info(f"Credentials verified for user {user_id}")
                else:
                    credential.verification_error = "Authentication failed"
                    logger.warning(f"Credential verification failed for user {user_id}")

                db.commit()

            return is_valid

        except Exception as e:
            logger.error(f"Credential verification error: {str(e)}")
            return False

    async def delete_credentials(
        self,
        db: Session,
        user_id: int
    ) -> bool:
        """
        Delete Knuspr credentials (soft delete - mark as inactive).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        try:
            credential = db.query(KnusprCredential).filter(
                KnusprCredential.user_id == user_id
            ).first()

            if not credential:
                logger.warning(f"No credentials found for user {user_id}")
                return False

            credential.is_active = False
            db.commit()
            logger.info(f"Credentials deactivated for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete credentials: {str(e)}")
            db.rollback()
            raise RuntimeError(f"Failed to delete credentials: {str(e)}")

    async def _test_credentials(
        self,
        email: str,
        password: str,
        country: str
    ) -> bool:
        """
        Test credentials by attempting to authenticate with Knuspr.

        Args:
            email: Knuspr email/phone
            password: Knuspr password
            country: Country code

        Returns:
            True if authentication succeeds, False otherwise
        """
        try:
            logger.debug(f"Testing Knuspr credentials for {email}")

            # Convert country string to Enum if needed
            try:
                country_enum = KnusprCountry(country)
            except ValueError:
                logger.warning(f"Invalid country code: {country}")
                return False

            # Create temporary client to test credentials
            client = KnusprMCPClient(
                login_email=email,
                login_password=password,
                country=country_enum
            )

            # Attempt authentication
            success = await client.authenticate()

            if success:
                # Clean up session
                await client.close()
                logger.info("Credentials validated successfully")
                return True
            else:
                logger.warning("Credential validation failed")
                return False

        except Exception as e:
            logger.error(f"Error testing credentials: {str(e)}")
            return False

    def get_encryption_key_hash(self) -> str:
        """
        Get a hash of the encryption key for verification.

        Used to ensure the same key is being used for decryption.

        Returns:
            Hash of encryption key
        """
        import hashlib
        key_bytes = self.cipher._signing_key + self.cipher._encryption_key
        return hashlib.sha256(key_bytes).hexdigest()[:16]
