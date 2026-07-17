from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

TIPOS_CAPTURA_RAPIDA = {"gasto", "ingreso", "transferencia"}
ESTADOS_CAPTURA_RAPIDA = {"pendiente", "completada", "descartada"}


class CapturaRapida(Base):
    __tablename__ = "capturas_rapidas"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo = Column(String(20), nullable=False, index=True)
    monto = Column(Numeric(18, 2), nullable=False)
    moneda = Column(String(5), nullable=False, default="PEN", server_default="PEN")
    cuenta_id = Column(
        BigInteger,
        ForeignKey("cuentas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    cuenta_destino_id = Column(
        BigInteger,
        ForeignKey("cuentas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    descripcion = Column(String(255), nullable=True)
    nota_rapida = Column(Text, nullable=True)
    estado = Column(
        String(20),
        nullable=False,
        default="pendiente",
        server_default="pendiente",
        index=True,
    )
    transaccion_id = Column(
        BigInteger,
        ForeignKey("transacciones.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship("Usuario", back_populates="capturas_rapidas")
    cuenta = relationship("Cuenta", foreign_keys=[cuenta_id])
    cuenta_destino = relationship("Cuenta", foreign_keys=[cuenta_destino_id])
    transaccion = relationship("Transaccion")
