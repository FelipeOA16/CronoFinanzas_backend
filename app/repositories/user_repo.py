from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.user import Usuario


class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[Usuario]:
        email_norm = email.strip().lower()
        return self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.roles))
            .where(
                Usuario.email_normalizado == email_norm,
                Usuario.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def get_by_id(self, usuario_id: int) -> Optional[Usuario]:
        usuario = self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.roles))
            .where(Usuario.id == usuario_id)
        ).scalar_one_or_none()
        if usuario is None or usuario.deleted_at is not None:
            return None
        return usuario

    def list_users(self) -> List[Usuario]:
        return self.db.execute(
            select(Usuario)
            .options(selectinload(Usuario.roles))
            .where(Usuario.deleted_at.is_(None))
            .order_by(Usuario.created_at.desc())
        ).scalars().all()

    def create_usuario(
        self,
        email: str,
        nombre: Optional[str] = None,
        apellido: Optional[str] = None,
        nombre_mostrar: Optional[str] = None,
    ) -> Usuario:
        email_norm = email.strip().lower()
        usuario = Usuario(
            email=email,
            email_normalizado=email_norm,
            nombre=nombre,
            apellido=apellido,
            nombre_mostrar=nombre_mostrar or nombre,
        )
        self.db.add(usuario)
        self.db.flush()
        return usuario

    def soft_delete(self, usuario: Usuario) -> Usuario:
        usuario.deleted_at = datetime.now(timezone.utc)
        usuario.estado_cuenta = "eliminado"
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
