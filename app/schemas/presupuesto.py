from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.schemas.categoria import CategoriaOut


class PresupuestoBase(BaseModel):
    categoria_id: Optional[int] = None   # None = presupuesto global
    mes: int
    anio: int
    monto_limite: Decimal
    moneda: str = "PEN"

    @field_validator("mes")
    @classmethod
    def validar_mes(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError("mes debe estar entre 1 y 12")
        return v

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, v: int) -> int:
        if v < 2020:
            raise ValueError("anio inválido")
        return v

    @field_validator("monto_limite")
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("monto_limite debe ser mayor a 0")
        return v


class PresupuestoCreate(PresupuestoBase):
    pass


class PresupuestoUpdate(BaseModel):
    monto_limite: Optional[Decimal] = None
    moneda: Optional[str] = None


class PresupuestoOut(PresupuestoBase):
    id: int
    usuario_id: int
    categoria: Optional[CategoriaOut] = None
    created_at: Optional[datetime] = None

    # Campos calculados (añadidos por el repositorio)
    monto_gastado: Decimal = Decimal("0")
    porcentaje: float = 0.0
    estado: str = "ok"   # ok | alerta | excedido

    model_config = {"from_attributes": True}
