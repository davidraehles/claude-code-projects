"""create_ingredients_tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-15

Creates tables for ingredient taxonomy, allergens, and substitution rules.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create ingredient intelligence tables.

    Tables:
    - ingredients: Core ingredient taxonomy
    - allergens: Common allergen definitions
    - ingredient_allergens: M2M relationship
    - substitution_rules: Ingredient substitution mappings
    """

    # Allergens table
    op.create_table(
        'allergens',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(20), nullable=False, comment="low, medium, high, severe"),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Ingredient categories (enum-like table)
    op.create_table(
        'ingredient_categories',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['ingredient_categories.id'], ondelete='SET NULL'),
    )

    # Main ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('normalized_name', sa.String(255), nullable=False, unique=True, index=True,
                  comment="Lowercase, singular form for matching"),
        sa.Column('category_id', sa.BigInteger(), nullable=True, index=True),
        sa.Column('aliases', sa.JSON(), nullable=True,
                  comment="List of alternative names/spellings"),
        sa.Column('base_unit', sa.String(50), nullable=True,
                  comment="Standard unit: gram, ml, piece, etc."),
        sa.Column('unit_conversions', sa.JSON(), nullable=True,
                  comment="Conversion factors to base unit"),
        sa.Column('nutrition_per_100g', sa.JSON(), nullable=True,
                  comment="Calories, protein, carbs, fat, fiber, etc."),
        sa.Column('seasonal_availability', sa.JSON(), nullable=True,
                  comment="Array of months when in season"),
        sa.Column('storage_tips', sa.Text(), nullable=True),
        sa.Column('shelf_life_days', sa.Integer(), nullable=True),
        sa.Column('is_common', sa.Boolean(), default=True, index=True,
                  comment="Is this a commonly used ingredient?"),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['category_id'], ['ingredient_categories.id'], ondelete='SET NULL'),
    )

    # Ingredient-Allergen relationship (many-to-many)
    op.create_table(
        'ingredient_allergens',
        sa.Column('ingredient_id', sa.BigInteger(), nullable=False),
        sa.Column('allergen_id', sa.BigInteger(), nullable=False),
        sa.Column('severity_override', sa.String(20), nullable=True,
                  comment="Override allergen severity for this ingredient"),
        sa.PrimaryKeyConstraint('ingredient_id', 'allergen_id'),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['allergen_id'], ['allergens.id'], ondelete='CASCADE'),
    )

    # Substitution rules
    op.create_table(
        'substitution_rules',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('ingredient_id', sa.BigInteger(), nullable=False, index=True,
                  comment="Original ingredient"),
        sa.Column('substitute_id', sa.BigInteger(), nullable=False, index=True,
                  comment="Substitute ingredient"),
        sa.Column('ratio', sa.Float(), nullable=False, default=1.0,
                  comment="Substitution ratio (e.g., 1.5 means use 150%)"),
        sa.Column('quality_score', sa.Float(), nullable=True,
                  comment="How good is this substitution? 0-1 scale"),
        sa.Column('notes', sa.Text(), nullable=True,
                  comment="Usage notes and tips"),
        sa.Column('context', sa.JSON(), nullable=True,
                  comment="When is this substitution appropriate? (baking, cooking, etc.)"),
        sa.Column('is_vegan', sa.Boolean(), default=False),
        sa.Column('is_vegetarian', sa.Boolean(), default=False),
        sa.Column('is_gluten_free', sa.Boolean(), default=False),
        sa.Column('is_dairy_free', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['substitute_id'], ['ingredients.id'], ondelete='CASCADE'),
    )

    # Indexes for performance
    op.create_index('ix_ingredients_category', 'ingredients', ['category_id'])
    op.create_index('ix_ingredients_common', 'ingredients', ['is_common'])
    op.create_index('ix_substitutions_ingredient', 'substitution_rules', ['ingredient_id'])
    op.create_index('ix_substitutions_substitute', 'substitution_rules', ['substitute_id'])
    op.create_index('ix_substitutions_quality', 'substitution_rules', ['quality_score'])


def downgrade() -> None:
    """Drop ingredient intelligence tables."""
    op.drop_table('substitution_rules')
    op.drop_table('ingredient_allergens')
    op.drop_table('ingredients')
    op.drop_table('ingredient_categories')
    op.drop_table('allergens')
