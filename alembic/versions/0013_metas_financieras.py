"""Create metas financieras MVP tables

Revision ID: 0013_metas_financieras
Revises: 0012_deudas_prestamos
Create Date: 2026-06-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0013_metas_financieras"
down_revision = "0012_deudas_prestamos"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "metas_financieras",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("monto_objetivo", sa.Numeric(18, 2), nullable=False),
        sa.Column("monto_actual", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("moneda", sa.String(length=5), server_default="PEN", nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_objetivo", sa.Date(), nullable=True),
        sa.Column("prioridad", sa.String(length=20), server_default="media", nullable=False),
        sa.Column("estado", sa.String(length=20), server_default="activa", nullable=False),
        sa.Column("cuenta_id", sa.BigInteger(), nullable=True),
        sa.Column("categoria_id", sa.BigInteger(), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("icono", sa.String(length=50), nullable=True),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("prioridad IN ('baja', 'media', 'alta')", name="ck_metas_financieras_prioridad"),
        sa.CheckConstraint("estado IN ('activa', 'completada', 'pausada', 'cancelada')", name="ck_metas_financieras_estado"),
        sa.CheckConstraint("monto_objetivo > 0", name="ck_metas_financieras_monto_objetivo_positive"),
        sa.CheckConstraint("monto_actual >= 0", name="ck_metas_financieras_monto_actual_nonnegative"),
        sa.CheckConstraint("monto_actual <= monto_objetivo", name="ck_metas_financieras_monto_actual_max"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cuenta_id"], ["cuentas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metas_financieras_usuario_id", "metas_financieras", ["usuario_id"])
    op.create_index("ix_metas_financieras_cuenta_id", "metas_financieras", ["cuenta_id"])
    op.create_index("ix_metas_financieras_categoria_id", "metas_financieras", ["categoria_id"])
    op.create_index("ix_metas_financieras_estado", "metas_financieras", ["estado"])
    op.create_index("ix_metas_financieras_prioridad", "metas_financieras", ["prioridad"])
    op.create_index("ix_metas_financieras_fecha_objetivo", "metas_financieras", ["fecha_objetivo"])

    op.create_table(
        "aportes_meta",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("meta_id", sa.BigInteger(), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("transaccion_id", sa.BigInteger(), nullable=False),
        sa.Column("cuenta_id", sa.BigInteger(), nullable=False),
        sa.Column("monto", sa.Numeric(18, 2), nullable=False),
        sa.Column("moneda", sa.String(length=5), server_default="PEN", nullable=False),
        sa.Column("fecha_aporte", sa.Date(), nullable=False),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("monto > 0", name="ck_aportes_meta_monto_positive"),
        sa.ForeignKeyConstraint(["meta_id"], ["metas_financieras.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaccion_id"], ["transacciones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cuenta_id"], ["cuentas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_aportes_meta_meta_id", "aportes_meta", ["meta_id"])
    op.create_index("ix_aportes_meta_usuario_id", "aportes_meta", ["usuario_id"])
    op.create_index("ix_aportes_meta_transaccion_id", "aportes_meta", ["transaccion_id"])
    op.create_index("ix_aportes_meta_cuenta_id", "aportes_meta", ["cuenta_id"])
    op.create_index("ix_aportes_meta_fecha_aporte", "aportes_meta", ["fecha_aporte"])


def downgrade():
    op.drop_index("ix_aportes_meta_fecha_aporte", table_name="aportes_meta")
    op.drop_index("ix_aportes_meta_cuenta_id", table_name="aportes_meta")
    op.drop_index("ix_aportes_meta_transaccion_id", table_name="aportes_meta")
    op.drop_index("ix_aportes_meta_usuario_id", table_name="aportes_meta")
    op.drop_index("ix_aportes_meta_meta_id", table_name="aportes_meta")
    op.drop_table("aportes_meta")
    op.drop_index("ix_metas_financieras_fecha_objetivo", table_name="metas_financieras")
    op.drop_index("ix_metas_financieras_prioridad", table_name="metas_financieras")
    op.drop_index("ix_metas_financieras_estado", table_name="metas_financieras")
    op.drop_index("ix_metas_financieras_categoria_id", table_name="metas_financieras")
    op.drop_index("ix_metas_financieras_cuenta_id", table_name="metas_financieras")
    op.drop_index("ix_metas_financieras_usuario_id", table_name="metas_financieras")
    op.drop_table("metas_financieras")
