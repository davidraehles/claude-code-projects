from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.events.bus import get_event_bus
from app.events import Event, EventType


class DummyRedis:
    async def publish(self, *args, **kwargs):
        return 1

    async def zadd(self, *args, **kwargs):
        return None

    async def zremrangebyrank(self, *args, **kwargs):
        return None

    async def expire(self, *args, **kwargs):
        return None


def test_stream_endpoint_auth_and_event_delivery(monkeypatch):
    # Override auth to return user 1
    from app.api.dependencies import get_current_user_id
    app.dependency_overrides[get_current_user_id] = lambda: 1

    client = TestClient(app)

    bus = get_event_bus()
    bus.redis_client = DummyRedis()

    # Start streaming and publish a single event, then assert it's received
    with client.stream("GET", "/api/v1/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        # Publish an event for user 1
        event = Event(event_type=EventType.MEAL_PLAN_GENERATED, correlation_id="c2", payload={"msg": "ok"}, user_id=1)
        # publish asynchronously
        import asyncio
        asyncio.get_event_loop().run_until_complete(bus.publish(event))
        # read a few lines from the streaming response
        # httpx's Response.iter_lines() does not accept the same kwargs as requests
        # so use the iterator as provided and stop when we get at least one non-empty line
        lines = []
        for chunk in response.iter_lines():
            if not chunk:
                continue
            lines.append(chunk)
            if len(lines) >= 1:
                break

        assert any("ok" in line or "MEAL_PLAN_GENERATED" in line for line in lines)
