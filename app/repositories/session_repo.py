import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import user_agents
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import SesionUsuario


def _hash_token(token: str) -> str:
    """SHA-256 del token para almacenamiento seguro en DB."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _parse_user_agent(ua_string: Optional[str]) -> dict:
    """Extrae dispositivo, SO y navegador del User-Agent string."""
    if not ua_string:
        return {"dispositivo": None, "sistema_operativo": None, "navegador": None}
    parsed = user_agents.parse(ua_string)
    dispositivo = parsed.device.family if parsed.device.family != "Other" else None
    so_parts = [parsed.os.family]
    if parsed.os.version_string:
        so_parts.append(parsed.os.version_string)
    sistema_operativo = " ".join(so_parts) if parsed.os.family != "Other" else None
    nav_parts = [parsed.browser.family]
    if parsed.browser.version_string:
        nav_parts.append(parsed.browser.version_string)
    navegador = " ".join(nav_parts) if parsed.browser.family != "Other" else None
    return {"dispositivo": dispositivo, "sistema_operativo": sistema_operativo, "navegador": navegador}


class SessionRepo:
    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self,
        usuario_id: int,
        tipo_autenticacion: str,
        access_token: str,
        refresh_token: str,
        expires_delta_minutes: int,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        dispositivo: Optional[str] = None,
        sistema_operativo: Optional[str] = None,
        navegador: Optional[str] = None,
    ) -> SesionUsuario:
        now = datetime.now(timezone.utc)
        ua_data = _parse_user_agent(user_agent)
        sesion = SesionUsuario(
            usuario_id=usuario_id,
            tipo_autenticacion=tipo_autenticacion,
            token_hash=_hash_token(access_token),
            refresh_token_hash=_hash_token(refresh_token),
            ip=ip,
            user_agent=user_agent,
            dispositivo=dispositivo or ua_data["dispositivo"],
            sistema_operativo=sistema_operativo or ua_data["sistema_operativo"],
            navegador=navegador or ua_data["navegador"],
            fecha_expiracion=now + timedelta(minutes=expires_delta_minutes),
            ultima_actividad_at=now,
        )
        self.db.add(sesion)
        self.db.flush()
        return sesion

    def get_by_refresh_token(self, refresh_token: str) -> Optional[SesionUsuario]:
        token_hash = _hash_token(refresh_token)
        return self.db.execute(
            select(SesionUsuario).where(
                SesionUsuario.refresh_token_hash == token_hash,
                SesionUsuario.revocada == False,  # noqa: E712
            )
        ).scalar_one_or_none()

    def rotate_session(
        self,
        sesion: SesionUsuario,
        new_access_token: str,
        new_refresh_token: str,
        expires_delta_minutes: int,
    ) -> SesionUsuario:
        now = datetime.now(timezone.utc)
        sesion.token_hash = _hash_token(new_access_token)
        sesion.refresh_token_hash = _hash_token(new_refresh_token)
        sesion.fecha_expiracion = now + timedelta(minutes=expires_delta_minutes)
        sesion.ultima_actividad_at = now
        self.db.add(sesion)
        return sesion

    def revoke_session(self, sesion: SesionUsuario, motivo: str = "logout") -> None:
        sesion.revocada = True
        sesion.motivo_revocacion = motivo
        self.db.add(sesion)

    def revoke_all_for_user(self, usuario_id: int, motivo: str = "logout_all") -> None:
        sesiones = self.db.execute(
            select(SesionUsuario).where(
                SesionUsuario.usuario_id == usuario_id,
                SesionUsuario.revocada == False,  # noqa: E712
            )
        ).scalars().all()
        for s in sesiones:
            s.revocada = True
            s.motivo_revocacion = motivo
            self.db.add(s)

    def list_active_for_user(self, usuario_id: int):
        """Return non-revoked, non-expired sessions for a user, newest first."""
        now = datetime.now(timezone.utc)
        return self.db.execute(
            select(SesionUsuario).where(
                SesionUsuario.usuario_id == usuario_id,
                SesionUsuario.revocada == False,  # noqa: E712
                SesionUsuario.fecha_expiracion > now,
            ).order_by(SesionUsuario.ultima_actividad_at.desc())
        ).scalars().all()

    def get_by_uuid(self, session_uuid: str) -> Optional[SesionUsuario]:
        return self.db.execute(
            select(SesionUsuario).where(
                SesionUsuario.uuid == session_uuid
            )
        ).scalar_one_or_none()
