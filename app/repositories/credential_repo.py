import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.credential import CredencialUsuario


class CredentialRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_usuario(self, usuario_id: int) -> Optional[CredencialUsuario]:
        return self.db.execute(
            select(CredencialUsuario).where(CredencialUsuario.usuario_id == usuario_id)
        ).scalar_one_or_none()

    def create_credential(
        self,
        usuario_id: int,
        password_hash: str,
        algoritmo: str = "argon2id",
    ) -> CredencialUsuario:
        cred = CredencialUsuario(
            usuario_id=usuario_id,
            password_hash=password_hash,
            password_algoritmo=algoritmo,
            password_actualizado_at=datetime.now(timezone.utc),
        )
        self.db.add(cred)
        self.db.flush()
        return cred

    def register_login_exitoso(self, cred: CredencialUsuario) -> None:
        cred.intentos_fallidos = 0
        cred.bloqueado_hasta = None
        cred.ultimo_login_exitoso_at = datetime.now(timezone.utc)
        self.db.add(cred)

    def register_login_fallido(
        self,
        cred: CredencialUsuario,
        max_intentos: int = 5,
        bloqueo_minutos: int = 30,
    ) -> None:
        cred.intentos_fallidos = (cred.intentos_fallidos or 0) + 1
        cred.ultimo_login_fallido_at = datetime.now(timezone.utc)
        if cred.intentos_fallidos >= max_intentos:
            cred.bloqueado_hasta = datetime.now(timezone.utc) + timedelta(minutes=bloqueo_minutos)
        self.db.add(cred)

    def update_password(
        self,
        cred: CredencialUsuario,
        new_hash: str,
        algoritmo: str = "argon2id",
    ) -> CredencialUsuario:
        cred.password_hash = new_hash
        cred.password_algoritmo = algoritmo
        cred.password_actualizado_at = datetime.now(timezone.utc)
        cred.intentos_fallidos = 0
        cred.bloqueado_hasta = None
        self.db.add(cred)
        self.db.commit()
        self.db.refresh(cred)
        return cred

    # ── Password reset tokens ────────────────────────────────────────────────

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def set_reset_token(
        self, cred: CredencialUsuario, token: str, expires_at: datetime
    ) -> None:
        cred.reset_token_hash = self._hash_token(token)
        cred.reset_token_expira_at = expires_at
        self.db.add(cred)

    def get_by_reset_token(self, token: str) -> Optional[CredencialUsuario]:
        token_hash = self._hash_token(token)
        return self.db.execute(
            select(CredencialUsuario).where(
                CredencialUsuario.reset_token_hash == token_hash,
                CredencialUsuario.reset_token_expira_at > datetime.now(timezone.utc),
            )
        ).scalar_one_or_none()

    def clear_reset_token(self, cred: CredencialUsuario) -> None:
        cred.reset_token_hash = None
        cred.reset_token_expira_at = None
        self.db.add(cred)

    # ── Email verification tokens ────────────────────────────────────────────

    def set_email_verification_token(
        self, cred: CredencialUsuario, token: str, expires_at: datetime
    ) -> None:
        cred.email_verificacion_token_hash = self._hash_token(token)
        cred.email_verificacion_expira_at = expires_at
        self.db.add(cred)

    def get_by_email_verification_token(
        self, token: str
    ) -> Optional[CredencialUsuario]:
        token_hash = self._hash_token(token)
        return self.db.execute(
            select(CredencialUsuario).where(
                CredencialUsuario.email_verificacion_token_hash == token_hash,
                CredencialUsuario.email_verificacion_expira_at
                > datetime.now(timezone.utc),
            )
        ).scalar_one_or_none()

    def mark_email_verified(self, cred: CredencialUsuario) -> None:
        cred.email_verificado = True
        cred.email_verificado_at = datetime.now(timezone.utc)
        cred.email_verificacion_token_hash = None
        cred.email_verificacion_expira_at = None
        self.db.add(cred)
