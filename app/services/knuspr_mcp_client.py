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
import importlib
import sys
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import os
from contextlib import asynccontextmanager

from tenacity import stop_after_attempt, wait_exponential, AsyncRetrying

try:
    logging.debug("Attempting to import mcp.ClientSession")
    from mcp import ClientSession, StdioServerParameters, McpError
    from mcp.client.stdio import stdio_client
    logging.info("Successfully imported mcp components")
except Exception as e:  # pragma: no cover
    logging.error(
        "Failed to import mcp components. Interpreter=%s, sys.path=%s, error=%s",
        sys.executable,
        sys.path,
        e,
        exc_info=True
    )
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None
    McpError = None


class ToolExecutionError(RuntimeError):
    """Local shim for MCP tool invocation errors."""

    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code


class ConnectionError(RuntimeError):
    """Local shim for MCP connection failures."""


def _map_mcp_errors(exc: Exception) -> Exception:
    if McpError and isinstance(exc, McpError):
        return ToolExecutionError(getattr(exc, "message", str(exc)), getattr(exc, "code", None))
    return exc


@asynccontextmanager
async def _create_mcp_session():
    mcp_url = os.getenv("ROHLIK_MCP_URL")

    # Check if we should run locally via stdio
    if not mcp_url or not mcp_url.startswith("http"):
        if ClientSession is None or StdioServerParameters is None or stdio_client is None:
             raise RuntimeError("mcp package components unavailable; ensure 'mcp' is installed")

        # Assume local execution if no URL or not HTTP
        # If mcp_url is set, treat it as path to script, otherwise default to sibling directory
        script_path = mcp_url
        if not script_path:
            # Default location relative to this project
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../rohlik-mcp-temp/dist/index.js"))

        if not os.path.exists(script_path):
             raise RuntimeError(f"Local MCP server script not found at: {script_path}")

        server_params = StdioServerParameters(
            command="node",
            args=[script_path],
            env={
                "ROHLIK_USERNAME": os.getenv("ROHLIK_USERNAME", ""),
                "ROHLIK_PASSWORD": os.getenv("ROHLIK_PASSWORD", ""),
                "ROHLIK_BASE_URL": os.getenv("ROHLIK_BASE_URL", "https://www.knuspr.de"),  # Use env var or default to DE
                **os.environ
            }
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
            return

    # Remote SSE connection
    try:
        from mcp.client.sse import sse_client
    except ImportError:
        raise RuntimeError("mcp package components unavailable; ensure 'mcp' is installed")

    async with sse_client(mcp_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


logger = logging.getLogger(__name__)


class KnusprCountry(str, Enum):
    """Supported Knuspr countries"""
    CZECH_REPUBLIC = "cz"
    GERMANY = "de"
    AUSTRIA = "at"


# Mapping from country code to domain
KNUSPR_COUNTRY_DOMAINS = {
    KnusprCountry.CZECH_REPUBLIC: "https://www.knuspr.cz",
    KnusprCountry.GERMANY: "https://www.knuspr.de",
    KnusprCountry.AUSTRIA: "https://www.knuspr.at",
    # Fallbacks for string values
    "cz": "https://www.knuspr.cz",
    "de": "https://www.knuspr.de",
    "at": "https://www.knuspr.at",
}


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
        country: KnusprCountry = KnusprCountry.GERMANY,
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

    def _session_context(self):
        return _create_mcp_session()

    def get_domain(self) -> str:
        """
        Get the domain URL for the current country.

        Returns:
            Domain URL (e.g., "https://www.knuspr.cz")
        """
        return KNUSPR_COUNTRY_DOMAINS.get(self.country, KNUSPR_COUNTRY_DOMAINS.get(self.country.value, "https://www.knuspr.de"))

    async def _call_tool(self, tool_name: str, **arguments) -> Dict[str, Any]:
        try:
            async with self._session_context() as session:
                # Sanitize sensitive fields in arguments
                sensitive_fields = {'password', 'email', 'username', 'token', 'secret', 'key', 'auth', 'credential'}
                sanitized_args = {
                    k: '***' if any(field in k.lower() for field in sensitive_fields) else v
                    for k, v in arguments.items()
                }
                logger.debug(f"Calling MCP tool '{tool_name}' with sanitized args: {sanitized_args}")
                response = await session.call_tool(tool_name, arguments=arguments)
                logger.debug(f"Received response from '{tool_name}': {response}")

                if hasattr(response, "result") and isinstance(response.result, dict):
                    return response.result
                if isinstance(response, dict):
                    return response
                if hasattr(response, "dict"):
                    return response.dict()
                return {"raw": response}
        except Exception as exc:
            logger.error(
                "MCP tool '%s' raised exception. Args=%s, Type=%s, Error=%s",
                tool_name,
                arguments,
                type(exc).__name__,
                exc,
                exc_info=True
            )
            wrapped = _map_mcp_errors(exc)
            logger.error(f"MCP tool '{tool_name}' failed: {wrapped}")
            raise wrapped

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

        Implements retry logic to handle transient auth failures:
        - Retries up to max_retries times with exponential backoff
        - Handles connection errors, timeouts, and API errors
        - Returns False on persistent failures

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            logger.info(f"Authenticating with Knuspr as {self.login_email}")
            logger.debug("Authentication will be validated via 'get_account_data'")

            # Use retry logic for transient failures
            async def auth_attempt():
                # The rohlik-mcp server handles authentication internally via env vars
                # We can verify authentication by making a simple call, e.g. to account data
                # or just assume it's working if we can connect.
                # Let's try to fetch account data to verify auth.
                response = await self._call_tool("get_account_data")
                logger.debug(f"Authentication verification response keys: {list(response.keys())}")
                return response

            response = await self._with_retry(auth_attempt)

            # If we get here without error, we are authenticated
            self.session_token = "implicit-session" # The MCP server manages the session
            self.authenticated = True
            logger.info("Authentication successful (verified via get_account_data)")
            return True

        except ToolExecutionError as exc:
            logger.error(f"Authentication verification failed (tool error): {exc}")
            self.authenticated = False
            return False
        except ConnectionError as exc:
            logger.error(f"Authentication connection error after retries: {exc}")
            self.authenticated = False
            return False
        except TimeoutError as exc:
            logger.error(f"Authentication timeout after retries: {exc}")
            self.authenticated = False
            return False
        except Exception as exc:
            logger.error(f"Authentication failed after retries: {exc}")
            self.authenticated = False
            return False

    async def _ensure_session(self):
        """
        Ensure we have a valid authenticated session.

        Attempts authentication if not already authenticated.
        Retries with exponential backoff on transient failures.

        Raises:
            RuntimeError: If authentication fails persistently
        """
        if not self.authenticated:
            success = await self.authenticate()
            if not success:
                raise RuntimeError("Failed to authenticate with Knuspr after retries")

    async def _with_retry(self, coro):
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.retry_backoff, min=1, max=10),
            reraise=True
        ):
            with attempt:
                return await coro()

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

        await self._ensure_session()

        async def _run():
            request_payload = {
                "product_name": ingredient_name,
                "country": self.country.value,
                "max_results": max_results,
                "exact_match": exact_match,
            }
            response = await self._call_tool(
                "search_products",
                **request_payload
            )

            products = []
            for product in response.get("products", []):
                products.append(KnusprProduct(
                    product_id=product.get("product_id"),
                    name=product.get("name"),
                    quantity=product.get("quantity", 1),
                    unit=self._normalize_knuspr_unit(product.get("unit", "pcs")),
                    price=product.get("price", 0.0),
                    available=product.get("available", False),
                    category=product.get("category", "unknown"),
                    image_url=product.get("image_url"),
                    confidence=product.get("confidence", 1.0)
                ))

            return products
        try:
            return await self._with_retry(_run)
        except ToolExecutionError as exc:
            logger.error(f"Product search failed: {exc}")
            raise RuntimeError(f"Knuspr product search failed: {exc}")
        except ConnectionError as exc:
            logger.error(f"Product search connection error: {exc}")
            raise RuntimeError(f"Knuspr product search connection error: {exc}")

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

        await self._ensure_session()

        async def _run():
            response = await self._call_tool(
                "create_cart",
                items=items,
                delivery_slot_id=delivery_slot_id
            )

            cart_data = response.get("cart") or {}
            cart_items = [
                KnusprProduct(
                    product_id=item.get("product_id"),
                    name=item.get("name", ""),
                    quantity=item.get("quantity", 1),
                    unit=self._normalize_knuspr_unit(item.get("unit", "pcs")),
                    price=item.get("price", 0.0),
                    available=item.get("available", False),
                    category=item.get("category", "unknown")
                )
                for item in cart_data.get("items", [])
            ]
            slot_data = cart_data.get("delivery_slot")
            delivery_slot = None
            if slot_data:
                delivery_slot = DeliverySlot(
                    slot_id=slot_data.get("slot_id"),
                    date=datetime.fromisoformat(slot_data.get("date")),
                    time_window=slot_data.get("time_window", ""),
                    price=slot_data.get("price", 0.0),
                    available=slot_data.get("available", False)
                )

            return KnusprCart(
                cart_id=cart_data.get("cart_id", ""),
                items=cart_items,
                total_price=cart_data.get("total_price", 0.0),
                delivery_slot=delivery_slot,
                created_at=datetime.fromisoformat(cart_data.get("created_at"))
                if cart_data.get("created_at") else None
            )
        try:
            return await self._with_retry(_run)
        except ToolExecutionError as exc:
            logger.error(f"Cart creation failed: {exc}")
            raise RuntimeError(f"Knuspr cart creation failed: {exc}")
        except ConnectionError as exc:
            logger.error(f"Cart creation connection error: {exc}")
            raise RuntimeError(f"Knuspr cart creation connection error: {exc}")

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

        await self._ensure_session()

        async def _run():
            response = await self._call_tool(
                "get_delivery_slots",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                country=self.country.value
            )

            slots = []
            for slot in response.get("delivery_slots", []):
                slots.append(DeliverySlot(
                    slot_id=slot.get("slot_id"),
                    date=datetime.fromisoformat(slot.get("date")),
                    time_window=slot.get("time_window", ""),
                    price=slot.get("price", 0.0),
                    available=slot.get("available", False)
                ))
            return slots
        try:
            return await self._with_retry(_run)
        except ToolExecutionError as exc:
            logger.error(f"Delivery slot fetch failed: {exc}")
            raise RuntimeError(f"Knuspr delivery slots failed: {exc}")
        except ConnectionError as exc:
            logger.error(f"Delivery slot connection error: {exc}")
            raise RuntimeError(f"Knuspr delivery slots connection error: {exc}")

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

        await self._ensure_session()

        async def _run():
            response = await self._call_tool(
                "select_delivery_slot",
                cart_id=cart_id,
                slot_id=slot_id
            )
            return bool(response.get("success"))
        try:
            return await self._with_retry(_run)
        except ToolExecutionError as exc:
            logger.error(f"Slot selection failed: {exc}")
            return False
        except ConnectionError as exc:
            logger.error(f"Slot selection connection error: {exc}")
            return False

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

        await self._ensure_session()

        async def _run():
            response = await self._call_tool(
                "get_cart",
                cart_id=cart_id
            )
            cart_data = response.get("cart")
            if not cart_data:
                return None

            items = [
                KnusprProduct(
                    product_id=item.get("product_id"),
                    name=item.get("name", ""),
                    quantity=item.get("quantity", 1),
                    unit=self._normalize_knuspr_unit(item.get("unit", "pcs")),
                    price=item.get("price", 0.0),
                    available=item.get("available", False),
                    category=item.get("category", "unknown")
                )
                for item in cart_data.get("items", [])
            ]
            slot_data = cart_data.get("delivery_slot")
            delivery_slot = None
            if slot_data:
                delivery_slot = DeliverySlot(
                    slot_id=slot_data.get("slot_id"),
                    date=datetime.fromisoformat(slot_data.get("date")),
                    time_window=slot_data.get("time_window", ""),
                    price=slot_data.get("price", 0.0),
                    available=slot_data.get("available", False)
                )

            return KnusprCart(
                cart_id=cart_data.get("cart_id", ""),
                items=items,
                total_price=cart_data.get("total_price", 0.0),
                delivery_slot=delivery_slot,
                created_at=datetime.fromisoformat(cart_data.get("created_at"))
                if cart_data.get("created_at") else None
            )
        try:
            return await self._with_retry(_run)
        except ToolExecutionError as exc:
            logger.error(f"Cart retrieval failed: {exc}")
            raise RuntimeError(f"Knuspr cart retrieval failed: {exc}")
        except ConnectionError as exc:
            logger.error(f"Cart retrieval connection error: {exc}")
            raise RuntimeError(f"Knuspr cart retrieval connection error: {exc}")

    async def close(self):
        """Clean up resources and logout from Knuspr"""
        self.authenticated = False
        self.session_token = None
