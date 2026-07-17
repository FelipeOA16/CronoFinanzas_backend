from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id           = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id   = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    categoria_id = Column(BigInteger, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=True, index=True)
    # Si categoria_id es NULL => presupuesto global mensual
    mes          = Column(Integer, nullable=False)   # 1-12
    anio         = Column(Integer, nullable=False)
    monto_limite = Column(Numeric(18, 2), nullable=False)
    moneda       = Column(String(5), nullable=False, default="PEN")
    created_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    usuario   = relationship("Usuario", back_populates="presupuestos")
    categoria = relationship("Categoria", back_populates="presupuestos")
