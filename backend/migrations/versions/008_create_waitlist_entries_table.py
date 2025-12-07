"""Create waitlist_entries table for Go Cart rebranding waitlist.

Revision ID: 008_create_waitlist_entries_table
Revises: 007_add_is_admin_to_users
Create Date: 2025-12-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_create_waitlist_entries_table'
down_revision = '007_add_is_admin_to_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create waitlist_entries table
    op.create_table('waitlist_entries',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
    sa.Column('verification_token', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('verified_at', sa.DateTime(), nullable=True),
    sa.Column('invited_at', sa.DateTime(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_waitlist_entries_created_at'), 'waitlist_entries', ['created_at'], unique=False)
    op.create_index(op.f('ix_waitlist_entries_email'), 'waitlist_entries', ['email'], unique=False)
    op.create_index(op.f('ix_waitlist_entries_status'), 'waitlist_entries', ['status'], unique=False)
    op.create_index(op.f('ix_waitlist_entries_verification_token'), 'waitlist_entries', ['verification_token'], unique=False)

    print("✅ Created waitlist_entries table with indexes")


def downgrade() -> None:
    op.drop_index(op.f('ix_waitlist_entries_verification_token'), table_name='waitlist_entries')
    op.drop_index(op.f('ix_waitlist_entries_status'), table_name='waitlist_entries')
    op.drop_index(op.f('ix_waitlist_entries_email'), table_name='waitlist_entries')
    op.drop_index(op.f('ix_waitlist_entries_created_at'), table_name='waitlist_entries')
    op.drop_table('waitlist_entries')

    print("✅ Dropped waitlist_entries table")
