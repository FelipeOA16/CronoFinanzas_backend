from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.cuenta import TIPOS_VALIDOS


class CuentaBase(BaseModel):
    nombre: str
    tipo: str
    moneda: str = "PEN"
    saldo_inicial: Decimal = Decimal("0")
    color: Optional[str] = None
    icono: Optional[str] = None
    institucion: Optional[str] = None
    es_activa: bool = True
    incluir_en_total: bool = True
    notas: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def _tipo_valido(cls, v: str) -> str:
        if v not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo inválido '{v}'. Valores permitidos: {sorted(TIPOS_VALIDOS)}"
            )
        return v

    @field_validator("color")
    @classmethod
    def _color_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 7 or not v.startswith("#")):
            raise ValueError("El color debe tener formato hexadecimal #RRGGBB")
        return v


class CuentaCreate(CuentaBase):
    pass


class CuentaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    moneda: Optional[str] = None
    color: Optional[str] = None
    icono: Optional[str] = None
    institucion: Optional[str] = None
    es_activa: Optional[bool] = None
    incluir_en_total: Optional[bool] = None
    notas: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def _tipo_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo inválido '{v}'. Valores permitidos: {sorted(TIPOS_VALIDOS)}"
            )
        return v

    @field_validator("color")
    @classmethod
    def _color_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) != 7 or not v.startswith("#")):
            raise ValueError("El color debe tener formato hexadecimal #RRGGBB")
        return v


class CuentaOut(CuentaBase):
    id: int
    usuario_id: int
    saldo_actual: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CuentasResumen(BaseModel):
    total_patrimonio: Decimal
    total_cuentas: int
    total_cuentas_activas: int
