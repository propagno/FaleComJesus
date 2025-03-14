"""Add use_count column to api_keys table

Revision ID: add_use_count_to_api_keys
Revises: 
Create Date: 2025-03-14 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_use_count_to_api_keys'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add use_count column to api_keys table
    op.add_column('api_keys', sa.Column(
        'use_count', sa.Integer(), nullable=True, server_default='0'))


def downgrade():
    # Remove use_count column from api_keys table
    op.drop_column('api_keys', 'use_count')
