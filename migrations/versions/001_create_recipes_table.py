"""Create recipes table.

Revision ID: 001
Revises:
Create Date: 2025-11-14 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create recipes table with proper indexes."""

    # Create recipes table
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("ingredients", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("prep_time", sa.Integer(), nullable=True),
        sa.Column("cook_time", sa.Integer(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("nutrition", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("source_url", sa.String(length=2000), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("duplicate_of_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["duplicate_of_id"], ["recipes.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_url"),
    )

    # Create indexes
    op.create_index(
        "ix_recipes_source_url",
        "recipes",
        ["source_url"],
        unique=False
    )
    op.create_index(
        "ix_recipes_source_type",
        "recipes",
        ["source_type"],
        unique=False
    )
    op.create_index(
        "ix_recipes_created_at",
        "recipes",
        ["created_at"],
        unique=False
    )
    op.create_index(
        "ix_recipes_duplicate_of_id",
        "recipes",
        ["duplicate_of_id"],
        unique=False
    )
    op.create_index(
        "ix_recipes_not_duplicate",
        "recipes",
        ["duplicate_of_id", "created_at"],
        unique=False
    )
    op.create_index(
        "ix_recipes_title",
        "recipes",
        ["title"],
        unique=False
    )


def downgrade() -> None:
    """Drop recipes table."""

    # Drop indexes
    op.drop_index("ix_recipes_title", table_name="recipes")
    op.drop_index("ix_recipes_not_duplicate", table_name="recipes")
    op.drop_index("ix_recipes_duplicate_of_id", table_name="recipes")
    op.drop_index("ix_recipes_created_at", table_name="recipes")
    op.drop_index("ix_recipes_source_type", table_name="recipes")
    op.drop_index("ix_recipes_source_url", table_name="recipes")

    # Drop table
    op.drop_table("recipes")
