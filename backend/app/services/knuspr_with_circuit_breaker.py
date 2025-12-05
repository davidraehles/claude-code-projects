"""
Knuspr MCP Client with Circuit Breaker integration.

This module provides a wrapper around KnusprMCPClient that integrates
circuit breaker protection for all external API calls.

Usage:
    from app.services.knuspr_with_circuit_breaker import get_protected_knuspr_client

    client = get_protected_knuspr_client(email, password)
    try:
        products = await client.search_products("milk")
    except CircuitBreakerError as e:
        # Circuit is open, service is down
        logger.warning(f"Knuspr service unavailable: {e}")
        # Return cached data or friendly error
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.services.knuspr_mcp_client import (
    KnusprMCPClient,
    KnusprCountry,
    KnusprProduct,
    DeliverySlot,
    KnusprCart,
    BatchAddResult
)
from app.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    get_circuit_breaker
)

logger = logging.getLogger(__name__)


class ProtectedKnusprMCPClient:
    """
    Knuspr MCP Client with circuit breaker protection.

    Wraps all external API calls with circuit breaker to prevent
    cascading failures when Knuspr API is experiencing issues.
    """

    def __init__(
        self,
        knuspr_client: KnusprMCPClient,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        """
        Initialize protected Knuspr client.

        Args:
            knuspr_client: Underlying KnusprMCPClient instance
            circuit_breaker: Optional circuit breaker (creates default if not provided)
        """
        self.client = knuspr_client

        # Get or create circuit breaker for Knuspr API
        if circuit_breaker:
            self.breaker = circuit_breaker
        else:
            # Configure circuit breaker for Knuspr API characteristics
            config = CircuitBreakerConfig(
                failure_threshold=5,  # Open after 5 failures
                success_threshold=2,  # Close after 2 successes in half-open
                timeout_seconds=60.0,  # Try again after 1 minute
                window_seconds=60.0,  # Count failures over 1 minute window
                half_open_max_calls=3  # Allow 3 test calls in half-open state
            )
            self.breaker = get_circuit_breaker("knuspr_api", config)

        logger.info("Protected Knuspr client initialized with circuit breaker")

    async def authenticate(self) -> bool:
        """
        Authenticate with Knuspr API through circuit breaker.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            return await self.breaker.call(self.client.authenticate)
        except CircuitBreakerError:
            logger.warning("Cannot authenticate: circuit breaker is OPEN")
            return False

    async def search_products(
        self,
        ingredient_name: str,
        max_results: int = 10,
        exact_match: bool = False
    ) -> List[KnusprProduct]:
        """
        Search products with circuit breaker protection.

        Args:
            ingredient_name: Name of ingredient to search
            max_results: Maximum results to return
            exact_match: Whether to require exact match

        Returns:
            List of KnusprProduct objects

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return await self.breaker.call(
            self.client.search_products,
            ingredient_name,
            max_results,
            exact_match
        )

    async def create_cart(
        self,
        items: List[Dict[str, Any]],
        delivery_slot_id: Optional[str] = None
    ) -> KnusprCart:
        """
        Create cart with circuit breaker protection.

        Args:
            items: List of items to add to cart
            delivery_slot_id: Optional delivery slot

        Returns:
            KnusprCart object

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return await self.breaker.call(
            self.client.create_cart,
            items,
            delivery_slot_id
        )

    async def get_delivery_slots(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[DeliverySlot]:
        """
        Get delivery slots with circuit breaker protection.

        Args:
            start_date: Earliest delivery date
            end_date: Latest delivery date

        Returns:
            List of DeliverySlot objects

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return await self.breaker.call(
            self.client.get_delivery_slots,
            start_date,
            end_date
        )

    async def select_delivery_slot(
        self,
        cart_id: str,
        slot_id: str
    ) -> bool:
        """
        Select delivery slot with circuit breaker protection.

        Args:
            cart_id: Cart ID
            slot_id: Slot ID

        Returns:
            True if successful

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return await self.breaker.call(
            self.client.select_delivery_slot,
            cart_id,
            slot_id
        )

    async def get_cart(self, cart_id: str) -> Optional[KnusprCart]:
        """
        Get cart with circuit breaker protection.

        Args:
            cart_id: Cart ID to retrieve

        Returns:
            KnusprCart object or None

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return await self.breaker.call(
            self.client.get_cart,
            cart_id
        )

    async def add_items_batch(
        self,
        items: List[Dict[str, Any]],
        batch_size: int = 10,
        max_retries: int = 3
    ) -> BatchAddResult:
        """
        Add items in batch with circuit breaker protection.

        Args:
            items: List of items to add
            batch_size: Items per batch
            max_retries: Max retry attempts

        Returns:
            BatchAddResult object

        Raises:
            CircuitBreakerError: If circuit is open
        """
        return await self.breaker.call(
            self.client.add_items_batch,
            items,
            batch_size,
            max_retries
        )

    async def close(self):
        """Close underlying client."""
        await self.client.close()

    def get_circuit_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.

        Returns:
            Dictionary with current metrics and state
        """
        return self.breaker.get_metrics()


def get_protected_knuspr_client(
    login_email: str,
    login_password: str,
    country: KnusprCountry = KnusprCountry.GERMANY,
    circuit_breaker: Optional[CircuitBreaker] = None
) -> ProtectedKnusprMCPClient:
    """
    Factory function to create a protected Knuspr client.

    Args:
        login_email: Knuspr account email
        login_password: Knuspr account password
        country: Target country
        circuit_breaker: Optional custom circuit breaker

    Returns:
        ProtectedKnusprMCPClient instance
    """
    knuspr_client = KnusprMCPClient(
        login_email=login_email,
        login_password=login_password,
        country=country
    )

    return ProtectedKnusprMCPClient(knuspr_client, circuit_breaker)
