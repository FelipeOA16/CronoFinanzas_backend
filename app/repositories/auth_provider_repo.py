from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth_provider import UsuarioProveedorAuth


class AuthProviderRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, usuario_id: int) -> List[UsuarioProveedorAuth]:
        return self.db.execute(
            select(UsuarioProveedorAuth)
            .where(
                UsuarioProveedorAuth.usuario_id == usuario_id,
                UsuarioProveedorAuth.vinculo_activo == True,  # noqa: E712
            )
            .order_by(UsuarioProveedorAuth.created_at)
        ).scalars().all()

    def get_by_provider(
        self, usuario_id: int, proveedor: str
    ) -> Optional[UsuarioProveedorAuth]:
        return self.db.execute(
            select(UsuarioProveedorAuth).where(
                UsuarioProveedorAuth.usuario_id == usuario_id,
                UsuarioProveedorAuth.proveedor == proveedor,
            )
        ).scalar_one_or_none()

    def link_provider(
        self,
        usuario_id: int,
        proveedor: str,
        proveedor_user_id: str,
        email_proveedor: Optional[str] = None,
        email_verificado_proveedor: Optional[bool] = None,
        nombre_proveedor: Optional[str] = None,
        foto_url_proveedor: Optional[str] = None,
        perfil_raw: Optional[dict] = None,
    ) -> UsuarioProveedorAuth:
        existing = self.get_by_provider(usuario_id, proveedor)
        if existing:
            # Reactivate if previously unlinked
            existing.vinculo_activo = True
            existing.proveedor_user_id = proveedor_user_id
            existing.email_proveedor = email_proveedor
            existing.email_verificado_proveedor = email_verificado_proveedor
            existing.nombre_proveedor = nombre_proveedor
            existing.foto_url_proveedor = foto_url_proveedor
            existing.perfil_raw = perfil_raw
            self.db.add(existing)
            return existing

        link = UsuarioProveedorAuth(
            usuario_id=usuario_id,
            proveedor=proveedor,
            proveedor_user_id=proveedor_user_id,
            email_proveedor=email_proveedor,
            email_verificado_proveedor=email_verificado_proveedor,
            nombre_proveedor=nombre_proveedor,
            foto_url_proveedor=foto_url_proveedor,
            perfil_raw=perfil_raw,
            vinculo_activo=True,
        )
        self.db.add(link)
        self.db.flush()
        return link

    def unlink_provider(self, usuario_id: int, proveedor: str) -> bool:
        """Soft-unlink: sets vinculo_activo=False. Returns True if found."""
        link = self.get_by_provider(usuario_id, proveedor)
        if not link:
            return False
        link.vinculo_activo = False
        self.db.add(link)
        return True
