from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.deuda_prestamo import (
    ESTADOS_DEUDA_PRESTAMO,
    PRIORIDADES_DEUDA_PRESTAMO,
    TIPOS_DEUDA_PRESTAMO,
)


class DeudaPrestamoBase(BaseModel):
    tipo: str
    nombre: str
    contraparte: str
    descripcion: Optional[str] = None
    monto_original: Decimal
    moneda: str = "PEN"
    fecha_inicio: date
    fecha_proxima: Optional[date] = None
    monto_proximo: Optional[Decimal] = None
    prioridad: str = "media"
    cuenta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    notas: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in TIPOS_DEUDA_PRESTAMO:
            raise ValueError(f"tipo debe ser uno de {TIPOS_DEUDA_PRESTAMO}")
        return v

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v: str) -> str:
        if v not in PRIORIDADES_DEUDA_PRESTAMO:
            raise ValueError(f"prioridad debe ser una de {PRIORIDADES_DEUDA_PRESTAMO}")
        return v

    @field_validator("monto_original", "monto_proximo")
    @classmethod
    def validar_montos(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return v

    @field_validator("color")
    @classmethod
    def validar_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 7 or not v.startswith("#")):
            raise ValueError("El color debe tener formato hexadecimal #RRGGBB")
        return v


class DeudaPrestamoCreate(DeudaPrestamoBase):
    pass


class DeudaPrestamoUpdate(BaseModel):
    nombre: Optional[str] = None
    contraparte: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_proxima: Optional[date] = None
    monto_proximo: Optional[Decimal] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    cuenta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    notas: Optional[str] = None

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in PRIORIDADES_DEUDA_PRESTAMO:
            raise ValueError(f"prioridad debe ser una de {PRIORIDADES_DEUDA_PRESTAMO}")
        return v

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ESTADOS_DEUDA_PRESTAMO:
            raise ValueError(f"estado debe ser uno de {ESTADOS_DEUDA_PRESTAMO}")
        return v

    @field_validator("monto_proximo")
    @classmethod
    def validar_monto(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("monto_proximo debe ser mayor a 0")
        return v

    @field_validator("color")
    @classmethod
    def validar_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 7 or not v.startswith("#")):
            raise ValueError("El color debe tener formato hexadecimal #RRGGBB")
        return v


class DeudaPrestamoOut(DeudaPrestamoBase):
    id: int
    usuario_id: int
    saldo_pendiente: Decimal
    estado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DeudaPrestamoListOut(DeudaPrestamoOut):
    total_pagado: Decimal = Decimal("0")


class PagoDeudaPrestamoCreate(BaseModel):
    cuenta_id: int
    monto: Decimal
    fecha_pago: date
    notas: Optional[str] = None

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return v


class PagoDeudaPrestamoOut(BaseModel):
    id: int
    deuda_prestamo_id: int
    usuario_id: int
    transaccion_id: int
    cuenta_id: int
    monto: Decimal
    moneda: str
    fecha_pago: date
    notas: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DeudaPrestamoResumenItem(BaseModel):
    id: int
    tipo: str
    nombre: str
    contraparte: str
    saldo_pendiente: Decimal
    monto_proximo: Optional[Decimal] = None
    fecha_proxima: Optional[date] = None
    prioridad: str

    model_config = {"from_attributes": True}


class DeudaPrestamoResumenOut(BaseModel):
    total_debo: Decimal
    total_me_deben: Decimal
    balance_neto: Decimal
    cantidad_activas: int
    cantidad_criticas: int
    proximas: list[DeudaPrestamoResumenItem]
