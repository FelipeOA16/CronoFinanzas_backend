from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.meta_financiera import ESTADOS_META, PRIORIDADES_META


class MetaFinancieraBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    monto_objetivo: Decimal
    monto_actual: Optional[Decimal] = None
    moneda: str = "PEN"
    fecha_inicio: date
    fecha_objetivo: Optional[date] = None
    prioridad: str = "media"
    cuenta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    notas: Optional[str] = None

    @field_validator("monto_objetivo")
    @classmethod
    def validar_objetivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("monto_objetivo debe ser mayor a 0")
        return v

    @field_validator("monto_actual")
    @classmethod
    def validar_actual(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("monto_actual no puede ser negativo")
        return v

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v: str) -> str:
        if v not in PRIORIDADES_META:
            raise ValueError(f"prioridad debe ser una de {PRIORIDADES_META}")
        return v

    @field_validator("color")
    @classmethod
    def validar_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 7 or not v.startswith("#")):
            raise ValueError("El color debe tener formato hexadecimal #RRGGBB")
        return v


class MetaFinancieraCreate(MetaFinancieraBase):
    pass


class MetaFinancieraUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    monto_objetivo: Optional[Decimal] = None
    fecha_objetivo: Optional[date] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    cuenta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    notas: Optional[str] = None

    @field_validator("monto_objetivo")
    @classmethod
    def validar_objetivo(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("monto_objetivo debe ser mayor a 0")
        return v

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in PRIORIDADES_META:
            raise ValueError(f"prioridad debe ser una de {PRIORIDADES_META}")
        return v

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ESTADOS_META:
            raise ValueError(f"estado debe ser uno de {ESTADOS_META}")
        return v

    @field_validator("color")
    @classmethod
    def validar_color(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 7 or not v.startswith("#")):
            raise ValueError("El color debe tener formato hexadecimal #RRGGBB")
        return v


class MetaFinancieraOut(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    descripcion: Optional[str] = None
    monto_objetivo: Decimal
    monto_actual: Decimal
    moneda: str
    fecha_inicio: date
    fecha_objetivo: Optional[date] = None
    prioridad: str
    estado: str
    cuenta_id: Optional[int] = None
    categoria_id: Optional[int] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    notas: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MetaFinancieraListOut(MetaFinancieraOut):
    porcentaje: Decimal = Decimal("0")
    faltante: Decimal = Decimal("0")


class AporteMetaCreate(BaseModel):
    cuenta_id: int
    monto: Decimal
    fecha_aporte: date
    notas: Optional[str] = None

    @field_validator("monto")
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("monto debe ser mayor a 0")
        return v


class AporteMetaOut(BaseModel):
    id: int
    meta_id: int
    usuario_id: int
    transaccion_id: int
    cuenta_id: int
    monto: Decimal
    moneda: str
    fecha_aporte: date
    notas: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MetaFinancieraResumenItem(BaseModel):
    id: int
    nombre: str
    monto_objetivo: Decimal
    monto_actual: Decimal
    porcentaje: Decimal
    prioridad: str
    fecha_objetivo: Optional[date] = None


class MetaFinancieraResumenOut(BaseModel):
    total_objetivo: Decimal
    total_actual: Decimal
    porcentaje_global: Decimal
    cantidad_activas: int
    cantidad_completadas: int
    top_metas: list[MetaFinancieraResumenItem]
