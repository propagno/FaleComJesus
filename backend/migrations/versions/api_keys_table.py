"""Create API keys table

Revision ID: 8a9fdcd4fa23
Revises: 
Create Date: 2023-06-12 10:23:45.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a9fdcd4fa23'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('key_encrypted', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index for faster lookups by user_id and provider
    op.create_index(
        'ix_api_keys_user_id_provider',
        'api_keys',
        ['user_id', 'provider'],
        unique=False
    )


def downgrade():
    # Drop index
    op.drop_index('ix_api_keys_user_id_provider')

    # Drop table
    op.drop_table('api_keys')
