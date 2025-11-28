"""
Dead Letter Queue (DLQ) for failed events.

Stores events that failed to process for later retry or investigation.
"""

import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer, JSON as SQLAlchemyJSON
from sqlalchemy.orm import Session

from app.database import Base
from app.events import Event
from app.models.user import JSONType


class FailedEvent(Base):
    """
    Model for failed events in the Dead Letter Queue.

    Attributes:
        id: Primary key
        event_id: Original event ID
        event_type: Type of event
        correlation_id: Event correlation ID
        payload: Event payload
        error_message: Error that caused failure
        error_type: Type of error
        stack_trace: Full stack trace
        retry_count: Number of retry attempts
        max_retries: Maximum retry attempts allowed
        status: Status (pending, retrying, failed, resolved)
        created_at: When event failed
        last_retry_at: Last retry timestamp
        resolved_at: When event was successfully processed
    """

    __tablename__ = "failed_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(String(255), nullable=False, unique=True, index=True)
    event_type = Column(String(255), nullable=False, index=True)
    correlation_id = Column(String(255), nullable=True, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)

    # Event data
    payload = Column(JSONType, nullable=False)
    metadata = Column(JSONType, nullable=True)

    # Error information
    error_message = Column(Text, nullable=False)
    error_type = Column(String(255), nullable=False)
    stack_trace = Column(Text, nullable=True)

    # Retry management
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)
    # Status values: pending, retrying, failed, resolved

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_retry_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<FailedEvent(id={self.id}, event_id='{self.event_id}', status='{self.status}', retries={self.retry_count})>"


class DeadLetterQueue:
    """
    Service for managing failed events.

    Features:
    - Store failed events
    - Retry with exponential backoff
    - Track retry attempts
    - Mark events as resolved
    """

    def __init__(self, db_session: Session):
        """
        Initialize DLQ service.

        Args:
            db_session: Database session
        """
        self.db = db_session

    def add_failed_event(
        self,
        event: Event,
        error_message: str,
        error_type: str,
        stack_trace: Optional[str] = None,
        max_retries: int = 3
    ) -> FailedEvent:
        """
        Add an event to the DLQ.

        Args:
            event: The failed event
            error_message: Error description
            error_type: Type of error
            stack_trace: Full stack trace (optional)
            max_retries: Maximum retry attempts

        Returns:
            FailedEvent: The created failed event record
        """
        failed_event = FailedEvent(
            event_id=event.event_id,
            event_type=event.event_type.value,
            correlation_id=event.correlation_id,
            user_id=event.user_id,
            payload=event.payload,
            metadata=event.metadata,
            error_message=error_message,
            error_type=error_type,
            stack_trace=stack_trace,
            retry_count=0,
            max_retries=max_retries,
            status="pending"
        )

        self.db.add(failed_event)
        self.db.commit()
        self.db.refresh(failed_event)

        print(f"📥 Added event {event.event_id} to DLQ: {error_type}")

        return failed_event

    def get_pending_events(self, limit: int = 100) -> List[FailedEvent]:
        """
        Get pending events that can be retried.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of pending failed events
        """
        return self.db.query(FailedEvent).filter(
            FailedEvent.status == "pending",
            FailedEvent.retry_count < FailedEvent.max_retries
        ).limit(limit).all()

    def mark_retrying(self, failed_event: FailedEvent) -> None:
        """
        Mark an event as being retried.

        Args:
            failed_event: The failed event to update
        """
        failed_event.status = "retrying"
        failed_event.retry_count += 1
        failed_event.last_retry_at = datetime.utcnow()
        self.db.commit()

    def mark_resolved(self, failed_event: FailedEvent) -> None:
        """
        Mark an event as successfully resolved.

        Args:
            failed_event: The failed event to mark as resolved
        """
        failed_event.status = "resolved"
        failed_event.resolved_at = datetime.utcnow()
        self.db.commit()

        print(f"✅ Resolved failed event {failed_event.event_id}")

    def mark_permanently_failed(self, failed_event: FailedEvent) -> None:
        """
        Mark an event as permanently failed (max retries exceeded).

        Args:
            failed_event: The failed event to mark as failed
        """
        failed_event.status = "failed"
        self.db.commit()

        print(f"❌ Permanently failed event {failed_event.event_id} after {failed_event.retry_count} retries")

    def get_stats(self) -> dict:
        """
        Get DLQ statistics.

        Returns:
            Dict with statistics
        """
        from sqlalchemy import func

        total = self.db.query(func.count(FailedEvent.id)).scalar()
        pending = self.db.query(func.count(FailedEvent.id)).filter(
            FailedEvent.status == "pending"
        ).scalar()
        retrying = self.db.query(func.count(FailedEvent.id)).filter(
            FailedEvent.status == "retrying"
        ).scalar()
        failed = self.db.query(func.count(FailedEvent.id)).filter(
            FailedEvent.status == "failed"
        ).scalar()
        resolved = self.db.query(func.count(FailedEvent.id)).filter(
            FailedEvent.status == "resolved"
        ).scalar()

        return {
            "total": total,
            "pending": pending,
            "retrying": retrying,
            "failed": failed,
            "resolved": resolved
        }
