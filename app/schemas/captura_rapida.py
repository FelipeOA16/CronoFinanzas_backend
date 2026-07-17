from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.captura_rapida import (
    ESTADOS_CAPTURA_RAPIDA,
    TIPOS_CAPTURA_RAPIDA,
)


class CapturaRapidaBase(BaseModel):
    tipo: str
    monto: Decimal
    moneda: str = "PEN"
    cuenta_id: Optional[int] = None
    cuenta_destino_id: Optional[int] = None
    descripcion: Optional[str] = None
    nota_rapida: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: str) -> str:
        if value not in TIPOS_CAPTURA_RAPIDA:
            raise ValueError(f"tipo debe ser uno de {TIPOS_CAPTURA_RAPIDA}")
        return value

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return value


class CapturaRapidaCreate(CapturaRapidaBase):
    pass


class CapturaRapidaUpdate(BaseModel):
    tipo: Optional[str] = None
    monto: Optional[Decimal] = None
    moneda: Optional[str] = None
    cuenta_id: Optional[int] = None
    cuenta_destino_id: Optional[int] = None
    descripcion: Optional[str] = None
    nota_rapida: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in TIPOS_CAPTURA_RAPIDA:
            raise ValueError(f"tipo debe ser uno de {TIPOS_CAPTURA_RAPIDA}")
        return value

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is not None and value <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return value


class CompletarCapturaRapida(BaseModel):
    cuenta_id: Optional[int] = None
    cuenta_destino_id: Optional[int] = None
    categoria_id: Optional[int] = None
    descripcion: Optional[str] = None
    fecha: Optional[date] = None
    pagado_a: Optional[str] = None
    notas: Optional[str] = None


class CapturaRapidaOut(CapturaRapidaBase):
    id: int
    usuario_id: int
    estado: str
    transaccion_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CapturaRapidaResumenOut(BaseModel):
    pendientes: int
    total_pendiente: Decimal
    ultima_captura: Optional[CapturaRapidaOut] = None


class CapturaRapidaEstadoFilter(BaseModel):
    estado: Optional[str] = None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ESTADOS_CAPTURA_RAPIDA:
            raise ValueError(f"estado debe ser uno de {ESTADOS_CAPTURA_RAPIDA}")
        return value
