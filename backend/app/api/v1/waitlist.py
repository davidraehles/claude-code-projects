"""
Waitlist API for Go, Cart! - Handles waitlist signup, verification, and status checks.
"""

from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.api.dependencies import get_database
from app.models.waitlist import WaitlistEntry
from app.schemas.waitlist import WaitlistCreate, WaitlistVerify, WaitlistResponse

router = APIRouter()

def get_position(db: Session, entry: WaitlistEntry) -> Optional[int]:
    """Compute FIFO queue position based on creation timestamp."""
    if not entry.created_at:
        return None
    count = db.query(WaitlistEntry).filter(
        WaitlistEntry.created_at < entry.created_at
    ).count()
    return count + 1

def create_waitlist_response(entry: WaitlistEntry, db: Session) -> WaitlistResponse:
    """Create response model with computed position."""
    position = get_position(db, entry)
    return WaitlistResponse(
        id=int(entry.id),
        email=entry.email,
        status=entry.status,
        position=position,
        created_at=entry.created_at
    )

@router.post("/", response_model=WaitlistResponse, status_code=201)
def join_waitlist(
    waitlist_in: WaitlistCreate,
    db: Session = Depends(get_database)
):
    # Prevent duplicates
    existing = db.query(WaitlistEntry).filter(
        WaitlistEntry.email == waitlist_in.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered on the waitlist"
        )

    # Create pending entry
    entry = WaitlistEntry(
        email=waitlist_in.email,
        status="PENDING",
        verification_token=str(uuid.uuid4()),
        metadata_payload=waitlist_in.metadata,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # TODO: Trigger verification email with entry.verification_token

    return create_waitlist_response(entry, db)

@router.post("/verify", response_model=WaitlistResponse)
def verify_email(
    verify_in: WaitlistVerify,
    db: Session = Depends(get_database)
):
    entry = db.query(WaitlistEntry).filter(
        WaitlistEntry.verification_token == verify_in.token
    ).first()

    if not entry:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )

    if entry.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )

    # Mark as verified and clear token
    entry.status = "VERIFIED"
    entry.verified_at = datetime.utcnow()
    entry.verification_token = None
    db.commit()
    db.refresh(entry)

    return create_waitlist_response(entry, db)

@router.get("/status", response_model=WaitlistResponse)
def get_status(
    email: EmailStr = Query(..., description="Email address to check"),
    db: Session = Depends(get_database)
):
    entry = db.query(WaitlistEntry).filter(
        WaitlistEntry.email == email
    ).first()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Waitlist entry not found"
        )

    return create_waitlist_response(entry, db)
