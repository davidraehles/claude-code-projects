"""Add dietary tags to recipes table.

Revision ID: 005_add_dietary_tags
Revises: 004_create_meal_plan_tables
Create Date: 2025-11-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_dietary_tags'
down_revision = '004_create_meal_plan_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Add dietary_tags column to recipes table."""
    # Add dietary_tags column (JSON type)
    op.add_column('recipes', sa.Column('dietary_tags', sa.JSON(), nullable=True,
                                       comment='Dietary tags: vegan, vegetarian, gluten_free, etc.'))

    print("✅ Added dietary_tags column to recipes table")


def downgrade():
    """Remove dietary_tags column from recipes table."""
    op.drop_column('recipes', 'dietary_tags')

    print("✅ Removed dietary_tags column from recipes table")
