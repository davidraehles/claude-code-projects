"""merge_multiple_heads

Revision ID: 1f5528e26798
Revises: 006, 008_create_waitlist_entries_table
Create Date: 2025-12-14 00:26:01.713491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f5528e26798'
down_revision: Union[str, Sequence[str], None] = ('006', '008_create_waitlist_entries_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
