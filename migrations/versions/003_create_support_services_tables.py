"""create_support_services_tables

Revision ID: 003
Revises: 002
Create Date: 2025-11-15

Creates tables for support services: failed_events (DLQ) and notifications.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create support services tables."""

    # Failed Events table (Dead Letter Queue)
    op.create_table(
        'failed_events',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('event_id', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('event_type', sa.String(255), nullable=False, index=True),
        sa.Column('correlation_id', sa.String(255), nullable=True, index=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True, index=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=False),
        sa.Column('error_type', sa.String(255), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=0, nullable=False),
        sa.Column('max_retries', sa.Integer(), default=3, nullable=False),
        sa.Column('status', sa.String(50), default='pending', nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_retry_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
    )

    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, default='info'),
        sa.Column('is_read', sa.Boolean(), default=False, nullable=False, index=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('read_at', sa.DateTime(), nullable=True),
    )

    # Indexes
    op.create_index('ix_failed_events_status_retry', 'failed_events', ['status', 'retry_count'])
    op.create_index('ix_notifications_user_unread', 'notifications', ['user_id', 'is_read'])


def downgrade() -> None:
    """Drop support services tables."""
    op.drop_table('notifications')
    op.drop_table('failed_events')
