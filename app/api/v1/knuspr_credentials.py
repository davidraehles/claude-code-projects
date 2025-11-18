"""
Knuspr Credentials API v1

Endpoints for managing user's Knuspr account credentials:
- POST /api/v1/knuspr-credentials - Add/update credentials
- GET /api/v1/knuspr-credentials - Get credential status
- POST /api/v1/knuspr-credentials/verify - Test credentials
- DELETE /api/v1/knuspr-credentials - Remove credentials
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from app.api.dependencies import get_database, get_current_user_id
from app.models.knuspr_credential import KnusprCredential
from app.services.credential_manager import CredentialManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knuspr-credentials", tags=["Knuspr Credentials"])

# Initialize credential manager
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """Get or create credential manager instance."""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager


# ============ Request/Response Models ============

class SaveCredentialsRequest(BaseModel):
    """Request to save Knuspr credentials"""
    knuspr_email: str = Field(..., description="Email or phone for Knuspr account")
    knuspr_password: str = Field(..., description="Knuspr account password", min_length=6)
    country: Optional[str] = Field(
        default="cz",
        description="Country code: cz (Czechia), sk (Slovakia), pl (Poland)"
    )
    test_connection: Optional[bool] = Field(
        default=True,
        description="If True, test credentials before saving"
    )


class CredentialStatusResponse(BaseModel):
    """Response with credential status"""
    has_credentials: bool = Field(..., description="Whether user has saved credentials")
    is_active: bool = Field(..., description="Whether credentials are active")
    country: Optional[str] = Field(None, description="Country code")
    knuspr_email: Optional[str] = Field(None, description="Masked Knuspr email")
    last_verified_at: Optional[str] = Field(None, description="Last successful verification")
    verification_error: Optional[str] = Field(None, description="Latest error message")


class VerifyCredentialsResponse(BaseModel):
    """Response from credential verification"""
    is_valid: bool = Field(..., description="Whether credentials are valid")
    message: str = Field(..., description="Status message")
    last_verified_at: Optional[str] = Field(None, description="Verification timestamp")


class DeleteCredentialsResponse(BaseModel):
    """Response from credential deletion"""
    message: str = Field(..., description="Status message")
    success: bool = Field(..., description="Whether deletion was successful")


# ============ API Endpoints ============

@router.post("/", response_model=CredentialStatusResponse, status_code=201)
async def save_knuspr_credentials(
    request: SaveCredentialsRequest,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
    credential_manager: CredentialManager = Depends(get_credential_manager)
):
    """
    Save or update Knuspr account credentials.

    Credentials are encrypted before storage and can be tested with Knuspr API.

    Args:
        request: SaveCredentialsRequest with email, password, country
        db: Database session
        user_id: Current user ID
        credential_manager: Credential manager service

    Returns:
        CredentialStatusResponse with credential status

    Raises:
        400: If credentials are invalid or test fails
        500: If storage fails
    """
    try:
        logger.info(f"Saving Knuspr credentials for user {user_id}")

        # Validate country code
        valid_countries = ["cz", "sk", "pl"]
        if request.country not in valid_countries:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid country. Must be one of: {', '.join(valid_countries)}"
            )

        # Save credentials
        credential = await credential_manager.save_credentials(
            db=db,
            user_id=user_id,
            knuspr_email=request.knuspr_email,
            knuspr_password=request.knuspr_password,
            country=request.country,
            test_connection=request.test_connection
        )

        logger.info(f"Credentials saved for user {user_id}")

        return CredentialStatusResponse(
            has_credentials=True,
            is_active=credential.is_active,
            country=credential.country,
            knuspr_email=credential.to_dict()["knuspr_email"],  # Masked
            last_verified_at=credential.last_verified_at.isoformat() if credential.last_verified_at else None,
            verification_error=credential.verification_error
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to save credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save credentials")


@router.get("/", response_model=CredentialStatusResponse)
async def get_credential_status(
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get status of user's Knuspr credentials.

    Returns masked email and verification status without exposing sensitive data.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        CredentialStatusResponse with credential status (no passwords)

    Raises:
        500: If retrieval fails
    """
    try:
        credential = db.query(KnusprCredential).filter(
            KnusprCredential.user_id == user_id,
            KnusprCredential.is_active == True
        ).first()

        if not credential:
            return CredentialStatusResponse(
                has_credentials=False,
                is_active=False,
                country=None,
                knuspr_email=None,
                last_verified_at=None,
                verification_error=None
            )

        return CredentialStatusResponse(
            has_credentials=True,
            is_active=credential.is_active,
            country=credential.country,
            knuspr_email=credential.to_dict()["knuspr_email"],  # Masked
            last_verified_at=credential.last_verified_at.isoformat() if credential.last_verified_at else None,
            verification_error=credential.verification_error
        )

    except Exception as e:
        logger.error(f"Failed to retrieve credential status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve credential status")


@router.post("/verify", response_model=VerifyCredentialsResponse)
async def verify_knuspr_credentials(
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
    credential_manager: CredentialManager = Depends(get_credential_manager)
):
    """
    Verify Knuspr credentials by testing with API.

    Attempts to authenticate with Knuspr using stored credentials.
    Updates credential record with verification status.

    Args:
        db: Database session
        user_id: Current user ID
        credential_manager: Credential manager service

    Returns:
        VerifyCredentialsResponse with verification status

    Raises:
        404: If no credentials found
        500: If verification fails
    """
    try:
        logger.info(f"Verifying Knuspr credentials for user {user_id}")

        # Check if credentials exist
        credential = db.query(KnusprCredential).filter(
            KnusprCredential.user_id == user_id,
            KnusprCredential.is_active == True
        ).first()

        if not credential:
            raise HTTPException(status_code=404, detail="No Knuspr credentials found")

        # Verify credentials
        is_valid = await credential_manager.verify_credentials(db, user_id)

        # Fetch updated credential record
        credential = db.query(KnusprCredential).filter(
            KnusprCredential.user_id == user_id
        ).first()

        if is_valid:
            message = "Knuspr credentials verified successfully"
        else:
            message = f"Credential verification failed: {credential.verification_error or 'Unknown error'}"

        return VerifyCredentialsResponse(
            is_valid=is_valid,
            message=message,
            last_verified_at=credential.last_verified_at.isoformat() if credential.last_verified_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Credential verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify credentials")


@router.delete("/", response_model=DeleteCredentialsResponse)
async def delete_knuspr_credentials(
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
    credential_manager: CredentialManager = Depends(get_credential_manager)
):
    """
    Delete/deactivate Knuspr credentials.

    Performs soft delete by marking credentials as inactive (GDPR compliant).

    Args:
        db: Database session
        user_id: Current user ID
        credential_manager: Credential manager service

    Returns:
        DeleteCredentialsResponse with deletion status

    Raises:
        404: If no credentials found
        500: If deletion fails
    """
    try:
        logger.info(f"Deleting Knuspr credentials for user {user_id}")

        # Delete credentials
        success = await credential_manager.delete_credentials(db, user_id)

        if not success:
            raise HTTPException(status_code=404, detail="No Knuspr credentials found")

        logger.info(f"Credentials deleted for user {user_id}")

        return DeleteCredentialsResponse(
            message="Knuspr credentials deleted successfully",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete credentials")
