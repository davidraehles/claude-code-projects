import asyncio

import pytest

from app.events import Event, EventType
from app.events.bus import get_event_bus


class DummyRedis:
    async def publish(self, *args, **kwargs):
        return 1

    async def zadd(self, *args, **kwargs):
        return None

    async def zremrangebyrank(self, *args, **kwargs):
        return None

    async def expire(self, *args, **kwargs):
        return None


@pytest.mark.asyncio
async def test_eventbus_sse_fanout_queue():
    bus = get_event_bus()

    # Simulate connected redis client
    bus.redis_client = DummyRedis()

    queue = asyncio.Queue()
    bus.register_sse_queue(queue)

    event = Event(event_type=EventType.AGENT_ERROR, correlation_id="c1", payload={"msg": "hello"}, user_id=1)

    ok = await bus.publish(event)
    assert ok is True

    # The queue should receive the event JSON string
    received = await asyncio.wait_for(queue.get(), timeout=1)
    # parse JSON to validate payload
    import json as _json
    parsed = _json.loads(received)
    assert parsed.get("payload", {}).get("msg") == "hello"

    bus.unregister_sse_queue(queue)
