import uuid as _uuid

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class SesionUsuario(Base):
    __tablename__ = "sesiones_usuario"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(PGUUID(as_uuid=True), unique=True, nullable=False, default=_uuid.uuid4, index=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    tipo_autenticacion = Column(String(30), nullable=False)
    token_hash = Column(Text, nullable=False)
    refresh_token_hash = Column(Text, nullable=True, index=True)
    dispositivo = Column(String(150), nullable=True)
    sistema_operativo = Column(String(100), nullable=True)
    navegador = Column(String(100), nullable=True)
    ip = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    revocada = Column(Boolean, nullable=False, default=False, server_default="false")
    motivo_revocacion = Column(String(100), nullable=True)
    ultima_actividad_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="sesiones")
