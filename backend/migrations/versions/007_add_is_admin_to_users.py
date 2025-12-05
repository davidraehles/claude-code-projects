"""Add is_admin field to users table for admin authorization.

Revision ID: 007_add_is_admin_to_users
Revises: 006_create_rate_limit_tables
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_add_is_admin_to_users'
down_revision = '006_create_rate_limit_tables'
branch_labels = None
depends_on = None


def upgrade():
    """Add is_admin column to users table."""
    # Add is_admin column with default False
    op.add_column(
        'users',
        sa.Column(
            'is_admin',
            sa.Boolean(),
            nullable=False,
            default=False,
            comment='Whether user has admin privileges'
        )
    )

    print("✅ Added is_admin column to users table")


def downgrade():
    """Remove is_admin column from users table."""
    op.drop_column('users', 'is_admin')

    print("✅ Removed is_admin column from users table")
