"""Add password reset and email verification token columns to credenciales_usuario

Revision ID: 0011_account_tokens
Revises: 0010_subcategorias_sistema
Create Date: 2026-06-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0011_account_tokens"
down_revision = "0010_subcategorias_sistema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "credenciales_usuario",
        sa.Column("reset_token_hash", sa.String(64), nullable=True),
    )
    op.add_column(
        "credenciales_usuario",
        sa.Column("reset_token_expira_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "credenciales_usuario",
        sa.Column("email_verificacion_token_hash", sa.String(64), nullable=True),
    )
    op.add_column(
        "credenciales_usuario",
        sa.Column("email_verificacion_expira_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_cred_reset_token_hash",
        "credenciales_usuario",
        ["reset_token_hash"],
    )
    op.create_index(
        "ix_cred_email_verif_token_hash",
        "credenciales_usuario",
        ["email_verificacion_token_hash"],
    )


def downgrade():
    op.drop_index("ix_cred_email_verif_token_hash", table_name="credenciales_usuario")
    op.drop_index("ix_cred_reset_token_hash", table_name="credenciales_usuario")
    op.drop_column("credenciales_usuario", "email_verificacion_expira_at")
    op.drop_column("credenciales_usuario", "email_verificacion_token_hash")
    op.drop_column("credenciales_usuario", "reset_token_expira_at")
    op.drop_column("credenciales_usuario", "reset_token_hash")
