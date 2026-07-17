from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class CredencialUsuario(Base):
    __tablename__ = "credenciales_usuario"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    password_algoritmo = Column(String(50), nullable=False, default="argon2id", server_default="argon2id")
    password_actualizado_at = Column(DateTime(timezone=True), nullable=True)
    email_verificado = Column(Boolean, nullable=False, default=False, server_default="false")
    email_verificado_at = Column(DateTime(timezone=True), nullable=True)
    intentos_fallidos = Column(Integer, nullable=False, default=0, server_default="0")
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)
    ultimo_login_exitoso_at = Column(DateTime(timezone=True), nullable=True)
    ultimo_login_fallido_at = Column(DateTime(timezone=True), nullable=True)
    reset_token_hash = Column(String(64), nullable=True, index=True)
    reset_token_expira_at = Column(DateTime(timezone=True), nullable=True)
    email_verificacion_token_hash = Column(String(64), nullable=True, index=True)
    email_verificacion_expira_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    usuario = relationship("Usuario", back_populates="credencial")
