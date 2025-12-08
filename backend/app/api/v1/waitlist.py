"""
Waitlist API for Go, Cart! - Handles waitlist signup, verification, and status checks.
"""

from datetime import datetime, timezone
from typing import Optional
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, Gauge

from app.api.dependencies import get_database
from app.models.waitlist import WaitlistEntry
from app.schemas.waitlist import WaitlistCreate, WaitlistVerify, WaitlistResponse, WaitlistStatus

logger = logging.getLogger(__name__)
router = APIRouter()

# Prometheus Metrics
waitlist_signups_total = Counter(
    'waitlist_signups_total',
    'Total number of waitlist signup attempts',
    ['status']  # success, duplicate, error
)

waitlist_verifications_total = Counter(
    'waitlist_verifications_total',
    'Total number of email verification attempts',
    ['status']  # success, invalid_token, already_verified, error
)

waitlist_status_checks_total = Counter(
    'waitlist_status_checks_total',
    'Total number of status check requests',
    ['status']  # success, not_found, error
)

waitlist_queue_size = Gauge(
    'waitlist_queue_size',
    'Current total number of entries on the waitlist',
    ['entry_status']  # pending, verified, invited, onboarded
)

waitlist_operation_duration = Histogram(
    'waitlist_operation_duration_seconds',
    'Duration of waitlist operations',
    ['operation']  # signup, verify, status_check
)

def update_queue_metrics(db: Session) -> None:
    """Update Prometheus gauge metrics for queue sizes by status."""
    try:
        for status in [WaitlistStatus.PENDING, WaitlistStatus.VERIFIED, WaitlistStatus.INVITED, WaitlistStatus.ONBOARDED]:
            count = db.query(WaitlistEntry).filter(
                WaitlistEntry.status == status.value
            ).count()
            waitlist_queue_size.labels(entry_status=status.value.lower()).set(count)
    except Exception as e:
        logger.error(f"Error updating queue metrics: {e}")


def get_position(db: Session, entry: WaitlistEntry) -> Optional[int]:
    """Compute FIFO queue position based on ID (FIFO order)."""
    if not entry.id:
        return None
    # Count entries with ID less than current (simpler and more reliable than timestamp comparison)
    count = db.query(WaitlistEntry).filter(WaitlistEntry.id < entry.id).count()
    return count + 1

def create_waitlist_response(entry: WaitlistEntry, db: Session) -> WaitlistResponse:
    """Create response model with computed position."""
    position = get_position(db, entry)
    return WaitlistResponse(
        id=int(entry.id),
        email=entry.email,
        status=entry.status,
        position=position,
        created_at=entry.created_at,
        verified_at=entry.verified_at,
        invited_at=entry.invited_at
    )

@router.post("/", response_model=WaitlistResponse, status_code=201)
def join_waitlist(
    waitlist_in: WaitlistCreate,
    db: Session = Depends(get_database)
) -> WaitlistResponse:
    """
    Create a new waitlist entry for early access.

    Args:
        waitlist_in: Waitlist signup data with email and optional metadata
        db: Database session

    Returns:
        WaitlistResponse with entry details and queue position

    Raises:
        HTTPException: 400 if email already registered on waitlist
    """
    with waitlist_operation_duration.labels(operation='signup').time():
        try:
            # Prevent duplicates
            existing = db.query(WaitlistEntry).filter(
                WaitlistEntry.email == waitlist_in.email
            ).first()
            if existing:
                waitlist_signups_total.labels(status='duplicate').inc()
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered on the waitlist"
                )

            # Create pending entry
            entry = WaitlistEntry(
                email=waitlist_in.email,
                status=WaitlistStatus.PENDING.value,
                verification_token=str(uuid.uuid4()),
                metadata_payload=waitlist_in.metadata,
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)

            # TODO: Trigger verification email with entry.verification_token
            # from app.services.email import get_email_service
            # email_service = get_email_service()
            # email_service.send_verification_email(
            #     to_email=entry.email,
            #     verification_token=entry.verification_token
            # )

            # Update metrics
            waitlist_signups_total.labels(status='success').inc()
            update_queue_metrics(db)

            logger.info(f"New waitlist signup: {entry.email}")

            return create_waitlist_response(entry, db)

        except HTTPException:
            raise
        except Exception as e:
            waitlist_signups_total.labels(status='error').inc()
            logger.error(f"Error in waitlist signup: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during signup"
            )

@router.post("/verify", response_model=WaitlistResponse)
def verify_email(
    verify_in: WaitlistVerify,
    db: Session = Depends(get_database)
) -> WaitlistResponse:
    """
    Verify an email address using the verification token.

    Args:
        verify_in: Verification token from email
        db: Database session

    Returns:
        WaitlistResponse with verified entry details and updated queue position

    Raises:
        HTTPException: 400 if token is invalid or expired, or email already verified
    """
    with waitlist_operation_duration.labels(operation='verify').time():
        try:
            # First, try to find entry by token (won't find if already verified since token is cleared)
            entry = db.query(WaitlistEntry).filter(
                WaitlistEntry.verification_token == verify_in.token
            ).first()

            # If not found by token, check if it was already verified
            if not entry:
                # Check if this token was used before (entry exists but token is cleared)
                # This is a security measure - we don't reveal if email exists
                waitlist_verifications_total.labels(status='invalid_token').inc()
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or expired verification token"
                )

            # Additional check: entry found but status is not PENDING
            if entry.status != WaitlistStatus.PENDING.value:
                waitlist_verifications_total.labels(status='already_verified').inc()
                raise HTTPException(
                    status_code=400,
                    detail="Email already verified"
                )

            # Mark as verified and clear token
            entry.status = WaitlistStatus.VERIFIED.value
            entry.verified_at = datetime.now(timezone.utc)
            entry.verification_token = None
            db.commit()
            db.refresh(entry)

            # Update metrics
            waitlist_verifications_total.labels(status='success').inc()
            update_queue_metrics(db)

            logger.info(f"Email verified: {entry.email}")

            return create_waitlist_response(entry, db)

        except HTTPException:
            raise
        except Exception as e:
            waitlist_verifications_total.labels(status='error').inc()
            logger.error(f"Error in email verification: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during verification"
            )

@router.get("/status", response_model=WaitlistResponse)
def get_status(
    email: EmailStr = Query(..., description="Email address to check"),
    db: Session = Depends(get_database)
) -> WaitlistResponse:
    """
    Get the status and queue position for a waitlist entry.

    Args:
        email: Email address to check
        db: Database session

    Returns:
        WaitlistResponse with entry details and current queue position

    Raises:
        HTTPException: 404 if email not found on waitlist
    """
    with waitlist_operation_duration.labels(operation='status_check').time():
        try:
            entry = db.query(WaitlistEntry).filter(
                WaitlistEntry.email == email
            ).first()

            if not entry:
                waitlist_status_checks_total.labels(status='not_found').inc()
                raise HTTPException(
                    status_code=404,
                    detail="Waitlist entry not found"
                )

            waitlist_status_checks_total.labels(status='success').inc()
            return create_waitlist_response(entry, db)

        except HTTPException:
            raise
        except Exception as e:
            waitlist_status_checks_total.labels(status='error').inc()
            logger.error(f"Error in status check: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during status check"
            )
