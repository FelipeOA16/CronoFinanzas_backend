from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

TIPOS_TRANSACCION = {"ingreso", "gasto", "transferencia"}


class Transaccion(Base):
    __tablename__ = "transacciones"

    id                 = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id         = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    cuenta_id          = Column(BigInteger, ForeignKey("cuentas.id", ondelete="CASCADE"), nullable=False, index=True)
    cuenta_destino_id  = Column(BigInteger, ForeignKey("cuentas.id", ondelete="SET NULL"), nullable=True)
    tipo               = Column(String(20), nullable=False)              # ingreso | gasto | transferencia
    monto              = Column(Numeric(18, 2), nullable=False)
    moneda             = Column(String(5), nullable=False, default="PEN")
    fecha              = Column(Date, nullable=False)
    categoria_id       = Column(BigInteger, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True, index=True)
    descripcion        = Column(String(255), nullable=True)
    pagado_a           = Column(String(200), nullable=True)   # "Pagado a" / "Recibido de"
    notas              = Column(Text, nullable=True)
    es_recurrente      = Column(Boolean, nullable=False, default=False)
    deleted_at         = Column(DateTime(timezone=True), nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at         = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    usuario        = relationship("Usuario", back_populates="transacciones")
    cuenta         = relationship("Cuenta", foreign_keys=[cuenta_id], back_populates="transacciones")
    cuenta_destino = relationship("Cuenta", foreign_keys=[cuenta_destino_id])
    categoria      = relationship("Categoria", back_populates="transacciones")
