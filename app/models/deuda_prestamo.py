from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

TIPOS_DEUDA_PRESTAMO = {"debo", "me_deben"}
PRIORIDADES_DEUDA_PRESTAMO = {"baja", "media", "alta", "critica"}
ESTADOS_DEUDA_PRESTAMO = {"activa", "pagada", "cancelada"}


class DeudaPrestamo(Base):
    __tablename__ = "deudas_prestamos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)
    nombre = Column(String(150), nullable=False)
    contraparte = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    monto_original = Column(Numeric(18, 2), nullable=False)
    saldo_pendiente = Column(Numeric(18, 2), nullable=False)
    moneda = Column(String(5), nullable=False, default="PEN", server_default="PEN")
    fecha_inicio = Column(Date, nullable=False)
    fecha_proxima = Column(Date, nullable=True)
    monto_proximo = Column(Numeric(18, 2), nullable=True)
    prioridad = Column(String(20), nullable=False, default="media", server_default="media")
    estado = Column(String(20), nullable=False, default="activa", server_default="activa")
    cuenta_id = Column(BigInteger, ForeignKey("cuentas.id", ondelete="SET NULL"), nullable=True, index=True)
    categoria_id = Column(BigInteger, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True, index=True)
    color = Column(String(7), nullable=True)
    icono = Column(String(50), nullable=True)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    usuario = relationship("Usuario", back_populates="deudas_prestamos")
    cuenta = relationship("Cuenta")
    categoria = relationship("Categoria")
    pagos = relationship("PagoDeudaPrestamo", back_populates="deuda_prestamo", order_by="PagoDeudaPrestamo.fecha_pago")


class PagoDeudaPrestamo(Base):
    __tablename__ = "pagos_deuda_prestamo"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    deuda_prestamo_id = Column(
        BigInteger,
        ForeignKey("deudas_prestamos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    transaccion_id = Column(BigInteger, ForeignKey("transacciones.id", ondelete="CASCADE"), nullable=False, index=True)
    cuenta_id = Column(BigInteger, ForeignKey("cuentas.id", ondelete="CASCADE"), nullable=False, index=True)
    monto = Column(Numeric(18, 2), nullable=False)
    moneda = Column(String(5), nullable=False, default="PEN", server_default="PEN")
    fecha_pago = Column(Date, nullable=False)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    deuda_prestamo = relationship("DeudaPrestamo", back_populates="pagos")
    usuario = relationship("Usuario")
    transaccion = relationship("Transaccion")
    cuenta = relationship("Cuenta")
