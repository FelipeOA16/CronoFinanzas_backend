from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from app.db.base import Base

TIPOS_CATEGORIA = {"ingreso", "gasto", "ambos"}

# Categorías del sistema (usuario_id = NULL)
CATEGORIAS_SISTEMA = [
    # Gastos
    {"nombre": "Alimentación",    "tipo": "gasto",   "color": "#FF5722", "icono": "restaurant"},
    {"nombre": "Transporte",      "tipo": "gasto",   "color": "#2196F3", "icono": "directions_car"},
    {"nombre": "Vivienda",        "tipo": "gasto",   "color": "#795548", "icono": "home"},
    {"nombre": "Salud",           "tipo": "gasto",   "color": "#E91E63", "icono": "local_hospital"},
    {"nombre": "Entretenimiento", "tipo": "gasto",   "color": "#9C27B0", "icono": "movie"},
    {"nombre": "Ropa",            "tipo": "gasto",   "color": "#FF9800", "icono": "checkroom"},
    {"nombre": "Educación",       "tipo": "gasto",   "color": "#3F51B5", "icono": "school"},
    {"nombre": "Otros gastos",    "tipo": "gasto",   "color": "#607D8B", "icono": "more_horiz"},
    # Ingresos
    {"nombre": "Sueldo",          "tipo": "ingreso", "color": "#4CAF50", "icono": "work"},
    {"nombre": "Freelance",       "tipo": "ingreso", "color": "#00BCD4", "icono": "laptop"},
    {"nombre": "Inversiones",     "tipo": "ingreso", "color": "#FFC107", "icono": "trending_up"},
    {"nombre": "Regalo",          "tipo": "ingreso", "color": "#E91E63", "icono": "card_giftcard"},
    {"nombre": "Otros ingresos",  "tipo": "ingreso", "color": "#607D8B", "icono": "attach_money"},
]


class Categoria(Base):
    __tablename__ = "categorias"

    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True, index=True)
    nombre     = Column(String(100), nullable=False)
    tipo       = Column(String(20), nullable=False, default="gasto")   # ingreso | gasto | ambos
    color      = Column(String(7), nullable=True)                       # #RRGGBB
    icono      = Column(String(80), nullable=True)
    padre_id   = Column(BigInteger, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    usuario       = relationship("Usuario", back_populates="categorias")
    hijas         = relationship(
        "Categoria",
        foreign_keys=[padre_id],
        backref=backref("padre_obj", remote_side="Categoria.id"),
        lazy="selectin",
    )
    transacciones = relationship("Transaccion", back_populates="categoria")
    presupuestos  = relationship("Presupuesto", back_populates="categoria")
