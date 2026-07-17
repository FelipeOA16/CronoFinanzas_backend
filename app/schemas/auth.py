from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    nombre_mostrar: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1)


# ── Session output schema ──────────────────────────────────────────────────────

class SesionOut(BaseModel):
    uuid: UUID
    dispositivo: Optional[str] = None
    sistema_operativo: Optional[str] = None
    navegador: Optional[str] = None
    ip: Optional[str] = None
    ultima_actividad_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
