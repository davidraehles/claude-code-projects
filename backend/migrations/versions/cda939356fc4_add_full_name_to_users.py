"""add_full_name_to_users

Revision ID: cda939356fc4
Revises: 1f5528e26798
Create Date: 2025-12-15 19:14:39.575328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cda939356fc4'
down_revision: Union[str, Sequence[str], None] = '1f5528e26798'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add full_name column to users table
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove full_name column from users table
    op.drop_column('users', 'full_name')
