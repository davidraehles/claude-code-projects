"""
Error Handler Agent.

Handles failed events from the Dead Letter Queue with retry logic.
"""

import asyncio
from typing import Optional
from sqlalchemy.orm import Session

from app.services.dead_letter_queue import DeadLetterQueue, FailedEvent
from app.events import Event, EventType
from app.events.bus import EventBus


class ErrorHandlerAgent:
    """
    Agent for handling failed events.

    Features:
    - Retry failed events with exponential backoff
    - Track retry attempts
    - Mark permanently failed events
    - Send notifications for critical failures
    """

    def __init__(self, db_session: Session, event_bus: EventBus):
        """
        Initialize Error Handler Agent.

        Args:
            db_session: Database session
            event_bus: Event bus for publishing retry events
        """
        self.db = db_session
        self.event_bus = event_bus
        self.dlq = DeadLetterQueue(db_session)

    async def process_failed_events(self, max_events: int = 50) -> dict:
        """
        Process failed events from the DLQ.

        Args:
            max_events: Maximum number of events to process

        Returns:
            Dict with processing statistics
        """
        stats = {
            "processed": 0,
            "retried": 0,
            "resolved": 0,
            "permanently_failed": 0
        }

        # Get pending events
        pending_events = self.dlq.get_pending_events(limit=max_events)

        for failed_event in pending_events:
            stats["processed"] += 1

            try:
                # Check if we've exceeded max retries
                if failed_event.retry_count >= failed_event.max_retries:
                    self.dlq.mark_permanently_failed(failed_event)
                    stats["permanently_failed"] += 1
                    continue

                # Mark as retrying
                self.dlq.mark_retrying(failed_event)

                # Calculate backoff delay (exponential: 2^retry_count seconds)
                backoff_delay = 2 ** failed_event.retry_count

                # Wait for backoff
                await asyncio.sleep(backoff_delay)

                # Reconstruct event
                event = Event(
                    event_id=failed_event.event_id,
                    event_type=EventType(failed_event.event_type),
                    correlation_id=failed_event.correlation_id,
                    user_id=failed_event.user_id,
                    payload=failed_event.payload,
                    metadata=failed_event.metadata or {}
                )

                # Retry publishing the event
                success = await self.event_bus.publish(event)

                if success:
                    self.dlq.mark_resolved(failed_event)
                    stats["resolved"] += 1
                    stats["retried"] += 1
                else:
                    # Mark back as pending for next retry
                    failed_event.status = "pending"
                    self.db.commit()
                    stats["retried"] += 1

            except Exception as e:
                print(f"⚠️  Error processing failed event {failed_event.event_id}: {e}")
                # Mark back as pending
                failed_event.status = "pending"
                self.db.commit()

        return stats

    async def handle_event_error(
        self,
        event: Event,
        error: Exception,
        max_retries: int = 3
    ) -> None:
        """
        Handle an event processing error.

        Args:
            event: The event that failed
            error: The exception that occurred
            max_retries: Maximum retry attempts
        """
        import traceback

        error_message = str(error)
        error_type = type(error).__name__
        stack_trace = traceback.format_exc()

        # Add to DLQ
        self.dlq.add_failed_event(
            event=event,
            error_message=error_message,
            error_type=error_type,
            stack_trace=stack_trace,
            max_retries=max_retries
        )

        # Publish error event
        await self.event_bus.publish(Event(
            event_type=EventType.AGENT_ERROR,
            correlation_id=event.correlation_id,
            user_id=event.user_id,
            payload={
                "agent_name": "ErrorHandler",
                "error_message": error_message,
                "error_type": error_type,
                "original_event_id": event.event_id,
                "original_event_type": event.event_type.value
            }
        ))

    def get_dlq_stats(self) -> dict:
        """
        Get DLQ statistics.

        Returns:
            Dict with DLQ stats
        """
        return self.dlq.get_stats()
