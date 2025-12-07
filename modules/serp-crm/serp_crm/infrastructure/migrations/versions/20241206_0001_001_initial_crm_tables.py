"""Initial CRM tables in 'crm' schema

Revision ID: 001
Revises:
Create Date: 2024-12-06

"""

import os
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Get schema from environment or use default
SCHEMA = os.getenv("SERP_CRM_DATABASE_SCHEMA", "crm")


def upgrade() -> None:
    # Create the schema if it doesn't exist
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    # Create enums in the schema
    partner_type_enum = postgresql.ENUM(
        "INDIVIDUAL", "COMPANY", name="partnertype", schema=SCHEMA, create_type=False
    )
    partner_type_enum.create(op.get_bind(), checkfirst=True)

    lead_status_enum = postgresql.ENUM(
        "NEW",
        "CONTACTED",
        "QUALIFIED",
        "LOST",
        name="leadstatus",
        schema=SCHEMA,
        create_type=False,
    )
    lead_status_enum.create(op.get_bind(), checkfirst=True)

    opportunity_stage_enum = postgresql.ENUM(
        "PROSPECTING",
        "QUALIFICATION",
        "PROPOSAL",
        "NEGOTIATION",
        "WON",
        "LOST",
        name="opportunitystage",
        schema=SCHEMA,
        create_type=False,
    )
    opportunity_stage_enum.create(op.get_bind(), checkfirst=True)

    activity_type_enum = postgresql.ENUM(
        "CALL",
        "EMAIL",
        "MEETING",
        "NOTE",
        "TASK",
        name="activitytype",
        schema=SCHEMA,
        create_type=False,
    )
    activity_type_enum.create(op.get_bind(), checkfirst=True)

    # Create partners table
    op.create_table(
        "partners",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "partner_type",
            postgresql.ENUM(
                "INDIVIDUAL",
                "COMPANY",
                name="partnertype",
                schema=SCHEMA,
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("is_customer", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_supplier", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("billing_address", postgresql.JSONB(), nullable=True),
        sa.Column("shipping_address", postgresql.JSONB(), nullable=True),
        sa.Column("tax_id_value", sa.String(50), nullable=True),
        sa.Column("tax_id_country", sa.String(2), nullable=True),
        sa.Column("company_registry", sa.String(100), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("annual_revenue_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("annual_revenue_currency", sa.String(3), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True, default=[]),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA,
    )
    op.create_index(f"ix_{SCHEMA}_partners_name", "partners", ["name"], schema=SCHEMA)
    op.create_index(f"ix_{SCHEMA}_partners_email", "partners", ["email"], schema=SCHEMA)
    op.create_index(
        f"ix_{SCHEMA}_partners_is_customer", "partners", ["is_customer"], schema=SCHEMA
    )
    op.create_index(
        f"ix_{SCHEMA}_partners_is_supplier", "partners", ["is_supplier"], schema=SCHEMA
    )
    op.create_index(
        f"ix_{SCHEMA}_partners_is_active", "partners", ["is_active"], schema=SCHEMA
    )

    # Create contacts table
    op.create_table(
        "contacts",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("partner_id", sa.String(36), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, default=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("mobile", sa.String(50), nullable=True),
        sa.Column("job_title", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("address", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True, default=[]),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["partner_id"], [f"{SCHEMA}.partners.id"], ondelete="CASCADE"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_contacts_partner_id", "contacts", ["partner_id"], schema=SCHEMA
    )
    op.create_index(f"ix_{SCHEMA}_contacts_email", "contacts", ["email"], schema=SCHEMA)
    op.create_index(
        f"ix_{SCHEMA}_contacts_is_active", "contacts", ["is_active"], schema=SCHEMA
    )

    # Create leads table
    op.create_table(
        "leads",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "NEW",
                "CONTACTED",
                "QUALIFIED",
                "LOST",
                name="leadstatus",
                schema=SCHEMA,
                create_type=False,
            ),
            nullable=False,
            default="NEW",
        ),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, default=0),
        sa.Column("interest_level", sa.String(20), nullable=True),
        sa.Column("converted_to_partner_id", sa.String(36), nullable=True),
        sa.Column("converted_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True, default=[]),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["converted_to_partner_id"], [f"{SCHEMA}.partners.id"], ondelete="SET NULL"
        ),
        schema=SCHEMA,
    )
    op.create_index(f"ix_{SCHEMA}_leads_name", "leads", ["name"], schema=SCHEMA)
    op.create_index(f"ix_{SCHEMA}_leads_company", "leads", ["company"], schema=SCHEMA)
    op.create_index(f"ix_{SCHEMA}_leads_email", "leads", ["email"], schema=SCHEMA)
    op.create_index(f"ix_{SCHEMA}_leads_status", "leads", ["status"], schema=SCHEMA)

    # Create opportunities table
    op.create_table(
        "opportunities",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("partner_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "stage",
            postgresql.ENUM(
                "PROSPECTING",
                "QUALIFICATION",
                "PROPOSAL",
                "NEGOTIATION",
                "WON",
                "LOST",
                name="opportunitystage",
                schema=SCHEMA,
                create_type=False,
            ),
            nullable=False,
            default="PROSPECTING",
        ),
        sa.Column("amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("probability", sa.Integer(), nullable=False, default=0),
        sa.Column("expected_close_date", sa.Date(), nullable=True),
        sa.Column("actual_close_date", sa.Date(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("campaign", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True, default=[]),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["partner_id"], [f"{SCHEMA}.partners.id"], ondelete="CASCADE"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_opportunities_partner_id",
        "opportunities",
        ["partner_id"],
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_opportunities_name", "opportunities", ["name"], schema=SCHEMA
    )
    op.create_index(
        f"ix_{SCHEMA}_opportunities_stage", "opportunities", ["stage"], schema=SCHEMA
    )

    # Create activities table
    op.create_table(
        "activities",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("partner_id", sa.String(36), nullable=False),
        sa.Column("contact_id", sa.String(36), nullable=True),
        sa.Column("opportunity_id", sa.String(36), nullable=True),
        sa.Column(
            "activity_type",
            postgresql.ENUM(
                "CALL",
                "EMAIL",
                "MEETING",
                "NOTE",
                "TASK",
                name="activitytype",
                schema=SCHEMA,
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, default=False),
        sa.Column("performed_by", sa.String(36), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["partner_id"], [f"{SCHEMA}.partners.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"], [f"{SCHEMA}.contacts.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["opportunity_id"], [f"{SCHEMA}.opportunities.id"], ondelete="SET NULL"
        ),
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_activities_partner_id",
        "activities",
        ["partner_id"],
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_activities_contact_id",
        "activities",
        ["contact_id"],
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_activities_opportunity_id",
        "activities",
        ["opportunity_id"],
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_activities_activity_type",
        "activities",
        ["activity_type"],
        schema=SCHEMA,
    )
    op.create_index(
        f"ix_{SCHEMA}_activities_is_completed",
        "activities",
        ["is_completed"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("activities", schema=SCHEMA)
    op.drop_table("opportunities", schema=SCHEMA)
    op.drop_table("leads", schema=SCHEMA)
    op.drop_table("contacts", schema=SCHEMA)
    op.drop_table("partners", schema=SCHEMA)

    # Drop enums
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.activitytype")
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.opportunitystage")
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.leadstatus")
    op.execute(f"DROP TYPE IF EXISTS {SCHEMA}.partnertype")

    # Optionally drop the schema (commented out for safety)
    # op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
