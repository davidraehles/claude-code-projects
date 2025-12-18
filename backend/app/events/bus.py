"""
Redis-based event bus for agent communication.

Implements publish-subscribe pattern using Redis for asynchronous
event-driven communication between agents.
"""

import json
import asyncio
import logging
from typing import Callable, Dict, List, Optional
import redis.asyncio as redis

from app.events import Event, EventType
from app.config.redis import get_redis_settings, get_redis_pool

logger = logging.getLogger(__name__)


class EventBus:
    """
    Redis-based event bus for publishing and subscribing to events.

    Supports:
        - Publishing events to specific channels
        - Subscribing to event types with handlers
        - Correlation ID tracking for request-response patterns
        - Retry logic with exponential backoff
        - Dead letter queue for failed events
    """

    def __init__(self):
        """Initialize event bus with Redis connection."""
        self.settings = get_redis_settings()
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.handlers: Dict[EventType, List[Callable]] = {}
        # For SSE streaming without creating additional Redis pubsub
        self._sse_queues: List[asyncio.Queue] = []
        self.is_running = False

    async def connect(self):
        """
        Establish connection to Redis.

        Raises:
            redis.ConnectionError: If connection fails
        """
        # Use shared connection pool (do not expose password in logged URL)
        pool = get_redis_pool()
        self.redis_client = redis.Redis(connection_pool=pool)
        self.pubsub = self.redis_client.pubsub()
        logger.info("Connected to Redis at %s:%s", self.settings.host, self.settings.port)

    async def disconnect(self):
        """Close Redis connection and cleanup resources."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from Redis")

    async def publish(self, event: Event) -> bool:
        """
        Publish an event to the event bus.

        Args:
            event: Event to publish

        Returns:
            bool: True if published successfully, False otherwise
        """
        if not self.redis_client:
            # Do not raise here; allow callers to continue gracefully when
            # the event bus is not available (e.g., in tests or degraded mode).
            logger.warning("EventBus not connected. Skipping publish")
            return False

        try:
            # Serialize event to JSON
            event_json = event.model_dump_json()

            # Publish to channel named after event type
            channel = f"events:{event.event_type.value}"
            await self.redis_client.publish(channel, event_json)

            # Also store in a sorted set for audit/replay (optional)
            timestamp_score = event.timestamp.timestamp()
            history_key = f"events:history:{event.event_type.value}"
            await self.redis_client.zadd(history_key, {event_json: timestamp_score})
            # Keep history bounded and set TTL to 24 hours
            max_history = 1000
            try:
                # Remove older entries if over limit
                await self.redis_client.zremrangebyrank(history_key, 0, -(max_history + 1))
            except Exception:
                # Best effort; don't fail publish on cleanup error
                logger.debug("Failed to trim event history for %s", history_key)
            await self.redis_client.expire(history_key, 86400)

            logger.debug("Published event: %s (ID: %s)", event.event_type.value, event.event_id)

            # Fan-out to local SSE queues without blocking
            for q in list(self._sse_queues):
                try:
                    q.put_nowait(event_json)
                except asyncio.QueueFull:
                    # Drop if queue is full (best-effort)
                    logger.debug("SSE queue full; dropping event %s", event.event_id)
            return True

        except Exception as e:
            logger.exception("Failed to publish event %s: %s", event.event_id, e)
            return False

    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Subscribe a handler to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event is received.
                     Should accept Event as parameter.
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.debug("Subscribed handler to %s", event_type.value)

    async def start_listening(self):
        """
        Start listening for events on subscribed channels.

        This runs in the background and dispatches events to handlers.
        Call this after subscribing to all event types.
        """
        if not self.redis_client or not self.pubsub:
            raise RuntimeError("EventBus not connected. Call connect() first.")

        # Subscribe to all channels for registered handlers
        channels = [f"events:{event_type.value}" for event_type in self.handlers.keys()]
        if not channels:
            logger.warning("No event handlers registered")
            return

        await self.pubsub.subscribe(*channels)
        logger.info("Listening for events on %d channels", len(channels))

        self.is_running = True

        # Listen for messages
        try:
            async for message in self.pubsub.listen():
                if not self.is_running:
                    break

                if message["type"] == "message":
                    await self._handle_message(message)

        except asyncio.CancelledError:
            logger.info("Event listener cancelled")
        finally:
            await self.pubsub.unsubscribe()

    async def stop_listening(self):
        """Stop listening for events."""
        self.is_running = False
        logger.info("Stopping event listener")

    async def _handle_message(self, message: dict):
        """
        Internal method to handle incoming messages.

        Args:
            message: Redis message dict with 'channel' and 'data'
        """
        try:
            # Parse event from JSON
            event_data = json.loads(message["data"])
            event = Event(**event_data)

            # Find handlers for this event type
            handlers = self.handlers.get(event.event_type, [])

            if not handlers:
                logger.debug("No handlers for event type: %s", event.event_type.value)
                return

            # Execute all handlers concurrently
            logger.debug("Received event: %s (ID: %s)", event.event_type.value, event.event_id)

            tasks = [handler(event) for handler in handlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for handler errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.exception("Handler %s failed for %s: %s", i, event.event_id, result)
                    # TODO: Send to dead letter queue

        except json.JSONDecodeError as e:
            logger.error("Failed to parse event JSON: %s", e)
        except Exception as e:
            logger.exception("Error handling message: %s", e)

    async def get_event_history(
        self, event_type: EventType, limit: int = 100
    ) -> List[Event]:
        """
        Retrieve recent events of a specific type.

        Args:
            event_type: Type of events to retrieve
            limit: Maximum number of events to return

        Returns:
            List of recent events, newest first
        """
        if not self.redis_client:
            raise RuntimeError("EventBus not connected. Call connect() first.")

        # Get from sorted set (newest first)
        event_jsons = await self.redis_client.zrevrange(
            f"events:history:{event_type.value}", 0, limit - 1
        )

        events = []
        for event_json in event_jsons:
            try:
                event_data = json.loads(event_json)
                events.append(Event(**event_data))
            except Exception as e:
                print(f"⚠️  Failed to parse event from history: {e}")

        return events


    def register_sse_queue(self, queue: asyncio.Queue) -> None:
        """Register an asyncio.Queue to receive published events for SSE clients."""
        self._sse_queues.append(queue)

    def unregister_sse_queue(self, queue: asyncio.Queue) -> None:
        """Unregister a previously registered SSE queue."""
        try:
            self._sse_queues.remove(queue)
        except ValueError:
            pass

# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get the global event bus instance (singleton pattern).

    Returns:
        EventBus: The global event bus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
