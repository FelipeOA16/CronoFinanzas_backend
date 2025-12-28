from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from app.models.user import RoleEnum


class UserOut(BaseModel):
    id: UUID
    email: str
    username: Optional[str]
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UpdateRoleRequest(BaseModel):
    role: RoleEnum
