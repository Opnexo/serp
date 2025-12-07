"""Initial common tables

Revision ID: 001
Revises:
Create Date: 2024-12-07 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Schema name for this module
SCHEMA = "common"


def upgrade() -> None:
    # Create schema
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    # Create addresses table
    op.create_table(
        "addresses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("street", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("address_type", sa.String(20), nullable=False, server_default="OTHER"),
        sa.Column("owner_type", sa.String(50), nullable=True),
        sa.Column("owner_id", sa.String(36), nullable=True),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema=SCHEMA,
    )

    # Create indexes
    op.create_index(
        "ix_addresses_owner",
        "addresses",
        ["owner_type", "owner_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_addresses_country",
        "addresses",
        ["country"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_addresses_city",
        "addresses",
        ["city"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_addresses_active",
        "addresses",
        ["is_active"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_addresses_active", table_name="addresses", schema=SCHEMA)
    op.drop_index("ix_addresses_city", table_name="addresses", schema=SCHEMA)
    op.drop_index("ix_addresses_country", table_name="addresses", schema=SCHEMA)
    op.drop_index("ix_addresses_owner", table_name="addresses", schema=SCHEMA)

    # Drop table
    op.drop_table("addresses", schema=SCHEMA)

    # Drop schema (only if empty)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
