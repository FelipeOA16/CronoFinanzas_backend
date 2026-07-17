from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, field_validator

from app.models.categoria import TIPOS_CATEGORIA


class CategoriaBase(BaseModel):
    nombre: str
    tipo: str = "gasto"
    color: Optional[str] = None
    icono: Optional[str] = None
    padre_id: Optional[int] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in TIPOS_CATEGORIA:
            raise ValueError(f"tipo debe ser uno de {TIPOS_CATEGORIA}")
        return v


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    color: Optional[str] = None
    icono: Optional[str] = None

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TIPOS_CATEGORIA:
            raise ValueError(f"tipo debe ser uno de {TIPOS_CATEGORIA}")
        return v


class CategoriaOut(CategoriaBase):
    id: int
    usuario_id: Optional[int] = None   # NULL = sistema
    hijas: List["CategoriaOut"] = []
    model_config = {"from_attributes": True}


CategoriaOut.model_rebuild()
