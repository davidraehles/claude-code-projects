"""add_delivery_slot_and_unavailable_items

Revision ID: 006
Revises: 005
Create Date: 2025-12-11

Adds delivery_slot_json and unavailable_items_json columns to grocery_carts table
to persist Knuspr delivery slot information and unavailable items.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_add_dietary_tags'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add delivery slot and unavailable items columns to grocery_carts."""

    # Add delivery_slot_json column
    op.add_column(
        'grocery_carts',
        sa.Column(
            'delivery_slot_json',
            sa.JSON(),
            nullable=True,
            comment='Selected delivery slot details (slot_id, date, time_window, price, availability)'
        )
    )

    # Add unavailable_items_json column
    op.add_column(
        'grocery_carts',
        sa.Column(
            'unavailable_items_json',
            sa.JSON(),
            nullable=True,
            comment='List of items that could not be mapped to Knuspr products'
        )
    )


def downgrade() -> None:
    """Remove delivery slot and unavailable items columns from grocery_carts."""

    op.drop_column('grocery_carts', 'unavailable_items_json')
    op.drop_column('grocery_carts', 'delivery_slot_json')
