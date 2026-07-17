from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


# Association table (no class needed — pure many-to-many)
usuario_roles = Table(
    "usuario_roles",
    Base.metadata,
    Column("usuario_id", BigInteger, ForeignKey("usuarios.id"), primary_key=True),
    Column("rol_id", BigInteger, ForeignKey("roles.id"), primary_key=True),
    Column("asignado_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)


class Rol(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuarios = relationship("Usuario", secondary="usuario_roles", back_populates="roles")
