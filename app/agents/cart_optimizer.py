"""
Cart Optimizer Agent

Orchestrates conversion of meal plans to Knuspr grocery shopping carts:
1. Extracts ingredients from meal plan
2. Searches Knuspr for matching products
3. Groups items by store section for efficient shopping
4. Selects optimal delivery slot (earliest/cheapest)
5. Creates cart and stores in PostgreSQL

Works with Knuspr MCP tools to handle all grocery ordering.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import time

from app.events.bus import EventBus
from app.events import Event, EventType
from app.models.meal_plan import MealPlan, MealPlanRecipe, GroceryCart, CartItem
from app.models.recipe import Recipe
from app.monitoring.metrics import (
    cart_creation_total,
    cart_creation_duration_seconds,
    cart_value_eur,
    cart_items_count
)

logger = logging.getLogger(__name__)


@dataclass
class MappedIngredient:
    """Ingredient with Knuspr product mapping"""
    original_ingredient: str
    product_id: str
    product_name: str
    quantity: float
    unit: str
    price: float
    category: str


class CartOptimizerAgent:
    """
    Cart Optimizer Agent - Converts meal plans to Knuspr shopping carts

    Responsibilities:
    - Extract ingredients from meal plan recipes
    - Map ingredients to Knuspr products (via MCP client)
    - Group products by store section
    - Select optimal delivery slot
    - Create and manage shopping carts
    """

    def __init__(self, knuspr_client, ingredient_mapper, db, event_bus: Optional[EventBus] = None):
        """
        Initialize Cart Optimizer Agent.

        Args:
            knuspr_client: KnusprMCPClient for Knuspr API access
            ingredient_mapper: IngredientMapper for ingredient→product mapping
            db: Database connection for cart storage
            event_bus: EventBus for publishing events
        """
        self.knuspr_client = knuspr_client
        self.ingredient_mapper = ingredient_mapper
        self.db = db
        self.event_bus = event_bus

    async def create_cart_from_meal_plan(
        self,
        meal_plan_id: str,
        user_id: str,
        db,
        credential_manager,
        delivery_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create Knuspr cart from meal plan.

        Full workflow:
        1. Fetch meal plan and extract all ingredients
        2. Map ingredients to Knuspr products
        3. Create cart with mapped products
        4. Fetch available delivery slots
        5. Select optimal slot based on preferences
        6. Store cart in database
        7. Return cart with summary

        Args:
            meal_plan_id: ID of meal plan to convert
            user_id: User ID (for credential lookup)
            delivery_preferences: Dict with keys:
                - preferred_dates: List[date] (preferred delivery dates)
                - preferred_time_slot: str ("morning", "afternoon", "evening")
                - budget_optimization: bool (choose cheapest vs earliest)

        Returns:
            Dict with cart info and metadata:
            {
                "cart_id": "...",
                "knuspr_url": "https://knuspr.cz/cart/...",
                "total_price": 1234.56,
                "item_count": 23,
                "delivery_slot": {...},
                "items_by_section": {...},
                "unavailable_items": [...]
            }

        Raises:
            ValueError: If meal plan not found or empty
            RuntimeError: If cart creation fails
        """
        start_time = time.time()
        try:
            logger.info(f"Creating cart from meal plan {meal_plan_id} for user {user_id}")

            # Step 1: Fetch meal plan and extract ingredients
            ingredients = await self._extract_ingredients_from_meal_plan(meal_plan_id)
            if not ingredients:
                raise ValueError(f"Meal plan {meal_plan_id} has no ingredients")

            logger.info(f"Extracted {len(ingredients)} ingredients from meal plan")

            # Step 2: Map ingredients to Knuspr products
            mapped_products, unmapped = await self.ingredient_mapper.map_ingredients_to_products(
                ingredients
            )

            if not mapped_products:
                raise RuntimeError(f"Failed to map any ingredients to Knuspr products")

            logger.info(f"Mapped {len(mapped_products)} products, {len(unmapped)} unavailable")

            # Step 3: Create cart with mapped products
            cart_items = [
                {
                    "product_id": p["product_id"],
                    "quantity": p["quantity"],
                    "unit": p["unit"]
                }
                for p in mapped_products
            ]

            cart = await self.knuspr_client.create_cart(cart_items)
            logger.info(f"Created Knuspr cart: {cart.cart_id}")

            # Step 4: Fetch available delivery slots
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)
            available_slots = await self.knuspr_client.get_delivery_slots(start_date, end_date)

            if not available_slots:
                logger.warning("No delivery slots available")
            else:
                logger.info(f"Found {len(available_slots)} available delivery slots")

            # Step 5: Select optimal delivery slot
            selected_slot = self._select_delivery_slot(
                available_slots,
                delivery_preferences or {}
            )

            if selected_slot:
                await self.knuspr_client.select_delivery_slot(cart.cart_id, selected_slot.slot_id)
                cart.delivery_slot = selected_slot
                logger.info(f"Selected delivery slot: {selected_slot.slot_id}")

            # Step 6: Group items by section
            items_by_section = await self.ingredient_mapper.categorize_products(mapped_products)

            # Step 7: Store cart in database
            await self._store_cart_in_database(
                user_id=user_id,
                meal_plan_id=meal_plan_id,
                cart_id=cart.cart_id,
                items_by_section=items_by_section,
                total_price=cart.total_price,
                delivery_slot=selected_slot
            )

            # Step 8: Return comprehensive cart summary
            result = {
                "cart_id": cart.cart_id,
                "knuspr_url": f"https://knuspr.cz/cart/{cart.cart_id}",  # TODO: Use actual domain
                "total_price": cart.total_price,
                "item_count": len(mapped_products),
                "delivery_slot": {
                    "slot_id": selected_slot.slot_id if selected_slot else None,
                    "date": selected_slot.date.isoformat() if selected_slot else None,
                    "time_window": selected_slot.time_window if selected_slot else None,
                    "price": selected_slot.price if selected_slot else None,
                } if selected_slot else None,
                "items_by_section": {
                    category: [
                        {
                            "name": p["name"],
                            "quantity": p["quantity"],
                            "unit": p["unit"],
                            "price": p["price"]
                        }
                        for p in items
                    ]
                    for category, items in items_by_section.items()
                },
                "unavailable_items": unmapped,
                "created_at": datetime.utcnow().isoformat()
            }

            # Record metrics
            duration = time.time() - start_time
            cart_creation_total.labels(status="success").inc()
            cart_creation_duration_seconds.observe(duration)
            cart_value_eur.observe(cart.total_price)
            cart_items_count.observe(len(mapped_products))

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(Event(
                    event_type=EventType.CART_CREATED,
                    correlation_id=meal_plan_id,  # Using meal_plan_id as correlation_id for now
                    user_id=int(user_id) if user_id.isdigit() else None,
                    payload={
                        "cart_id": cart.cart_id,
                        "meal_plan_id": meal_plan_id,
                        "total_price": cart.total_price,
                        "item_count": len(mapped_products)
                    }
                ))

            logger.info(f"Cart creation complete: {result['cart_id']}")
            return result

        except Exception as e:
            logger.error(f"Cart creation failed: {str(e)}")

            # Record failure metrics
            cart_creation_total.labels(status="failure").inc()

            # Publish failure event
            if self.event_bus:
                await self.event_bus.publish(Event(
                    event_type=EventType.CART_CREATION_FAILED,
                    correlation_id=meal_plan_id,
                    user_id=int(user_id) if user_id.isdigit() else None,
                    payload={
                        "meal_plan_id": meal_plan_id,
                        "error": str(e)
                    }
                ))

            raise

    def _select_delivery_slot(
        self,
        available_slots: List,
        preferences: Dict
    ) -> Optional[Any]:
        """
        Select optimal delivery slot based on preferences.

        Selection strategy:
        1. Filter by preferred dates if specified
        2. Filter by preferred time window if specified
        3. Choose based on optimization preference (cheapest vs earliest)

        Args:
            available_slots: List of available DeliverySlot objects
            preferences: Dict with preferred_dates, preferred_time_slot, budget_optimization

        Returns:
            Selected DeliverySlot or None if no match
        """
        if not available_slots:
            return None

        slots = available_slots[:]

        # Filter by preferred dates
        preferred_dates = preferences.get("preferred_dates", [])
        if preferred_dates:
            slots = [
                s for s in slots
                if any(s.date.date() == pd for pd in preferred_dates)
            ]

        # Filter by preferred time window
        time_slot = preferences.get("preferred_time_slot", "afternoon")
        time_filters = {
            "morning": ("08:00", "12:00"),
            "afternoon": ("12:00", "18:00"),
            "evening": ("18:00", "21:00")
        }

        if time_slot in time_filters:
            start_time, end_time = time_filters[time_slot]
            slots = [
                s for s in slots
                if start_time <= s.time_window.split("-")[0] < end_time
            ]

        if not slots:
            # Fall back to any available slot
            slots = available_slots

        # Sort by preference
        budget_opt = preferences.get("budget_optimization", False)
        if budget_opt:
            # Choose cheapest
            slots.sort(key=lambda s: s.price)
        else:
            # Choose earliest
            slots.sort(key=lambda s: s.date)

        return slots[0] if slots else None

    async def _extract_ingredients_from_meal_plan(self, meal_plan_id: str) -> List[str]:
        """
        Extract all unique ingredients from meal plan recipes.

        Args:
            meal_plan_id: ID of meal plan

        Returns:
            List of unique ingredient strings
        """
        logger.debug(f"Extracting ingredients from meal plan {meal_plan_id}")

        try:
            # Query recipes associated with the meal plan
            recipes = self.db.query(Recipe).join(
                MealPlanRecipe, Recipe.id == MealPlanRecipe.recipe_id
            ).filter(
                MealPlanRecipe.meal_plan_id == meal_plan_id
            ).all()

            all_ingredients = []
            for recipe in recipes:
                # Recipe ingredients are stored as JSON list of dicts or strings
                if isinstance(recipe.ingredients, list):
                    for ing in recipe.ingredients:
                        if isinstance(ing, dict):
                            # Extract name from dict (e.g. {"name": "Milk", ...})
                            name = ing.get("name") or ing.get("ingredient")
                            if name:
                                all_ingredients.append(name)
                        elif isinstance(ing, str):
                            all_ingredients.append(ing)

            # Deduplicate
            unique_ingredients = list(set(all_ingredients))
            logger.info(f"Found {len(unique_ingredients)} unique ingredients in {len(recipes)} recipes")
            return unique_ingredients

        except Exception as e:
            logger.error(f"Failed to extract ingredients: {str(e)}")
            return []

    async def _store_cart_in_database(
        self,
        user_id: str,
        meal_plan_id: str,
        cart_id: str,
        items_by_section: Dict,
        total_price: float,
        delivery_slot: Optional[Any]
    ) -> None:
        """
        Store cart information in PostgreSQL.

        Args:
            user_id: User ID
            meal_plan_id: Meal plan ID
            cart_id: Knuspr cart ID
            items_by_section: Dict of products by category
            total_price: Total cart price
            delivery_slot: Selected delivery slot or None
        """
        logger.debug(f"Storing cart {cart_id} in database for user {user_id}")

        try:
            # Create GroceryCart record
            cart = GroceryCart(
                user_id=int(user_id),
                meal_plan_id=int(meal_plan_id),
                name=f"Knuspr Cart {datetime.utcnow().strftime('%Y-%m-%d')}",
                status="active",
                total_items=sum(len(items) for items in items_by_section.values()),
                total_cost=total_price,
                knuspr_cart_id=cart_id,
                knuspr_synced_at=datetime.utcnow()
            )
            self.db.add(cart)
            self.db.flush() # Get ID

            # Create CartItem records
            for section, items in items_by_section.items():
                for item in items:
                    cart_item = CartItem(
                        cart_id=cart.id,
                        name=item["name"],
                        quantity=item["quantity"],
                        unit=item["unit"],
                        category=section,
                        unit_price=item.get("price", 0),
                        total_price=item.get("price", 0) * item["quantity"],
                        knuspr_product_id=item.get("product_id"),
                        is_purchased=False
                    )
                    self.db.add(cart_item)

            self.db.commit()
            logger.info(f"Stored cart {cart.id} in database")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store cart in database: {str(e)}")
            raise

    async def group_items_by_section(
        self,
        items: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Group shopping cart items by store section.

        Store sections:
        - produce: Fresh vegetables, fruits
        - dairy: Milk, cheese, butter, yogurt
        - meat: Fresh/frozen meat, fish
        - canned_goods: Canned vegetables, beans, tomatoes
        - frozen: Frozen vegetables, berries
        - grains: Bread, pasta, rice
        - oils_vinegar: Oils, vinegars, condiments

        Args:
            items: List of product dicts

        Returns:
            Dict mapping section names to product lists
        """
        return self.ingredient_mapper.categorize_products(items)

    async def regenerate_cart(
        self,
        cart_id: str,
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Regenerate cart with changes (e.g., remove unavailable item, change slot).

        Args:
            cart_id: ID of cart to update
            changes: Dict with possible keys:
                - remove_items: List[product_id]
                - add_items: List[{product_id, quantity, unit}]
                - delivery_slot_id: str

        Returns:
            Updated cart dict
        """
        # TODO: Fetch existing cart, apply changes, regenerate
        logger.info(f"Regenerating cart {cart_id} with changes: {changes}")
        return {}
