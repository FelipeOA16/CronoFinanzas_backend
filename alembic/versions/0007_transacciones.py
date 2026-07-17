"""Create categorias and transacciones tables

Revision ID: 0007_transacciones
Revises: 0006_cuentas
Create Date: 2026-05-27 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TIMESTAMP

revision = "0007_transacciones"
down_revision = "0006_cuentas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── categorias ────────────────────────────────────────────────────────────
    op.create_table(
        "categorias",
        sa.Column("id",         sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id", sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True),
        sa.Column("nombre",     sa.String(100), nullable=False),
        sa.Column("tipo",       sa.String(20),  nullable=False, server_default="gasto"),
        sa.Column("color",      sa.String(7),   nullable=True),
        sa.Column("icono",      sa.String(80),  nullable=True),
        sa.Column("padre_id",   sa.BigInteger(), sa.ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True),
        sa.Column("deleted_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_categorias_usuario_id", "categorias", ["usuario_id"])

    # ── seed categorías del sistema (usuario_id = NULL) ───────────────────────
    categorias_sistema = [
        # Gastos
        ("Alimentación",    "gasto",   "#FF5722", "restaurant"),
        ("Transporte",      "gasto",   "#2196F3", "directions_car"),
        ("Vivienda",        "gasto",   "#795548", "home"),
        ("Salud",           "gasto",   "#E91E63", "local_hospital"),
        ("Entretenimiento", "gasto",   "#9C27B0", "movie"),
        ("Ropa",            "gasto",   "#FF9800", "checkroom"),
        ("Educación",       "gasto",   "#3F51B5", "school"),
        ("Otros gastos",    "gasto",   "#607D8B", "more_horiz"),
        # Ingresos
        ("Sueldo",          "ingreso", "#4CAF50", "work"),
        ("Freelance",       "ingreso", "#00BCD4", "laptop"),
        ("Inversiones",     "ingreso", "#FFC107", "trending_up"),
        ("Regalo",          "ingreso", "#E91E63", "card_giftcard"),
        ("Otros ingresos",  "ingreso", "#607D8B", "attach_money"),
    ]
    op.bulk_insert(
        sa.table(
            "categorias",
            sa.column("nombre", sa.String),
            sa.column("tipo",   sa.String),
            sa.column("color",  sa.String),
            sa.column("icono",  sa.String),
        ),
        [{"nombre": n, "tipo": t, "color": c, "icono": i} for n, t, c, i in categorias_sistema],
    )

    # ── transacciones ─────────────────────────────────────────────────────────
    op.create_table(
        "transacciones",
        sa.Column("id",                sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("usuario_id",        sa.BigInteger(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cuenta_id",         sa.BigInteger(), sa.ForeignKey("cuentas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cuenta_destino_id", sa.BigInteger(), sa.ForeignKey("cuentas.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tipo",              sa.String(20), nullable=False),
        sa.Column("monto",             sa.Numeric(18, 2), nullable=False),
        sa.Column("moneda",            sa.String(5), nullable=False, server_default="PEN"),
        sa.Column("fecha",             sa.Date(), nullable=False),
        sa.Column("categoria_id",      sa.BigInteger(), sa.ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True),
        sa.Column("descripcion",       sa.String(255), nullable=True),
        sa.Column("notas",             sa.Text(), nullable=True),
        sa.Column("es_recurrente",     sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at",        TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at",        TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at",        TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_transacciones_usuario_id",   "transacciones", ["usuario_id"])
    op.create_index("ix_transacciones_cuenta_id",    "transacciones", ["cuenta_id"])
    op.create_index("ix_transacciones_categoria_id", "transacciones", ["categoria_id"])
    op.create_index("ix_transacciones_fecha",        "transacciones", ["fecha"])


def downgrade() -> None:
    op.drop_table("transacciones")
    op.drop_index("ix_categorias_usuario_id", table_name="categorias")
    op.drop_table("categorias")
