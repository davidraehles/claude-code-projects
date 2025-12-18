"""
Base Agent Class.

Defines the standard interface for all agents in the system, including
lifecycle management, event handling, and capability discovery.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

from pydantic import BaseModel
from app.events.bus import EventBus
from app.events import Event, EventType

logger = logging.getLogger(__name__)

class CapabilityManifest(BaseModel):
    """Defines what an agent can do."""
    name: str
    version: str
    description: str
    capabilities: List[str]
    input_events: List[EventType]
    output_events: List[EventType]

class Agent(ABC):
    """
    Abstract base class for all agents.

    Agents are autonomous units that:
    1. Listen for specific events
    2. Process data
    3. Publish results as new events
    4. Maintain their own state
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.manifest = self.get_manifest()
        self.is_running = False
        self.logger = logging.getLogger(f"agent.{self.manifest.name}")

    @abstractmethod
    def get_manifest(self) -> CapabilityManifest:
        """Return the agent's capability manifest."""
        pass

    async def start(self):
        """Start the agent and subscribe to events."""
        self.is_running = True
        self.logger.info(f"Starting agent: {self.manifest.name}")
        await self._setup_subscriptions()

    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        self.logger.info(f"Stopping agent: {self.manifest.name}")

    async def _setup_subscriptions(self):
        """Subscribe to events defined in manifest."""
        for event_type in self.manifest.input_events:
            self.event_bus.subscribe(event_type, self.handle_event)

    @abstractmethod
    async def handle_event(self, event: Event):
        """Process incoming events."""
        pass

    async def publish(self, event_type: EventType, payload: Dict[str, Any], correlation_id: Optional[str] = None):
        """Publish an event to the bus."""
        event = Event(
            type=event_type,
            source=self.manifest.name,
            payload=payload,
            correlation_id=correlation_id
        )
        await self.event_bus.publish(event)
