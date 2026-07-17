from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class UsuarioProveedorAuth(Base):
    __tablename__ = "usuarios_proveedores_auth"
    __table_args__ = (UniqueConstraint("proveedor", "proveedor_user_id", name="uq_proveedor_user"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    proveedor = Column(String(30), nullable=False)
    proveedor_user_id = Column(String(255), nullable=True)
    email_proveedor = Column(String(255), nullable=True)
    email_verificado_proveedor = Column(Boolean, nullable=True)
    nombre_proveedor = Column(String(255), nullable=True)
    foto_url_proveedor = Column(Text, nullable=True)
    perfil_raw = Column(JSONB, nullable=True)
    vinculo_activo = Column(Boolean, nullable=True)
    ultimo_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    usuario = relationship("Usuario", back_populates="proveedores_auth")
