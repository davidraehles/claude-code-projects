"""
Knuspr MCP Client Wrapper

Integrates with Knuspr grocery store via Claude MCP tools for:
- Product search and lookup
- Cart creation and management
- Delivery slot retrieval
- Price optimization

This service bridges the meal planning system with Knuspr's grocery ordering API.
"""

import logging
import asyncio
import difflib
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class KnusprCountry(str, Enum):
    """Supported Knuspr countries"""
    CZECH_REPUBLIC = "cz"
    SLOVAKIA = "sk"
    POLAND = "pl"


@dataclass
class KnusprProduct:
    """Knuspr product information"""
    product_id: str
    name: str
    quantity: float
    unit: str  # "g", "ml", "pcs", etc.
    price: float
    available: bool
    category: str  # "produce", "dairy", "meat", etc.
    image_url: Optional[str] = None
    confidence: float = 1.0  # Matching confidence (0-1)


@dataclass
class DeliverySlot:
    """Knuspr delivery slot"""
    slot_id: str
    date: datetime
    time_window: str  # "09:00-12:00"
    price: float
    available: bool


@dataclass
class KnusprCart:
    """Knuspr shopping cart"""
    cart_id: str
    items: List[KnusprProduct]
    total_price: float
    delivery_slot: Optional[DeliverySlot] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class KnusprMCPClient:
    """
    Knuspr MCP Client - Wrapper around Knuspr grocery API

    Provides async methods for:
    - Searching products by ingredient name
    - Creating/managing shopping carts
    - Retrieving delivery slots
    - Price optimization

    Uses Claude's MCP tools as the interface to Knuspr services.
    """

    def __init__(
        self,
        login_email: str,
        login_password: str,
        country: KnusprCountry = KnusprCountry.CZECH_REPUBLIC,
        api_timeout: int = 30,
        max_retries: int = 3,
        retry_backoff: float = 1.5
    ):
        """
        Initialize Knuspr MCP client.

        Args:
            login_email: Knuspr account email
            login_password: Knuspr account password
            country: Target country (cz, sk, pl)
            api_timeout: API request timeout in seconds
            max_retries: Max retry attempts for failed requests
            retry_backoff: Exponential backoff multiplier (retry_delay = base * backoff^attempt)
        """
        self.login_email = login_email
        self.login_password = login_password
        self.country = country
        self.api_timeout = api_timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.session_token: Optional[str] = None
        self.authenticated = False

        logger.info(f"Initialized KnusprMCPClient for {country.value}")

    def _normalize_knuspr_unit(self, unit: str) -> str:
        """Normalize Knuspr-specific units to standard units."""
        unit = unit.lower().strip()
        mapping = {
            "ks": "pcs",
            "kus": "pcs",
            "bal": "pkg",
            "balení": "pkg",
            "g": "g",
            "kg": "kg",
            "ml": "ml",
            "l": "l"
        }
        return mapping.get(unit, unit)

    async def authenticate(self) -> bool:
        """
        Authenticate with Knuspr API using stored credentials.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            logger.info(f"Authenticating with Knuspr as {self.login_email}")

            # TODO: Call MCP tool to authenticate
            # client = MCPClient()
            # response = await client.authenticate({
            #     "email": self.login_email,
            #     "password": self.login_password,
            #     "country": self.country.value
            # })
            # self.session_token = response.get("session_token")

            # For now, simulate successful auth
            self.session_token = "mock_session_token"
            self.authenticated = True
            logger.info("Authentication successful")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self.authenticated = False
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
        reraise=True
    )
    async def search_products(
        self,
        ingredient_name: str,
        max_results: int = 10,
        exact_match: bool = False
    ) -> List[KnusprProduct]:
        """
        Search Knuspr for products matching an ingredient.

        Args:
            ingredient_name: Name of ingredient to search (e.g., "kidney beans")
            max_results: Maximum number of results to return
            exact_match: If True, require exact match; if False, allow fuzzy matching

        Returns:
            List of KnusprProduct objects sorted by relevance

        Raises:
            RuntimeError: If not authenticated
            TimeoutError: If API request times out
        """
        if not self.authenticated:
            await self.authenticate()

        if not self.authenticated:
            raise RuntimeError("Failed to authenticate with Knuspr")

        try:
            logger.info(f"Searching Knuspr for '{ingredient_name}'")

            # TODO: Call MCP tool to search products
            # client = MCPClient()
            # response = await client.search_products({
            #     "query": ingredient_name,
            #     "country": self.country.value,
            #     "max_results": max_results,
            #     "exact_match": exact_match,
            #     "session_token": self.session_token
            # })

            # For now, return mock results
            mock_products = [
                KnusprProduct(
                    product_id=f"knuspr-{ingredient_name.replace(' ', '-')}-1",
                    name=f"{ingredient_name.title()} 400g",
                    quantity=400,
                    unit=self._normalize_knuspr_unit("g"),
                    price=45.99,
                    available=True,
                    category="canned_goods",
                    confidence=0.95
                )
            ]

            if not exact_match and mock_products:
                # Sort by similarity to ingredient_name
                def similarity(p):
                    return difflib.SequenceMatcher(None, ingredient_name.lower(), p.name.lower()).ratio()

                mock_products.sort(key=similarity, reverse=True)

            logger.info(f"Found {len(mock_products)} products for '{ingredient_name}'")
            return mock_products[:max_results]
        except asyncio.TimeoutError:
            logger.error(f"Search timeout for '{ingredient_name}'")
            raise TimeoutError(f"Knuspr search timeout for '{ingredient_name}'")
        except Exception as e:
            logger.error(f"Product search failed: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
        reraise=True
    )
    async def create_cart(
        self,
        items: List[Dict[str, Any]],
        delivery_slot_id: Optional[str] = None
    ) -> KnusprCart:
        """
        Create a shopping cart with specified items.

        Args:
            items: List of dicts with keys:
                - product_id: str (Knuspr product ID)
                - quantity: float
                - unit: str (optional, override product unit)
            delivery_slot_id: Optional delivery slot to pre-select

        Returns:
            KnusprCart object

        Raises:
            RuntimeError: If not authenticated
            ValueError: If items list is empty
        """
        if not self.authenticated:
            await self.authenticate()

        if not items:
            raise ValueError("Cart must contain at least one item")

        try:
            logger.info(f"Creating Knuspr cart with {len(items)} items")

            # TODO: Call MCP tool to create cart
            # client = MCPClient()
            # response = await client.create_cart({
            #     "items": items,
            #     "session_token": self.session_token,
            #     "delivery_slot_id": delivery_slot_id
            # })

            # For now, return mock cart
            mock_products = [
                KnusprProduct(
                    product_id=item.get("product_id"),
                    name=f"Product {item.get('product_id')}",
                    quantity=item.get("quantity", 1),
                    unit=item.get("unit", "pcs"),
                    price=50.0,
                    available=True,
                    category="unknown"
                )
                for item in items
            ]

            total_price = sum(p.price * p.quantity for p in mock_products)
            cart = KnusprCart(
                cart_id=f"cart-{datetime.utcnow().timestamp()}",
                items=mock_products,
                total_price=total_price
            )

            logger.info(f"Cart created: {cart.cart_id} with total {total_price} CZK")
            return cart
        except Exception as e:
            logger.error(f"Cart creation failed: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
        reraise=True
    )
    async def get_delivery_slots(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[DeliverySlot]:
        """
        Get available delivery slots for a date range.

        Args:
            start_date: Earliest delivery date
            end_date: Latest delivery date

        Returns:
            List of available DeliverySlot objects sorted by date

        Raises:
            RuntimeError: If not authenticated
            ValueError: If date range is invalid
        """
        if not self.authenticated:
            await self.authenticate()

        if start_date > end_date:
            raise ValueError("start_date must be before end_date")

        if start_date < datetime.utcnow():
            start_date = datetime.utcnow()

        try:
            logger.info(f"Fetching delivery slots from {start_date} to {end_date}")

            # TODO: Call MCP tool to get slots
            # client = MCPClient()
            # response = await client.get_delivery_slots({
            #     "start_date": start_date.isoformat(),
            #     "end_date": end_date.isoformat(),
            #     "country": self.country.value,
            #     "session_token": self.session_token
            # })

            # For now, return mock slots
            slots = []
            current_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
            while current_date <= end_date:
                for hour in [9, 15, 18]:
                    slots.append(DeliverySlot(
                        slot_id=f"slot-{current_date.date()}-{hour:02d}",
                        date=current_date.replace(hour=hour),
                        time_window=f"{hour:02d}:00-{hour+3:02d}:00",
                        price=69.0 if hour == 18 else 49.0,
                        available=True
                    ))
                current_date += timedelta(days=1)

            logger.info(f"Found {len(slots)} delivery slots")
            return slots
        except Exception as e:
            logger.error(f"Delivery slot fetch failed: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
        reraise=True
    )
    async def select_delivery_slot(
        self,
        cart_id: str,
        slot_id: str
    ) -> bool:
        """
        Select a delivery slot for a cart.

        Args:
            cart_id: ID of cart to update
            slot_id: ID of delivery slot to select

        Returns:
            True if successful, False otherwise
        """
        if not self.authenticated:
            await self.authenticate()

        try:
            logger.info(f"Selecting delivery slot {slot_id} for cart {cart_id}")

            # TODO: Call MCP tool to select slot
            # client = MCPClient()
            # response = await client.select_delivery_slot({
            #     "cart_id": cart_id,
            #     "slot_id": slot_id,
            #     "session_token": self.session_token
            # })

            logger.info(f"Successfully selected slot {slot_id}")
            return True
        except Exception as e:
            logger.error(f"Slot selection failed: {str(e)}")
            raise

    async def get_cart(self, cart_id: str) -> Optional[KnusprCart]:
        """
        Retrieve cart details from Knuspr.

        Args:
            cart_id: ID of cart to retrieve

        Returns:
            KnusprCart object or None if not found
        """
        if not self.authenticated:
            await self.authenticate()

        try:
            logger.info(f"Retrieving cart {cart_id}")

            # TODO: Call MCP tool to get cart
            # client = MCPClient()
            # response = await client.get_cart({
            #     "cart_id": cart_id,
            #     "session_token": self.session_token
            # })

            logger.info(f"Cart retrieved: {cart_id}")
            return None  # TODO: Parse and return actual cart
        except Exception as e:
            logger.error(f"Cart retrieval failed: {str(e)}")
            return None

    async def close(self):
        """Clean up resources and logout from Knuspr"""
        try:
            if self.authenticated:
                # TODO: Call MCP tool to logout
                logger.info("Logged out from Knuspr")
                self.authenticated = False
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
