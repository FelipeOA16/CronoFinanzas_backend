from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.transaccion import TIPOS_TRANSACCION
from app.schemas.categoria import CategoriaOut


class TransaccionBase(BaseModel):
    cuenta_id: int
    tipo: str
    monto: Decimal
    moneda: str = "PEN"
    fecha: date
    descripcion: Optional[str] = None
    notas: Optional[str] = None
    categoria_id: Optional[int] = None
    cuenta_destino_id: Optional[int] = None
    es_recurrente: bool = False

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in TIPOS_TRANSACCION:
            raise ValueError(f"tipo debe ser uno de {TIPOS_TRANSACCION}")
        return v

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return v


class TransaccionCreate(TransaccionBase):
    pass


class TransaccionUpdate(BaseModel):
    tipo: Optional[str] = None
    monto: Optional[Decimal] = None
    moneda: Optional[str] = None
    fecha: Optional[date] = None
    descripcion: Optional[str] = None
    pagado_a: Optional[str] = None
    notas: Optional[str] = None
    categoria_id: Optional[int] = None
    es_recurrente: Optional[bool] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TIPOS_TRANSACCION:
            raise ValueError(f"tipo debe ser uno de {TIPOS_TRANSACCION}")
        return v

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return v


class TransaccionOut(TransaccionBase):
    id: int
    usuario_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    categoria: Optional[CategoriaOut] = None
    model_config = {"from_attributes": True}


class TransaccionesPaginadas(BaseModel):
    items: list[TransaccionOut]
    total: int
    limit: int
    offset: int
