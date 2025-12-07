"""Create rate limiting tables.

Revision ID: 006_create_rate_limit_tables
Revises: 005_add_dietary_tags
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "006_create_rate_limit_tables"
down_revision = "005_add_dietary_tags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create rate limiting tables."""

    # Create rate_limit_policies table
    op.create_table(
        "rate_limit_policies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("endpoint_pattern", sa.String(length=255), nullable=False),
        sa.Column("limit_type", sa.String(length=20), nullable=False),
        sa.Column("requests_per_window", sa.Integer(), nullable=False),
        sa.Column("window_seconds", sa.Integer(), nullable=False),
        sa.Column("burst_multiplier", sa.Float(), nullable=False, server_default="1.5"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
            onupdate=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for rate_limit_policies
    op.create_index(
        op.f("ix_rate_limit_policies_id"), "rate_limit_policies", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_rate_limit_policies_endpoint_pattern"),
        "rate_limit_policies",
        ["endpoint_pattern"],
        unique=True,
    )
    op.create_index(
        "idx_rate_limit_policies_enabled", "rate_limit_policies", ["enabled"], unique=False
    )

    # Create rate_limit_overrides table
    op.create_table(
        "rate_limit_overrides",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("endpoint_pattern", sa.String(length=255), nullable=False),
        sa.Column("limit_type", sa.String(length=20), nullable=False),
        sa.Column("requests_per_window", sa.Integer(), nullable=False),
        sa.Column("window_seconds", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
            onupdate=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for rate_limit_overrides
    op.create_index(
        op.f("ix_rate_limit_overrides_id"), "rate_limit_overrides", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_rate_limit_overrides_user_id"), "rate_limit_overrides", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_rate_limit_overrides_expires_at"),
        "rate_limit_overrides",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        "idx_rate_limit_overrides_user_expires",
        "rate_limit_overrides",
        ["user_id", "expires_at"],
        unique=False,
    )

    # Create rate_limit_whitelist table
    op.create_table(
        "rate_limit_whitelist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column("limit_type", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
            onupdate=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for rate_limit_whitelist
    op.create_index(
        op.f("ix_rate_limit_whitelist_id"), "rate_limit_whitelist", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_rate_limit_whitelist_identifier"),
        "rate_limit_whitelist",
        ["identifier"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rate_limit_whitelist_limit_type"),
        "rate_limit_whitelist",
        ["limit_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rate_limit_whitelist_enabled_ix"),
        "rate_limit_whitelist",
        ["enabled"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rate_limit_whitelist_expires_at"),
        "rate_limit_whitelist",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        "idx_rate_limit_whitelist_identifier_type",
        "rate_limit_whitelist",
        ["identifier", "limit_type"],
        unique=False,
    )

    print("✅ Created rate_limit_policies table with indexes")
    print("✅ Created rate_limit_overrides table with indexes")
    print("✅ Created rate_limit_whitelist table with indexes")


def downgrade() -> None:
    """Drop rate limiting tables."""

    # Drop rate_limit_whitelist table
    op.drop_index(
        "idx_rate_limit_whitelist_identifier_type", table_name="rate_limit_whitelist"
    )
    op.drop_index(op.f("ix_rate_limit_whitelist_expires_at"), table_name="rate_limit_whitelist")
    op.drop_index(op.f("ix_rate_limit_whitelist_enabled_ix"), table_name="rate_limit_whitelist")
    op.drop_index(op.f("ix_rate_limit_whitelist_limit_type"), table_name="rate_limit_whitelist")
    op.drop_index(op.f("ix_rate_limit_whitelist_identifier"), table_name="rate_limit_whitelist")
    op.drop_index(op.f("ix_rate_limit_whitelist_id"), table_name="rate_limit_whitelist")
    op.drop_table("rate_limit_whitelist")

    # Drop rate_limit_overrides table
    op.drop_index(
        "idx_rate_limit_overrides_user_expires", table_name="rate_limit_overrides"
    )
    op.drop_index(
        op.f("ix_rate_limit_overrides_expires_at"), table_name="rate_limit_overrides"
    )
    op.drop_index(op.f("ix_rate_limit_overrides_user_id"), table_name="rate_limit_overrides")
    op.drop_index(op.f("ix_rate_limit_overrides_id"), table_name="rate_limit_overrides")
    op.drop_table("rate_limit_overrides")

    # Drop rate_limit_policies table
    op.drop_index("idx_rate_limit_policies_enabled", table_name="rate_limit_policies")
    op.drop_index(
        op.f("ix_rate_limit_policies_endpoint_pattern"), table_name="rate_limit_policies"
    )
    op.drop_index(op.f("ix_rate_limit_policies_id"), table_name="rate_limit_policies")
    op.drop_table("rate_limit_policies")

    print("✅ Dropped all rate limiting tables")
