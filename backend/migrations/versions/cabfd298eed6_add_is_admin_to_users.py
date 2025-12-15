"""Add is_admin field to users table for admin authorization.

Revision ID: cabfd298eed6
Revises: 963f23794be8
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cabfd298eed6'
down_revision = '963f23794be8'
branch_labels = None
depends_on = None


def upgrade():
    """Add is_admin column to users table."""
    # Add is_admin column with server-side default (important for existing rows)
    op.add_column(
        'users',
        sa.Column(
            'is_admin',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment='Whether user has admin privileges'
        )
    )

    # Explicitly set existing rows to False (in case server_default doesn't apply)
    op.execute('UPDATE users SET is_admin = FALSE WHERE is_admin IS NULL')

    print("✅ Added is_admin column to users table")


def downgrade():
    """Remove is_admin column from users table."""
    op.drop_column('users', 'is_admin')

    print("✅ Removed is_admin column from users table")
