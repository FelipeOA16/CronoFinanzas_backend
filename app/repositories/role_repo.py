from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Rol, usuario_roles
from app.models.user import Usuario


class RoleRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Rol]:
        return self.db.execute(select(Rol).order_by(Rol.nombre)).scalars().all()

    def get_by_name(self, nombre: str) -> Optional[Rol]:
        return self.db.execute(
            select(Rol).where(Rol.nombre == nombre)
        ).scalar_one_or_none()

    def get_user_roles(self, usuario: Usuario) -> List[str]:
        return [r.nombre for r in usuario.roles]

    def assign_role(self, usuario: Usuario, nombre_rol: str) -> None:
        rol = self.get_by_name(nombre_rol)
        if not rol:
            raise ValueError(f"Rol '{nombre_rol}' no existe")
        if rol not in usuario.roles:
            usuario.roles.append(rol)
            self.db.add(usuario)

    def remove_role(self, usuario: Usuario, nombre_rol: str) -> None:
        rol = self.get_by_name(nombre_rol)
        if rol and rol in usuario.roles:
            usuario.roles.remove(rol)
            self.db.add(usuario)
