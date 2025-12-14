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


@dataclass
class BatchItemResult:
    """Result for a single item in batch operation"""
    name: str
    quantity: float
    unit: str
    success: bool
    knuspr_product_id: Optional[str] = None
    knuspr_product_name: Optional[str] = None
    error_message: Optional[str] = None
    match_confidence: float = 0.0
    retry_count: int = 0


@dataclass
class BatchAddResult:
    """Result of batch add operation"""
    total_items: int
    succeeded_items: List[BatchItemResult]
    failed_items: List[BatchItemResult]
    partial_matches: List[BatchItemResult]
    cart_id: Optional[str] = None
    cart_url: Optional[str] = None

    @property
    def success_count(self) -> int:
        """Number of successfully added items"""
        return len(self.succeeded_items)

    @property
    def failure_count(self) -> int:
        """Number of failed items"""
        return len(self.failed_items)

    @property
    def partial_count(self) -> int:
        """Number of partial matches"""
        return len(self.partial_matches)


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

                # Handle CallToolResult from mcp library
                content_blocks = []
                if hasattr(response, "content"):
                    content_blocks = response.content
                elif isinstance(response, dict) and "content" in response:
                    content_blocks = response["content"]

                # Parse text content
                full_text = ""
                if content_blocks:
                    for block in content_blocks:
                        # block can be TextContent object or dict
                        if hasattr(block, "type") and block.type == "text":
                            full_text += block.text
                        elif isinstance(block, dict) and block.get("type") == "text":
                            full_text += block.get("text", "")

                if full_text:
                    try:
                        import json
                        return json.loads(full_text)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse tool response as JSON: {full_text}")
                        # Fallback to returning raw text if not JSON
                        return {"raw_text": full_text}

                # Fallback for older behavior or different structures
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

    async def add_items_batch(
        self,
        items: List[Dict[str, Any]],
        batch_size: int = 10,
        max_retries: int = 3
    ) -> BatchAddResult:
        """
        Add multiple items to Knuspr cart in batches with retry logic.

        This method:
        1. Authenticates if not already authenticated
        2. Searches for each item to get Knuspr product IDs
        3. Batches items into groups for efficient API calls
        4. Retries failed items up to max_retries times
        5. Returns detailed results with success/failure tracking

        Args:
            items: List of dicts with keys:
                - name: str (ingredient name)
                - quantity: float
                - unit: str (g, ml, pcs, etc.)
                - category: str (optional)
            batch_size: Number of items to process per batch (default: 10)
            max_retries: Maximum retry attempts for failed items (default: 3)

        Returns:
            BatchAddResult with succeeded_items, failed_items, and partial_matches

        Raises:
            RuntimeError: If authentication fails
            ValueError: If items list is empty
        """
        if not items:
            raise ValueError("Items list cannot be empty")

        await self._ensure_session()

        logger.info(f"Starting batch add operation for {len(items)} items")

        succeeded_items: List[BatchItemResult] = []
        failed_items: List[BatchItemResult] = []
        partial_matches: List[BatchItemResult] = []

        # Track cart creation
        cart_id: Optional[str] = None
        cart_items_to_add: List[Dict[str, Any]] = []

        # Process items in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            logger.debug(f"Processing batch {i // batch_size + 1} with {len(batch)} items")

            for item in batch:
                item_name = item.get("name", "")
                item_quantity = item.get("quantity", 1.0)
                item_unit = item.get("unit", "pcs")
                retry_count = 0

                # Search for product with retries
                product_found = False
                best_match: Optional[KnusprProduct] = None

                while retry_count < max_retries and not product_found:
                    try:
                        # Search for product
                        logger.debug(f"Searching for product: {item_name} (attempt {retry_count + 1})")
                        products = await self.search_products(
                            ingredient_name=item_name,
                            max_results=5,
                            exact_match=False
                        )

                        if not products:
                            logger.warning(f"No products found for: {item_name}")
                            retry_count += 1
                            await asyncio.sleep(0.5 * retry_count)  # Exponential backoff
                            continue

                        # Get best match (first result is usually best)
                        best_match = products[0]

                        # Check match quality
                        if best_match.confidence >= 0.8:
                            # High confidence match
                            product_found = True
                            logger.info(f"Found product for {item_name}: {best_match.name} (confidence: {best_match.confidence})")
                        elif best_match.confidence >= 0.5:
                            # Partial match
                            product_found = True
                            logger.info(f"Partial match for {item_name}: {best_match.name} (confidence: {best_match.confidence})")
                        else:
                            # Low confidence, retry
                            retry_count += 1
                            await asyncio.sleep(0.5 * retry_count)
                            continue

                    except Exception as e:
                        logger.error(f"Error searching for {item_name}: {str(e)}")
                        retry_count += 1
                        await asyncio.sleep(0.5 * retry_count)
                        continue

                # Process result
                if best_match and product_found:
                    # Prepare item for cart
                    cart_item = {
                        "product_id": best_match.product_id,
                        "quantity": item_quantity,
                        "unit": item_unit
                    }
                    cart_items_to_add.append(cart_item)

                    result = BatchItemResult(
                        name=item_name,
                        quantity=item_quantity,
                        unit=item_unit,
                        success=True,
                        knuspr_product_id=best_match.product_id,
                        knuspr_product_name=best_match.name,
                        match_confidence=best_match.confidence,
                        retry_count=retry_count
                    )

                    if best_match.confidence >= 0.8:
                        succeeded_items.append(result)
                    else:
                        partial_matches.append(result)
                else:
                    # Failed to find product
                    failed_items.append(BatchItemResult(
                        name=item_name,
                        quantity=item_quantity,
                        unit=item_unit,
                        success=False,
                        error_message=f"Product not found after {max_retries} attempts",
                        retry_count=retry_count
                    ))

        # Create cart with all successfully matched items
        if cart_items_to_add:
            try:
                logger.info(f"Creating cart with {len(cart_items_to_add)} items")
                knuspr_cart = await self.create_cart(cart_items_to_add)
                cart_id = knuspr_cart.cart_id

                # Generate cart URL
                domain = self.get_domain()
                cart_url = f"{domain}/cart/{cart_id}" if cart_id else None

                logger.info(f"Cart created successfully: {cart_id}")
            except Exception as e:
                logger.error(f"Failed to create cart: {str(e)}")
                # Move all items to failed
                for item in succeeded_items + partial_matches:
                    failed_items.append(BatchItemResult(
                        name=item.name,
                        quantity=item.quantity,
                        unit=item.unit,
                        success=False,
                        error_message=f"Cart creation failed: {str(e)}",
                        retry_count=item.retry_count
                    ))
                succeeded_items.clear()
                partial_matches.clear()
                cart_id = None
                cart_url = None
        else:
            cart_url = None
            logger.warning("No items to add to cart")

        result = BatchAddResult(
            total_items=len(items),
            succeeded_items=succeeded_items,
            failed_items=failed_items,
            partial_matches=partial_matches,
            cart_id=cart_id,
            cart_url=cart_url
        )

        logger.info(
            f"Batch operation complete: {result.success_count} succeeded, "
            f"{result.partial_count} partial matches, {result.failure_count} failed"
        )

        return result

    async def get_cart_content(self) -> Dict[str, Any]:
        """
        Get current cart contents from Knuspr.

        Returns:
            Dict containing cart items, total price, and other cart details
        """
        await self._ensure_session()
        return await self._call_tool("get_cart_content")

    async def remove_from_cart(self, product_ids: List[int]) -> Dict[str, Any]:
        """
        Remove products from the cart.

        Args:
            product_ids: List of product IDs to remove

        Returns:
            Dict with removal results
        """
        await self._ensure_session()
        return await self._call_tool("remove_from_cart", product_ids=product_ids)

    async def get_frequent_items(self) -> Dict[str, Any]:
        """
        Get frequently ordered items for the current user.

        Returns:
            Dict containing list of frequently purchased products
        """
        await self._ensure_session()
        return await self._call_tool("get_frequent_items")

    async def get_meal_suggestions(
        self,
        meal_type: str = "dinner",
        items_count: int = 10,
        orders_to_analyze: int = 5,
        prefer_frequent: bool = True
    ) -> Dict[str, Any]:
        """
        Get meal suggestions from Knuspr/Rohlik based on meal type.

        Args:
            meal_type: Type of meal - "breakfast", "lunch", "dinner", "snack", "baking", "drinks", or "healthy"
            items_count: Number of items to suggest (3-30, default 10)
            orders_to_analyze: Number of recent orders to analyze (1-20, default 5)
            prefer_frequent: Prefer frequently ordered items (default True)

        Returns:
            Dict containing meal recommendations and recipes
        """
        await self._ensure_session()
        return await self._call_tool(
            "get_meal_suggestions",
            meal_type=meal_type,
            items_count=items_count,
            orders_to_analyze=orders_to_analyze,
            prefer_frequent=prefer_frequent
        )

    async def get_order_history(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user's order history.

        Args:
            limit: Optional maximum number of orders to retrieve

        Returns:
            Dict containing list of past orders
        """
        await self._ensure_session()
        params = {}
        if limit is not None:
            params["limit"] = limit
        return await self._call_tool("get_order_history", **params)

    async def get_order_detail(self, order_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific order.

        Args:
            order_id: The ID of the order to retrieve

        Returns:
            Dict containing order details
        """
        await self._ensure_session()
        return await self._call_tool("get_order_detail", order_id=order_id)

    async def get_upcoming_orders(self) -> Dict[str, Any]:
        """
        Get upcoming scheduled orders.

        Returns:
            Dict containing list of upcoming/scheduled deliveries
        """
        await self._ensure_session()
        return await self._call_tool("get_upcoming_orders")

    async def get_premium_info(self) -> Dict[str, Any]:
        """
        Get user's premium/subscription information.

        Returns:
            Dict containing premium status and benefits
        """
        await self._ensure_session()
        return await self._call_tool("get_premium_info")

    async def get_reusable_bags_info(self) -> Dict[str, Any]:
        """
        Get information about reusable bags credits.

        Returns:
            Dict containing bag credits and deposit information
        """
        await self._ensure_session()
        return await self._call_tool("get_reusable_bags_info")

    async def get_shopping_list(self, shopping_list_id: str) -> Dict[str, Any]:
        """
        Get user's saved shopping list by ID.

        Args:
            shopping_list_id: The ID of the shopping list to retrieve

        Returns:
            Dict containing saved shopping list items
        """
        await self._ensure_session()
        return await self._call_tool("get_shopping_list", shopping_list_id=shopping_list_id)

    async def get_shopping_scenarios(self) -> Dict[str, Any]:
        """
        Get shopping scenarios and usage examples.

        Returns:
            Dict containing recommended shopping scenarios
        """
        await self._ensure_session()
        return await self._call_tool("get_shopping_scenarios")

    async def get_announcements(self) -> Dict[str, Any]:
        """
        Get service announcements and notifications.

        Returns:
            Dict containing current announcements
        """
        await self._ensure_session()
        return await self._call_tool("get_announcements")

    async def get_account_data(self) -> Dict[str, Any]:
        """
        Get user's account information.

        Returns:
            Dict containing account details (email, address, preferences)
        """
        await self._ensure_session()
        return await self._call_tool("get_account_data")

    async def get_delivery_info(self) -> Dict[str, Any]:
        """
        Get general delivery service information.

        Returns:
            Dict containing delivery zones, fees, and service details
        """
        await self._ensure_session()
        return await self._call_tool("get_delivery_info")

    async def close(self):
        """Clean up resources and logout from Knuspr"""
        self.authenticated = False
        self.session_token = None
