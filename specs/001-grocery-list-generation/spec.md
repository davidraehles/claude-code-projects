# Feature Specification: Automated Grocery List Generation with Knuspr Integration

**Feature Branch**: `001-grocery-list-generation`
**Created**: 2025-11-29
**Status**: Draft
**Input**: User description: "After creating a meal plan, generate a grocery list aggregated by recipe or category showing portion sizes. Same ingredients from multiple recipes should be combined with indication of source. Users can click to fill their Knuspr cart, triggering authentication if needed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Aggregated Grocery List After Meal Plan Creation (Priority: P1)

After completing meal plan generation, users should immediately see a comprehensive grocery list derived from all recipes in their plan, with quantities adjusted for the portion size they selected. The list should show which recipes contribute each ingredient, allowing users to understand their shopping needs at a glance.

**Why this priority**: This is the core value proposition. Without this, users cannot see what groceries they need, making the meal planning feature incomplete. It's the foundation for all subsequent shopping actions.

**Independent Test**: User can generate a meal plan and immediately view a consolidated grocery list with accurate portion-adjusted quantities. The list shows ingredient source information from recipes.

**Acceptance Scenarios**:

1. **Given** a meal plan is created for 2 people × 7 days × 3 meals, **When** meal plan generation completes, **Then** the user sees a grocery list with all unique ingredients from all recipes, with quantities multiplied by total servings needed (42 meals)
2. **Given** the grocery list is displayed, **When** the user examines an ingredient (e.g., "flour"), **Then** they see it comes from multiple recipes (e.g., "Pancakes, Bread, Cookies") with individual quantities that sum to the total
3. **Given** the grocery list is displayed, **When** the user reviews the data, **Then** the total quantity for each ingredient is accurate based on portion size (e.g., "2 cups flour" if recipes need 0.5, 0.75, 0.75 cups respectively)

---

### User Story 2 - Switch Between Recipe and Category View (Priority: P2)

Users should be able to toggle between two viewing modes: organize groceries by which recipe they come from, or organize them by shopping category (produce, dairy, meat, etc.). This helps with different shopping strategies and store layouts.

**Why this priority**: While viewing by recipe shows source clarity, many users prefer shopping by category following store layout. This improves usability and shopping efficiency for the majority of users.

**Independent Test**: User can toggle between recipe-based and category-based views, with ingredient aggregation working correctly in both views.

**Acceptance Scenarios**:

1. **Given** a grocery list is displayed in recipe view, **When** the user clicks the "View by Category" button, **Then** the list reorganizes showing Produce, Dairy, Meat, etc., with all ingredients properly categorized and aggregated
2. **Given** a grocery list is displayed in category view with "flour" showing sources from 3 recipes, **When** the user toggles back to recipe view, **Then** recipes are displayed with their ingredient requirements, and "flour" shows the aggregated quantity with a note "(combined from Pancakes, Bread)"
3. **Given** an ingredient appears in multiple recipes, **When** viewing by recipe, **Then** the ingredient is listed under each recipe with its individual quantity, but the aggregated total is shown separately or in the summary

---

### User Story 3 - Fill Knuspr Cart with Selected Ingredients (Priority: P1)

Users should be able to send all (or selected) groceries from their list to their Knuspr shopping cart with a single click. If they haven't authenticated with Knuspr yet, the system should initiate the Knuspr authentication flow.

**Why this priority**: This is critical for completing the user journey - converting meal planning into actual shopping. Without this, the meal plan feature creates work (users still need to manually add items to Knuspr), rather than reducing work.

**Independent Test**: User can click "Start Filling Knuspr Cart" and either (a) see items added to their cart if authenticated, or (b) be guided through Knuspr authentication if not yet authenticated.

**Acceptance Scenarios**:

1. **Given** a user has created a meal plan and sees the grocery list, **When** they click "Start Filling Knuspr Cart", **Then** the system checks if Knuspr credentials are stored
2. **Given** the user has previously authenticated with Knuspr, **When** they click "Start Filling Knuspr Cart", **Then** the system uses their stored credentials to add all selected ingredients to their Knuspr cart and shows a success message
3. **Given** the user has NOT authenticated with Knuspr, **When** they click "Start Filling Knuspr Cart", **Then** the system redirects to Knuspr.de authentication, and after successful authentication, adds the selected ingredients to their cart
4. **Given** some ingredients have been deselected (unchecked) by the user, **When** they click "Start Filling Knuspr Cart", **Then** only selected/checked ingredients are added to the cart
5. **Given** the system is adding items to the Knuspr cart, **When** an API error occurs, **Then** the user sees a clear error message with instructions (retry, contact support, etc.)

---

### Edge Cases

- What happens when an ingredient has no category mapping and cannot be categorized automatically? → System should use "Other" category and flag for manual review
- What happens when a recipe ingredient doesn't match any Knuspr product? → System should show a warning and skip that ingredient with user notification
- What happens when the user has multiple Knuspr accounts? → System authenticates with one account (either remembering the last used or prompting for selection)
- What happens if the user edits the meal plan after viewing the grocery list? → The grocery list should update to reflect the new recipes and quantities
- What happens if Knuspr API is temporarily unavailable? → System should show a helpful message and allow the user to retry or try again later
- What happens if a user has already selected some items in their Knuspr cart? → System should add meal plan items without clearing existing cart items

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a grocery list immediately after meal plan creation, extracting all ingredients from all recipes in the meal plan
- **FR-002**: System MUST adjust ingredient quantities based on the portion size (number of people × number of days × meals per day) selected in the meal plan
- **FR-003**: System MUST aggregate identical ingredients from multiple recipes into a single line item showing combined quantity
- **FR-004**: System MUST indicate ingredient source(s) - showing which recipes contribute to each ingredient quantity (e.g., "Flour (from Pancakes, Bread, Cookies)")
- **FR-005**: System MUST provide a "View by Recipe" display mode showing recipes with their individual ingredient requirements
- **FR-006**: System MUST provide a "View by Category" display mode organizing ingredients by shopping category (Produce, Dairy, Meat, Seafood, Bakery, Pantry, Frozen, Beverages, Snacks, Other)
- **FR-007**: System MUST allow users to toggle between recipe and category view modes without losing their selection state (checked/unchecked items)
- **FR-008**: System MUST provide a "Start Filling Knuspr Cart" button that sends selected ingredients to the user's Knuspr cart
- **FR-009**: System MUST check for stored Knuspr credentials before attempting to add items to cart
- **FR-010**: System MUST initiate Knuspr OAuth authentication flow if credentials are not available, redirecting to Knuspr.de
- **FR-011**: System MUST store Knuspr authentication tokens securely for future use (with proper token refresh/expiration handling)
- **FR-012**: System MUST only add selected/checked ingredients to the Knuspr cart (support partial selection)
- **FR-013**: System MUST handle Knuspr API errors gracefully and provide user-friendly error messages
- **FR-014**: System MUST update the grocery list if the meal plan is modified (new recipes added/removed)
- **FR-015**: System MUST map meal plan ingredients to Knuspr product catalog, handling cases where direct matches don't exist
- **FR-016**: System MUST show a loading state while communicating with Knuspr API
- **FR-017**: System MUST confirm successful cart population with a summary of added items count

### Key Entities

- **GroceryItem**: Represents an ingredient from a recipe with quantity, unit, and category. Includes references to source recipes.
- **AggregatedGroceryItem**: Represents a combined ingredient from multiple recipes with total quantity and list of source recipes with their individual quantities.
- **GroceryList**: Contains aggregated items derived from a meal plan, organized by either recipe or category. Tracks user selections (checked/unchecked).
- **KnusprCredentials**: Stores OAuth tokens and refresh tokens for Knuspr API access, with expiration tracking.
- **KnusprProduct**: Represents a product in Knuspr catalog with matching algorithm for meal plan ingredients.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view a complete grocery list within 2 seconds of meal plan completion
- **SC-002**: Ingredient aggregation is 100% accurate - no duplicate ingredients or incorrect quantity calculations
- **SC-003**: Users can switch between recipe and category views within 1 click and 1 second load time
- **SC-004**: First-time Knuspr authentication happens within 3 steps and takes less than 2 minutes
- **SC-005**: Users can fill their Knuspr cart with one click and see confirmation within 5 seconds
- **SC-006**: 95% of common meal plan ingredients are successfully matched to Knuspr products without manual intervention
- **SC-007**: Cart population succeeds for 99% of requests (tracking errors and success rates)
- **SC-008**: Knuspr authentication tokens remain valid and refresh automatically without user intervention

## Assumptions

- Ingredients are stored in recipes with standard units (cups, grams, ml, etc.) that can be used for scaling calculations
- Knuspr provides an API for searching products and adding items to carts
- Knuspr authentication uses OAuth2 with redirect-based flow
- Recipe ingredient data is available in structured format with ingredient names and quantities
- Users may have Knuspr accounts and are willing to authenticate
- Ingredient-to-Knuspr-product mapping can be done with fuzzy matching or a maintained catalog

## Out of Scope

- Manual ingredient editing in the grocery list (users cannot add/remove/modify ingredients, they work with what's generated)
- Price comparison or alternate product suggestions
- Integration with grocery stores other than Knuspr
- Nutritional analysis or macro tracking for ingredients
- Shopping list sharing or collaboration features
- Barcode scanning or in-store shopping features
- Recurring/automated grocery ordering

## Dependencies

- Knuspr API availability and product catalog
- Existing meal plan generation feature (must have valid recipes with ingredients)
- Authentication service for Knuspr OAuth flow
- Recipe data structure must include ingredient quantities and units
