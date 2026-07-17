"""add pagado_a to transacciones

Revision ID: 0008_add_pagado_a
Revises: 0007_transacciones
Create Date: 2026-05-27
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_add_pagado_a"
down_revision = "0007_transacciones"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transacciones",
        sa.Column("pagado_a", sa.String(200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("transacciones", "pagado_a")
