"""SSE Endpoint for streaming agent thoughts and events.

This implementation avoids creating a new Redis pubsub per client by
registering an in-process asyncio.Queue with the global EventBus which
fans out published events. It enforces authentication, a per-user
concurrent connection limit, and a timeout for idle connections.
"""

import asyncio
import json
import os
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.events.bus import get_event_bus
from app.api.dependencies import get_current_user_id

router = APIRouter()

# SSE configuration
SSE_POLL_INTERVAL = float(os.getenv("SSE_POLL_INTERVAL", "0.5"))  # seconds
SSE_IDLE_TIMEOUT = int(os.getenv("SSE_IDLE_TIMEOUT", "300"))  # seconds
MAX_SSE_CONNECTIONS_PER_USER = int(os.getenv("MAX_SSE_CONNECTIONS_PER_USER", "3"))

# Track active SSE connections per user (simple in-memory limiter)
_sse_connections: dict[int, int] = {}


@router.get("/stream")
async def stream_events(request: Request, user_id: int = Depends(get_current_user_id)):
    """Stream events to an authenticated user via SSE.

    - Registers a temporary asyncio.Queue with the global EventBus.
    - Enforces max concurrent connections per user.
    - Sleeps when no events are available and yields keep-alive heartbeats.
    """
    # Simple per-user connection limit
    current = _sse_connections.get(user_id, 0)
    if current >= MAX_SSE_CONNECTIONS_PER_USER:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many SSE connections")

    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    event_bus = get_event_bus()
    event_bus.register_sse_queue(queue)
    _sse_connections[user_id] = current + 1

    async def event_generator():
        try:
            start = asyncio.get_event_loop().time()
            while True:
                elapsed = asyncio.get_event_loop().time() - start
                if elapsed > SSE_IDLE_TIMEOUT:
                    # Idle timeout reached; close connection
                    break

                try:
                    # Wait for event with a small timeout so we can detect disconnects
                    event_json = await asyncio.wait_for(queue.get(), timeout=SSE_POLL_INTERVAL)
                except asyncio.TimeoutError:
                    # If client disconnected while we were sleeping, stop
                    if await request.is_disconnected():
                        break
                    # Yield a heartbeat to keep connection alive
                    yield {"event": "heartbeat", "data": ""}
                    continue

                # Filter events by user_id if payload contains recipient info
                try:
                    payload = json.loads(event_json)
                    # Check top-level user_id first, then payload recipient
                    top_user = payload.get("user_id")
                    event_payload = payload.get("payload", {})
                    target_user = top_user or event_payload.get("user_id") or event_payload.get("recipient_user_id")
                    if target_user and int(target_user) != int(user_id):
                        # Skip events not intended for this user
                        continue
                except Exception:
                    # If parsing fails, still send raw event
                    pass

                yield {"data": event_json}

        finally:
            # Cleanup
            event_bus.unregister_sse_queue(queue)
            _sse_connections[user_id] = max(0, _sse_connections.get(user_id, 1) - 1)

    return EventSourceResponse(event_generator())
