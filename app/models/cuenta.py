from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

TIPOS_VALIDOS = {
    "banco",
    "efectivo",
    "tarjeta_credito",
    "tarjeta_debito",
    "inversion",
    "cripto",
    "otro",
}


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(30), nullable=False)
    moneda = Column(String(10), nullable=False, default="PEN", server_default="PEN")
    saldo_inicial = Column(
        Numeric(18, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    saldo_actual = Column(
        Numeric(18, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    color = Column(String(7), nullable=True)
    icono = Column(String(50), nullable=True)
    institucion = Column(String(100), nullable=True)
    es_activa = Column(Boolean, nullable=False, default=True, server_default="true")
    incluir_en_total = Column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    notas = Column(Text, nullable=True)
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    usuario = relationship("Usuario", back_populates="cuentas")
    transacciones = relationship("Transaccion", foreign_keys="Transaccion.cuenta_id", back_populates="cuenta")
