"""Create capturas rapidas table

Revision ID: 0014_capturas_rapidas
Revises: 0013_metas_financieras
Create Date: 2026-07-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0014_capturas_rapidas"
down_revision = "0013_metas_financieras"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "capturas_rapidas",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("monto", sa.Numeric(18, 2), nullable=False),
        sa.Column(
            "moneda",
            sa.String(length=5),
            server_default="PEN",
            nullable=False,
        ),
        sa.Column("cuenta_id", sa.BigInteger(), nullable=True),
        sa.Column("cuenta_destino_id", sa.BigInteger(), nullable=True),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("nota_rapida", sa.Text(), nullable=True),
        sa.Column(
            "estado",
            sa.String(length=20),
            server_default="pendiente",
            nullable=False,
        ),
        sa.Column("transaccion_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "tipo IN ('gasto', 'ingreso', 'transferencia')",
            name="ck_capturas_rapidas_tipo",
        ),
        sa.CheckConstraint(
            "estado IN ('pendiente', 'completada', 'descartada')",
            name="ck_capturas_rapidas_estado",
        ),
        sa.CheckConstraint(
            "monto > 0",
            name="ck_capturas_rapidas_monto_positive",
        ),
        sa.CheckConstraint(
            "cuenta_id IS NULL OR cuenta_destino_id IS NULL OR "
            "cuenta_id <> cuenta_destino_id",
            name="ck_capturas_rapidas_cuentas_distintas",
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["cuenta_id"],
            ["cuentas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["cuenta_destino_id"],
            ["cuentas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["transaccion_id"],
            ["transacciones.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "transaccion_id",
            name="uq_capturas_rapidas_transaccion_id",
        ),
    )
    op.create_index(
        "ix_capturas_rapidas_usuario_id",
        "capturas_rapidas",
        ["usuario_id"],
    )
    op.create_index(
        "ix_capturas_rapidas_tipo",
        "capturas_rapidas",
        ["tipo"],
    )
    op.create_index(
        "ix_capturas_rapidas_estado",
        "capturas_rapidas",
        ["estado"],
    )
    op.create_index(
        "ix_capturas_rapidas_cuenta_id",
        "capturas_rapidas",
        ["cuenta_id"],
    )
    op.create_index(
        "ix_capturas_rapidas_cuenta_destino_id",
        "capturas_rapidas",
        ["cuenta_destino_id"],
    )
    op.create_index(
        "ix_capturas_rapidas_pendientes_usuario",
        "capturas_rapidas",
        ["usuario_id", "estado", "created_at"],
    )


def downgrade():
    op.drop_index(
        "ix_capturas_rapidas_pendientes_usuario",
        table_name="capturas_rapidas",
    )
    op.drop_index(
        "ix_capturas_rapidas_cuenta_destino_id",
        table_name="capturas_rapidas",
    )
    op.drop_index(
        "ix_capturas_rapidas_cuenta_id",
        table_name="capturas_rapidas",
    )
    op.drop_index(
        "ix_capturas_rapidas_estado",
        table_name="capturas_rapidas",
    )
    op.drop_index(
        "ix_capturas_rapidas_tipo",
        table_name="capturas_rapidas",
    )
    op.drop_index(
        "ix_capturas_rapidas_usuario_id",
        table_name="capturas_rapidas",
    )
    op.drop_table("capturas_rapidas")
