"""seed_doc_types

Revision ID: abcdef123456
Revises: d33e5dd597a3
Create Date: 2026-01-28 18:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid4
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = 'd33e5dd597a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Seed Document Types
    doc_types = [
        {'code': 'GEN', 'name': 'General Document', 'description': 'General purpose document', 'category': 'General'},
        {'code': 'REP', 'name': 'Report', 'description': 'Technical or status report', 'category': 'Technical'},
        {'code': 'MEM', 'name': 'Memo', 'description': 'Internal memorandum', 'category': 'Administrative'},
        {'code': 'SPC', 'name': 'Specification', 'description': 'Technical specification', 'category': 'Technical'},
        {'code': 'INV', 'name': 'Invoice', 'description': 'Billing invoice', 'category': 'Financial'},
        {'code': 'CTR', 'name': 'Contract', 'description': 'Legal contract', 'category': 'Legal'},
        {'code': 'DWG', 'name': 'Drawing', 'description': 'Engineering drawing', 'category': 'Technical'},
    ]
    
    op.bulk_insert(
        sa.Table('document_types', sa.MetaData(),
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('code', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('category', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            schema='dm'
        ),
        [
            {
                'id': uuid4(),
                'code': dt['code'],
                'name': dt['name'],
                'description': dt['description'],
                'category': dt['category'],
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            for dt in doc_types
        ]
    )

    # Seed Stage Templates (if relevant for seeding, though user manages these)
    # Let's add a default stage template
    template_id = uuid4()
    op.bulk_insert(
        sa.Table('stage_templates', sa.MetaData(),
            sa.Column('id', sa.UUID()),
            sa.Column('name', sa.String()),
            sa.Column('description', sa.Text()),
            sa.Column('is_default', sa.Boolean()),
            sa.Column('created_at', sa.DateTime()),
            sa.Column('updated_at', sa.DateTime()),
            schema='dm'
        ),
        [{
            'id': template_id,
            'name': 'Standard Workflow',
            'description': 'Standard Draft > Review > Approved workflow',
            'is_default': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }]
    )
    
    # Seed Stage Template Items
    op.bulk_insert(
        sa.Table('stage_template_items', sa.MetaData(),
            sa.Column('id', sa.UUID()),
            sa.Column('template_id', sa.UUID()),
            sa.Column('name', sa.String()),
            sa.Column('description', sa.Text()),
            sa.Column('order_index', sa.Integer()),
            sa.Column('color', sa.String()),
            sa.Column('created_at', sa.DateTime()),
            schema='dm'
        ),
        [
            {
                'id': uuid4(),
                'template_id': template_id,
                'name': 'Draft',
                'description': 'Initial draft',
                'order_index': 0,
                'color': '#e2e8f0', # Slate 200
                'created_at': datetime.utcnow()
            },
            {
                'id': uuid4(),
                'template_id': template_id,
                'name': 'Review',
                'description': 'Under internal review',
                'order_index': 1,
                'color': '#fde047', # Yellow 300
                'created_at': datetime.utcnow()
            },
            {
                'id': uuid4(),
                'template_id': template_id,
                'name': 'Approved',
                'description': 'Approved for distribution',
                'order_index': 2,
                'color': '#86efac', # Green 300
                'created_at': datetime.utcnow()
            }
        ]
    )

def downgrade() -> None:
    op.execute("DELETE FROM dm.document_types WHERE code IN ('GEN', 'REP', 'MEM', 'SPC', 'INV', 'CTR', 'DWG')")
    op.execute("DELETE FROM dm.stage_templates WHERE name = 'Standard Workflow'")
    # Cascade delete should handle items, but for safety/correctness:
    # op.execute("DELETE FROM dm.stage_template_items WHERE template_id IN (SELECT id FROM dm.stage_templates WHERE name = 'Standard Workflow')")
