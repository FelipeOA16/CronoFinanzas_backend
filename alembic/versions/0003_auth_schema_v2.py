"""Reemplazo esquema auth: usuarios, credenciales, proveedores, sesiones

Revision ID: 0003_auth_schema_v2
Revises: 0002_add_soft_delete
Create Date: 2026-03-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0003_auth_schema_v2"
down_revision = "0002_add_soft_delete"
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------ #
    # 1. Tabla principal de usuarios                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "usuarios",
        sa.Column("id_usuario", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("nombre", sa.String(120), nullable=True),
        sa.Column("apellido", sa.String(120), nullable=True),
        sa.Column("nombre_mostrar", sa.String(150), nullable=True),
        sa.Column("email", sa.String(225), nullable=False),
        sa.Column("email_normalizado", sa.String(225), nullable=False),
        sa.Column("telefono", sa.String(30), nullable=True),
        sa.Column("pais", sa.String(80), nullable=True),
        sa.Column(
            "zona_horaria",
            sa.String(80),
            nullable=False,
            server_default="America/Lima",
        ),
        sa.Column(
            "idioma",
            sa.String(20),
            nullable=False,
            server_default="es-PE",
        ),
        sa.Column(
            "estado_cuenta",
            sa.String(30),
            nullable=False,
            server_default="activo",
        ),
        sa.Column("foto_url", sa.Text(), nullable=True),
        sa.Column(
            "onboarding_completado",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("ultimo_acceso", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.UniqueConstraint("uuid", name="uq_usuarios_uuid"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
        sa.UniqueConstraint("email_normalizado", name="uq_usuarios_email_normalizado"),
    )
    op.create_index("ix_usuarios_uuid", "usuarios", ["uuid"])
    op.create_index("ix_usuarios_email", "usuarios", ["email"])
    op.create_index("ix_usuarios_email_normalizado", "usuarios", ["email_normalizado"])

    # ------------------------------------------------------------------ #
    # 2. Credenciales de usuario (contraseña, bloqueos, verificación)     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "credenciales_usuario",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("password_algoritmo", sa.String(50), nullable=True),
        sa.Column("password_actualizado_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "email_verificado",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("email_verificado_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("intentos_fallidos", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("bloqueado_hasta", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("ultimo_login_exitoso_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("ultimo_login_fallido_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.UniqueConstraint("id_usuario", name="uq_credenciales_id_usuario"),
    )

    # ------------------------------------------------------------------ #
    # 3. Proveedores de autenticación (OAuth / Social Login)              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "usuarios_proveedores_auth",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("proveedor", sa.String(30), nullable=False),
        sa.Column("proveedor_user_id", sa.String(225), nullable=True),
        sa.Column("email_proveedor", sa.String(255), nullable=True),
        sa.Column("email_verificado_proveedor", sa.Boolean(), nullable=True),
        sa.Column("nombre_proveedor", sa.String(255), nullable=True),
        sa.Column("foto_url_proveedor", sa.Text(), nullable=True),
        sa.Column("perfil_raw", postgresql.JSONB(), nullable=True),
        sa.Column("vinculo_activo", sa.Boolean(), nullable=True),
        sa.Column("ultimo_login_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_proveedores_auth_id_usuario",
        "usuarios_proveedores_auth",
        ["id_usuario"],
    )

    # ------------------------------------------------------------------ #
    # 4. Sesiones de usuario (tokens, dispositivos, revocación)           #
    # ------------------------------------------------------------------ #
    op.create_table(
        "sesiones_usuario",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "id_usuario",
            sa.BigInteger(),
            sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo_autenticacion", sa.String(30), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("refresh_token_hash", sa.Text(), nullable=True),
        sa.Column("dispositivo", sa.String(150), nullable=True),
        sa.Column("sistema_operativo", sa.String(100), nullable=True),
        sa.Column("navegador", sa.String(100), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("fecha_expiracion", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "revocada",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("motivo_revocacion", sa.String(100), nullable=True),
        sa.Column(
            "ultima_actividad_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("uuid", name="uq_sesiones_uuid"),
    )
    op.create_index("ix_sesiones_uuid", "sesiones_usuario", ["uuid"])
    op.create_index(
        "ix_sesiones_refresh_token_hash",
        "sesiones_usuario",
        ["refresh_token_hash"],
    )
    op.create_index("ix_sesiones_id_usuario", "sesiones_usuario", ["id_usuario"])


def downgrade():
    op.drop_table("sesiones_usuario")
    op.drop_table("usuarios_proveedores_auth")
    op.drop_table("credenciales_usuario")
    op.drop_table("usuarios")
