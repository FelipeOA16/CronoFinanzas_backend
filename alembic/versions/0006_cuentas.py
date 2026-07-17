"""Create cuentas table

Revision ID: 0006_cuentas
Revises: 0005_drop_legacy_users
Create Date: 2026-05-20 00:00:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = "0006_cuentas"
down_revision = "0005_drop_legacy_users"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cuentas",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("moneda", sa.String(10), nullable=False, server_default="PEN"),
        sa.Column("saldo_inicial", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("saldo_actual", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("icono", sa.String(50), nullable=True),
        sa.Column("institucion", sa.String(100), nullable=True),
        sa.Column("es_activa", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("incluir_en_total", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_cuentas_usuario_id", "cuentas", ["usuario_id"])


def downgrade():
    op.drop_index("ix_cuentas_usuario_id", table_name="cuentas")
    op.drop_table("cuentas")
