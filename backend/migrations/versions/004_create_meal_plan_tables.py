"""create_meal_plan_tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-15

Creates tables for meal planning and grocery cart functionality.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create meal planning tables."""

    # Meal Plans table
    op.create_table(
        'meal_plans',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False, index=True),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('num_people', sa.Integer(), nullable=False, default=2),

        # Constraints and preferences (stored as JSON)
        sa.Column('dietary_restrictions', sa.JSON(), nullable=True, comment="List of dietary restrictions"),
        sa.Column('excluded_ingredients', sa.JSON(), nullable=True, comment="List of excluded ingredients"),
        sa.Column('target_calories_per_day', sa.Integer(), nullable=True),
        sa.Column('target_budget', sa.Float(), nullable=True, comment="Target budget in EUR"),
        sa.Column('preferred_cuisines', sa.JSON(), nullable=True, comment="List of preferred cuisines"),

        # Generated metadata
        sa.Column('total_recipes', sa.Integer(), nullable=False, default=0),
        sa.Column('total_calories', sa.Integer(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('optimization_score', sa.Float(), nullable=True, comment="Z3 solver optimization score"),

        # Status tracking
        sa.Column('status', sa.String(50), nullable=False, default='draft', index=True,
                  comment="draft, generating, ready, active, completed"),
        sa.Column('generation_time_seconds', sa.Float(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # Meal Plan Recipes (M2M relationship with scheduling info)
    op.create_table(
        'meal_plan_recipes',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('meal_plan_id', sa.BigInteger(), sa.ForeignKey('meal_plans.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('recipe_id', sa.BigInteger(), sa.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False, index=True),

        # Scheduling information
        sa.Column('day_number', sa.Integer(), nullable=False, comment="1-based day number in the plan"),
        sa.Column('meal_type', sa.String(50), nullable=False, comment="breakfast, lunch, dinner, snack"),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=False, default=2),

        # Nutritional tracking (calculated)
        sa.Column('calories', sa.Integer(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),

        # Position in the plan (for ordering)
        sa.Column('position', sa.Integer(), nullable=False, default=0),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Grocery Carts table
    op.create_table(
        'grocery_carts',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('meal_plan_id', sa.BigInteger(), sa.ForeignKey('meal_plans.id', ondelete='CASCADE'), nullable=True, index=True),

        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='active', index=True,
                  comment="active, ordered, completed"),

        # Totals
        sa.Column('total_items', sa.Integer(), nullable=False, default=0),
        sa.Column('total_cost', sa.Float(), nullable=True),

        # Knuspr integration
        sa.Column('knuspr_cart_id', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('knuspr_synced_at', sa.DateTime(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ordered_at', sa.DateTime(), nullable=True),
    )

    # Cart Items table
    op.create_table(
        'cart_items',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('cart_id', sa.BigInteger(), sa.ForeignKey('grocery_carts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('ingredient_id', sa.BigInteger(), sa.ForeignKey('ingredients.id', ondelete='SET NULL'), nullable=True),

        # Item details
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),

        # Pricing
        sa.Column('unit_price', sa.Float(), nullable=True),
        sa.Column('total_price', sa.Float(), nullable=True),

        # Source tracking (which recipes need this ingredient)
        sa.Column('recipe_ids', sa.JSON(), nullable=True, comment="List of recipe IDs that need this ingredient"),

        # Knuspr integration
        sa.Column('knuspr_product_id', sa.String(255), nullable=True),
        sa.Column('knuspr_url', sa.String(500), nullable=True),

        # Status
        sa.Column('is_purchased', sa.Boolean(), default=False, nullable=False),
        sa.Column('purchased_at', sa.DateTime(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Indexes for performance
    op.create_index('ix_meal_plans_user_status', 'meal_plans', ['user_id', 'status'])
    op.create_index('ix_meal_plans_dates', 'meal_plans', ['start_date', 'end_date'])
    op.create_index('ix_meal_plan_recipes_plan_day', 'meal_plan_recipes', ['meal_plan_id', 'day_number'])
    op.create_index('ix_meal_plan_recipes_plan_meal', 'meal_plan_recipes', ['meal_plan_id', 'meal_type'])
    op.create_index('ix_grocery_carts_user_status', 'grocery_carts', ['user_id', 'status'])
    op.create_index('ix_cart_items_cart', 'cart_items', ['cart_id'])


def downgrade() -> None:
    """Drop meal planning tables."""
    op.drop_table('cart_items')
    op.drop_table('grocery_carts')
    op.drop_table('meal_plan_recipes')
    op.drop_table('meal_plans')
