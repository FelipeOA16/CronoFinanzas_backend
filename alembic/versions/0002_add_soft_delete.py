"""add soft-delete fields to users

Revision ID: 0002_add_soft_delete
Revises: 0001_create_users
Create Date: 2026-01-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_soft_delete'
down_revision = '0001_create_users'
branch_labels = None
depends_on = None


def upgrade():
    # add is_deleted and deleted_at columns
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('users', sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade():
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'is_deleted')
