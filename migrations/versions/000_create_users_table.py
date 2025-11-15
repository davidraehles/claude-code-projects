"""Create users table.

Revision ID: 000
Revises:
Create Date: 2025-11-14 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create users table with indexes."""

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False, comment="ISO 3166-1 alpha-2 country code"),
        sa.Column(
            "subscription_tier",
            sa.String(length=50),
            nullable=False,
            server_default="free",
            comment="Subscription level: free, basic, premium"
        ),
        sa.Column("subscription_expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="User preferences: language, theme, dietary preferences, etc."
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(), nullable=True, comment="Soft delete for GDPR compliance"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # Create indexes
    op.create_index(
        "idx_users_email",
        "users",
        ["email"],
        unique=True
    )
    op.create_index(
        "idx_users_subscription_expires",
        "users",
        ["subscription_expires_at"],
        unique=False
    )


def downgrade() -> None:
    """Drop users table."""

    # Drop indexes
    op.drop_index("idx_users_subscription_expires", table_name="users")
    op.drop_index("idx_users_email", table_name="users")

    # Drop table
    op.drop_table("users")
