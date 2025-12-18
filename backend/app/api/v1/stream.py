"""
SSE Endpoint for streaming agent thoughts.
"""

from fastapi import APIRouter, Request, Depends
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from app.events.bus import EventBus, EventType
from app.config.redis import get_redis_client

router = APIRouter()

@router.get("/stream")
async def stream_events(request: Request):
    """
    Stream agent thoughts and system events to the client via SSE.
    """
    async def event_generator():
        redis = await get_redis_client()
        pubsub = redis.pubsub()
        # Subscribe to all agent events
        await pubsub.psubscribe("events:*")

        try:
            while True:
                if await request.is_disconnected():
                    break

                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = message['data']
                    yield {"data": data}

                await asyncio.sleep(0.1)
        finally:
            await pubsub.punsubscribe()
            await pubsub.close()
            await redis.close()

    return EventSourceResponse(event_generator())
