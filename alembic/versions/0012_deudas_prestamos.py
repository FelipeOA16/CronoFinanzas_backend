"""Create deudas y prestamos MVP tables

Revision ID: 0012_deudas_prestamos
Revises: 0011_account_tokens
Create Date: 2026-06-15 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_deudas_prestamos"
down_revision = "0011_account_tokens"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "deudas_prestamos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("contraparte", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("monto_original", sa.Numeric(18, 2), nullable=False),
        sa.Column("saldo_pendiente", sa.Numeric(18, 2), nullable=False),
        sa.Column("moneda", sa.String(length=5), server_default="PEN", nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_proxima", sa.Date(), nullable=True),
        sa.Column("monto_proximo", sa.Numeric(18, 2), nullable=True),
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
        sa.CheckConstraint("tipo IN ('debo', 'me_deben')", name="ck_deudas_prestamos_tipo"),
        sa.CheckConstraint("prioridad IN ('baja', 'media', 'alta', 'critica')", name="ck_deudas_prestamos_prioridad"),
        sa.CheckConstraint("estado IN ('activa', 'pagada', 'cancelada')", name="ck_deudas_prestamos_estado"),
        sa.CheckConstraint("monto_original > 0", name="ck_deudas_prestamos_monto_original_positive"),
        sa.CheckConstraint("saldo_pendiente >= 0", name="ck_deudas_prestamos_saldo_nonnegative"),
        sa.CheckConstraint("monto_proximo IS NULL OR monto_proximo > 0", name="ck_deudas_prestamos_monto_proximo_positive"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cuenta_id"], ["cuentas.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_deudas_prestamos_usuario_id", "deudas_prestamos", ["usuario_id"])
    op.create_index("ix_deudas_prestamos_cuenta_id", "deudas_prestamos", ["cuenta_id"])
    op.create_index("ix_deudas_prestamos_categoria_id", "deudas_prestamos", ["categoria_id"])
    op.create_index("ix_deudas_prestamos_tipo_estado", "deudas_prestamos", ["tipo", "estado"])
    op.create_index("ix_deudas_prestamos_fecha_proxima", "deudas_prestamos", ["fecha_proxima"])
    op.create_index("ix_deudas_prestamos_prioridad", "deudas_prestamos", ["prioridad"])

    op.create_table(
        "pagos_deuda_prestamo",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("deuda_prestamo_id", sa.BigInteger(), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("transaccion_id", sa.BigInteger(), nullable=False),
        sa.Column("cuenta_id", sa.BigInteger(), nullable=False),
        sa.Column("monto", sa.Numeric(18, 2), nullable=False),
        sa.Column("moneda", sa.String(length=5), server_default="PEN", nullable=False),
        sa.Column("fecha_pago", sa.Date(), nullable=False),
        sa.Column("notas", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("monto > 0", name="ck_pagos_deuda_prestamo_monto_positive"),
        sa.ForeignKeyConstraint(["deuda_prestamo_id"], ["deudas_prestamos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transaccion_id"], ["transacciones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cuenta_id"], ["cuentas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pagos_deuda_prestamo_deuda_prestamo_id", "pagos_deuda_prestamo", ["deuda_prestamo_id"])
    op.create_index("ix_pagos_deuda_prestamo_usuario_id", "pagos_deuda_prestamo", ["usuario_id"])
    op.create_index("ix_pagos_deuda_prestamo_transaccion_id", "pagos_deuda_prestamo", ["transaccion_id"])
    op.create_index("ix_pagos_deuda_prestamo_cuenta_id", "pagos_deuda_prestamo", ["cuenta_id"])
    op.create_index("ix_pagos_deuda_prestamo_fecha_pago", "pagos_deuda_prestamo", ["fecha_pago"])


def downgrade():
    op.drop_index("ix_pagos_deuda_prestamo_fecha_pago", table_name="pagos_deuda_prestamo")
    op.drop_index("ix_pagos_deuda_prestamo_cuenta_id", table_name="pagos_deuda_prestamo")
    op.drop_index("ix_pagos_deuda_prestamo_transaccion_id", table_name="pagos_deuda_prestamo")
    op.drop_index("ix_pagos_deuda_prestamo_usuario_id", table_name="pagos_deuda_prestamo")
    op.drop_index("ix_pagos_deuda_prestamo_deuda_prestamo_id", table_name="pagos_deuda_prestamo")
    op.drop_table("pagos_deuda_prestamo")
    op.drop_index("ix_deudas_prestamos_prioridad", table_name="deudas_prestamos")
    op.drop_index("ix_deudas_prestamos_fecha_proxima", table_name="deudas_prestamos")
    op.drop_index("ix_deudas_prestamos_tipo_estado", table_name="deudas_prestamos")
    op.drop_index("ix_deudas_prestamos_categoria_id", table_name="deudas_prestamos")
    op.drop_index("ix_deudas_prestamos_cuenta_id", table_name="deudas_prestamos")
    op.drop_index("ix_deudas_prestamos_usuario_id", table_name="deudas_prestamos")
    op.drop_table("deudas_prestamos")
