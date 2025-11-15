"""
Notification Service.

Handles in-app notifications for users.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Boolean
from sqlalchemy.orm import Session

from app.database import Base


class Notification(Base):
    """
    In-app notification model.

    Attributes:
        id: Primary key
        user_id: User to notify
        title: Notification title
        message: Notification message
        type: Notification type (info, success, warning, error)
        is_read: Has user read this notification?
        action_url: Optional action URL
        created_at: Creation timestamp
        read_at: When notification was read
    """

    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, default="info")  # info, success, warning, error
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    action_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', is_read={self.is_read})>"


class NotificationService:
    """Service for managing user notifications."""

    def __init__(self, db_session: Session):
        """
        Initialize notification service.

        Args:
            db_session: Database session
        """
        self.db = db_session

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info",
        action_url: Optional[str] = None
    ) -> Notification:
        """
        Create a new notification.

        Args:
            user_id: User to notify
            title: Notification title
            message: Notification message
            notification_type: Type (info, success, warning, error)
            action_url: Optional action URL

        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            action_url=action_url
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        Get notifications for a user.

        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number to return

        Returns:
            List of notifications
        """
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: Notification ID
            user_id: User ID (for security)

        Returns:
            True if successful, False otherwise
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        self.db.commit()

        return True

    def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: User ID

        Returns:
            Number of notifications marked as read
        """
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })

        self.db.commit()
        return count

    def get_unread_count(self, user_id: int) -> int:
        """
        Get count of unread notifications.

        Args:
            user_id: User ID

        Returns:
            Number of unread notifications
        """
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
