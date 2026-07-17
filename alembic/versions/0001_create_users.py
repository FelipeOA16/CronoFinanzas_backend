from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    role_enum = psql.ENUM("ADMIN", "USER", name="roleenum")
    # create enum only if it does not already exist
    role_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", psql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("username", sa.String(length=50), nullable=True, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        # use the existing enum type without attempting to create it again
        sa.Column("role", psql.ENUM("ADMIN", "USER", name="roleenum", create_type=False), nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade():
    op.drop_table("users")
    role_enum = psql.ENUM("ADMIN", "USER", name="roleenum")
    # drop enum only if it exists
    role_enum.drop(op.get_bind(), checkfirst=True)
