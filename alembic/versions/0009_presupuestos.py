"""Create presupuestos table

Revision ID: 0009_presupuestos
Revises: 0008_add_pagado_a
Create Date: 2026-05-29 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_presupuestos"
down_revision = "0008_add_pagado_a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "presupuestos",
        sa.Column("id",           sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id",   sa.BigInteger(), sa.ForeignKey("usuarios.id",   ondelete="CASCADE"), nullable=False),
        sa.Column("categoria_id", sa.BigInteger(), sa.ForeignKey("categorias.id", ondelete="CASCADE"), nullable=True),
        sa.Column("mes",          sa.Integer(),    nullable=False),
        sa.Column("anio",         sa.Integer(),    nullable=False),
        sa.Column("monto_limite", sa.Numeric(18, 2), nullable=False),
        sa.Column("moneda",       sa.String(5),    nullable=False, server_default="PEN"),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",   sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_presupuestos_usuario_id",   "presupuestos", ["usuario_id"])
    op.create_index("ix_presupuestos_categoria_id", "presupuestos", ["categoria_id"])
    # Unicidad: un usuario no puede tener 2 presupuestos del mismo tipo (global o por categoría) en el mismo mes/año
    op.create_unique_constraint(
        "uq_presupuesto_usuario_cat_mes_anio",
        "presupuestos",
        ["usuario_id", "categoria_id", "mes", "anio"],
    )


def downgrade() -> None:
    op.drop_table("presupuestos")
