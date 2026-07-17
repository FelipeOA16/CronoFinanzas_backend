from datetime import datetime
from uuid import UUID
from typing import Any, List, Optional

from pydantic import BaseModel, field_validator


class UserOut(BaseModel):
    id: int
    uuid: UUID
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    nombre_mostrar: Optional[str] = None
    email: str
    telefono: Optional[str] = None
    pais: Optional[str] = None
    zona_horaria: str
    idioma: str
    estado_cuenta: str
    foto_url: Optional[str] = None
    onboarding_completado: bool
    ultimo_acceso_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    roles: List[str] = []
    email_verificado: bool = False

    model_config = {"from_attributes": True}

    @field_validator("roles", mode="before")
    @classmethod
    def _coerce_roles(cls, v: Any) -> List[str]:
        if not v:
            return []
        return [r.nombre if hasattr(r, "nombre") else str(r) for r in v]

    @classmethod
    def from_orm_with_roles(cls, usuario) -> "UserOut":
        return cls.model_validate(usuario)


class UpdatePerfilRequest(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    nombre_mostrar: Optional[str] = None
    telefono: Optional[str] = None
    pais: Optional[str] = None
    zona_horaria: Optional[str] = None
    idioma: Optional[str] = None
    foto_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ProveedorAuthOut(BaseModel):
    proveedor: str
    proveedor_user_id: str
    email_proveedor: Optional[str] = None
    nombre_proveedor: Optional[str] = None
    foto_url_proveedor: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
