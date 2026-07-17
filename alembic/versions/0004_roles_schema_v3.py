"""Schema v3: roles, rename PKs/FKs, fix email length, argon2id, unique constraint on proveedores

Revision ID: 0004_roles_schema_v3
Revises: 0003_auth_schema_v2
Create Date: 2026-04-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_roles_schema_v3"
down_revision = "0003_auth_schema_v2"
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------ #
    # 1. usuarios: rename PK column id_usuario → id                       #
    # ------------------------------------------------------------------ #
    op.alter_column("usuarios", "id_usuario", new_column_name="id")

    # Fix email column lengths (225 → 255)
    op.alter_column("usuarios", "email",
        existing_type=sa.String(225), type_=sa.String(255), existing_nullable=False)
    op.alter_column("usuarios", "email_normalizado",
        existing_type=sa.String(225), type_=sa.String(255), existing_nullable=False)

    # Rename ultimo_acceso → ultimo_acceso_at
    op.alter_column("usuarios", "ultimo_acceso", new_column_name="ultimo_acceso_at")

    # ------------------------------------------------------------------ #
    # 2. credenciales_usuario: rename FK column id_usuario → usuario_id   #
    # ------------------------------------------------------------------ #
    op.alter_column("credenciales_usuario", "id_usuario", new_column_name="usuario_id")

    # Fix default algorithm annotation (data stays valid — bcrypt hashes work with argon2 verify fallback)
    op.alter_column("credenciales_usuario", "password_algoritmo",
        existing_type=sa.String(50), nullable=False,
        server_default="argon2id")

    # Make intentos_fallidos NOT NULL
    op.execute("UPDATE credenciales_usuario SET intentos_fallidos = 0 WHERE intentos_fallidos IS NULL")
    op.alter_column("credenciales_usuario", "intentos_fallidos",
        existing_type=sa.Integer(), nullable=False, server_default="0")

    # ------------------------------------------------------------------ #
    # 3. sesiones_usuario: rename FK column id_usuario → usuario_id       #
    # ------------------------------------------------------------------ #
    op.alter_column("sesiones_usuario", "id_usuario", new_column_name="usuario_id")

    # ------------------------------------------------------------------ #
    # 4. usuarios_proveedores_auth: rename FK + fix length + add UNIQUE   #
    # ------------------------------------------------------------------ #
    op.alter_column("usuarios_proveedores_auth", "id_usuario", new_column_name="usuario_id")
    op.alter_column("usuarios_proveedores_auth", "proveedor_user_id",
        existing_type=sa.String(225), type_=sa.String(255))
    op.create_unique_constraint(
        "uq_proveedor_user",
        "usuarios_proveedores_auth",
        ["proveedor", "proveedor_user_id"],
    )

    # ------------------------------------------------------------------ #
    # 5. Nueva tabla roles                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(50), unique=True, nullable=False),
        sa.Column("descripcion", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )

    # ------------------------------------------------------------------ #
    # 6. Nueva tabla usuario_roles (many-to-many)                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "usuario_roles",
        sa.Column("usuario_id", sa.BigInteger(),
                  sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("rol_id", sa.BigInteger(),
                  sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("asignado_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )

    # ------------------------------------------------------------------ #
    # 7. Seed: insertar los 3 roles base                                   #
    # ------------------------------------------------------------------ #
    op.execute("""
        INSERT INTO roles (nombre, descripcion) VALUES
        ('admin',     'Administrador con acceso total'),
        ('estandar',  'Usuario estándar de la aplicación'),
        ('premium',   'Usuario premium con funciones extendidas')
        ON CONFLICT (nombre) DO NOTHING;
    """)


def downgrade():
    op.drop_table("usuario_roles")
    op.drop_table("roles")
    op.drop_constraint("uq_proveedor_user", "usuarios_proveedores_auth", type_="unique")
    op.alter_column("usuarios_proveedores_auth", "usuario_id", new_column_name="id_usuario")
    op.alter_column("sesiones_usuario", "usuario_id", new_column_name="id_usuario")
    op.alter_column("credenciales_usuario", "usuario_id", new_column_name="id_usuario")
    op.alter_column("usuarios", "ultimo_acceso_at", new_column_name="ultimo_acceso")
    op.alter_column("usuarios", "id", new_column_name="id_usuario")
