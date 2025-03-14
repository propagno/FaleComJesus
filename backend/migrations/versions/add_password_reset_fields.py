"""Add password reset fields

Revision ID: a19c72d9ef2e
Revises: 8a9fdcd4fa23
Create Date: 2025-03-14 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a19c72d9ef2e'
down_revision = '8a9fdcd4fa23'
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona os campos de redefinição de senha na tabela users
    op.add_column('users', sa.Column(
        'reset_token', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column(
        'reset_token_expires', sa.DateTime(), nullable=True))


def downgrade():
    # Remove os campos de redefinição de senha da tabela users
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
