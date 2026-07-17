from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

PRIORIDADES_META = {"baja", "media", "alta"}
ESTADOS_META = {"activa", "completada", "pausada", "cancelada"}


class MetaFinanciera(Base):
    __tablename__ = "metas_financieras"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    monto_objetivo = Column(Numeric(18, 2), nullable=False)
    monto_actual = Column(Numeric(18, 2), nullable=False, default=0, server_default="0")
    moneda = Column(String(5), nullable=False, default="PEN", server_default="PEN")
    fecha_inicio = Column(Date, nullable=False)
    fecha_objetivo = Column(Date, nullable=True)
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

    usuario = relationship("Usuario", back_populates="metas_financieras")
    cuenta = relationship("Cuenta")
    categoria = relationship("Categoria")
    aportes = relationship("AporteMeta", back_populates="meta", order_by="AporteMeta.fecha_aporte")


class AporteMeta(Base):
    __tablename__ = "aportes_meta"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    meta_id = Column(
        BigInteger,
        ForeignKey("metas_financieras.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    transaccion_id = Column(BigInteger, ForeignKey("transacciones.id", ondelete="CASCADE"), nullable=False, index=True)
    cuenta_id = Column(BigInteger, ForeignKey("cuentas.id", ondelete="CASCADE"), nullable=False, index=True)
    monto = Column(Numeric(18, 2), nullable=False)
    moneda = Column(String(5), nullable=False, default="PEN", server_default="PEN")
    fecha_aporte = Column(Date, nullable=False)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meta = relationship("MetaFinanciera", back_populates="aportes")
    usuario = relationship("Usuario")
    transaccion = relationship("Transaccion")
    cuenta = relationship("Cuenta")
