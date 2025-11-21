"""
User API endpoints.

Provides REST API for user operations including preferences and notifications.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator

from app.api.dependencies import get_database, get_current_user_id
from app.models.user import User
from app.services.notifications import NotificationService, Notification as NotificationModel


router = APIRouter()


# Pydantic schemas
class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    dietary_restrictions: Optional[List[str]] = Field(None, description="Dietary restrictions")
    excluded_ingredients: Optional[List[str]] = Field(None, description="Excluded ingredients")
    preferred_cuisines: Optional[List[str]] = Field(None, description="Preferred cuisines")
    language: Optional[str] = Field(None, description="Preferred language")
    theme: Optional[str] = Field(None, description="UI theme (light, dark)")
    notification_settings: Optional[dict] = Field(None, description="Notification preferences")


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""
    user_id: int
    preferences: dict


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


# User Preferences Endpoints

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get user preferences.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        User preferences
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPreferencesResponse(
        user_id=user.id,
        preferences=user.preferences or {}
    )


@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Update user preferences.

    Args:
        preferences: Preferences to update
        db: Database session
        user_id: Current user ID

    Returns:
        Updated user preferences
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get existing preferences or empty dict
    current_prefs = user.preferences or {}

    # Update with new preferences
    update_dict = preferences.model_dump(exclude_unset=True)
    current_prefs.update(update_dict)

    user.preferences = current_prefs
    db.commit()
    db.refresh(user)

    return UserPreferencesResponse(
        user_id=user.id,
        preferences=user.preferences
    )


# Notification Endpoints

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get user notifications.

    Args:
        unread_only: Only return unread notifications
        limit: Maximum number to return
        db: Database session
        user_id: Current user ID

    Returns:
        List of notifications
    """
    service = NotificationService(db)
    notifications = service.get_user_notifications(
        user_id=user_id,
        unread_only=unread_only,
        limit=limit
    )

    return [
        NotificationResponse(
            id=n.id,
            title=n.title,
            message=n.message,
            type=n.type,
            is_read=n.is_read,
            action_url=n.action_url,
            created_at=n.created_at.isoformat()
        )
        for n in notifications
    ]


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark a notification as read.

    Args:
        notification_id: Notification ID
        db: Database session
        user_id: Current user ID

    Returns:
        Success message
    """
    service = NotificationService(db)
    success = service.mark_as_read(notification_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"status": "success", "message": "Notification marked as read"}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Mark all notifications as read.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        Number of notifications marked as read
    """
    service = NotificationService(db)
    count = service.mark_all_as_read(user_id)

    return {"status": "success", "count": count}


@router.get("/notifications/unread-count")
async def get_unread_count(
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id)
):
    """
    Get count of unread notifications.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        Unread count
    """
    service = NotificationService(db)
    count = service.get_unread_count(user_id)

    return {"unread_count": count}
