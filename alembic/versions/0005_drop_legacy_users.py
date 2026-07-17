"""Drop legacy 'users' table and 'roleenum' type left over from migration 0001

Revision ID: 0005_drop_legacy_users
Revises: 0004_roles_schema_v3
Create Date: 2026-05-20 00:00:00.000000
"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_drop_legacy_users"
down_revision = "0004_roles_schema_v3"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("users")
    postgresql.ENUM(name="roleenum").drop(op.get_bind(), checkfirst=True)


def downgrade():
    import sqlalchemy as sa
    role_enum = postgresql.ENUM("ADMIN", "USER", name="roleenum")
    role_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("username", sa.String(50), nullable=True, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", postgresql.ENUM("ADMIN", "USER", name="roleenum", create_type=False), nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
