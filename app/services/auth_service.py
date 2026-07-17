from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

from fastapi import HTTPException, Request

from app.repositories.user_repo import UserRepo
from app.repositories.credential_repo import CredentialRepo
from app.repositories.session_repo import SessionRepo
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.token import TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config import Settings

if TYPE_CHECKING:
    from app.models.user import Usuario

settings = Settings()


class AuthService:
    def __init__(self, user_repo: UserRepo, cred_repo: CredentialRepo, session_repo: SessionRepo):
        self.user_repo = user_repo
        self.cred_repo = cred_repo
        self.session_repo = session_repo

    def register(self, data: RegisterRequest) -> "Usuario":
        if self.user_repo.get_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email ya registrado")
        password_hash = hash_password(data.password)

        usuario = self.user_repo.create_usuario(
            email=data.email,
            nombre=data.nombre,
            apellido=data.apellido,
            nombre_mostrar=data.nombre_mostrar,
        )
        self.cred_repo.create_credential(
            usuario_id=usuario.id,
            password_hash=password_hash,
        )
        self.user_repo.db.commit()
        self.user_repo.db.refresh(usuario)
        return usuario

    def login(self, data: LoginRequest, request: Optional[Request] = None) -> TokenResponse:
        usuario = self.user_repo.get_by_email(data.email)
        if not usuario:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if usuario.estado_cuenta != "activo":
            raise HTTPException(status_code=403, detail="Cuenta inactiva o suspendida")

        cred = self.cred_repo.get_by_usuario(usuario.id)
        if not cred:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        if cred.bloqueado_hasta and cred.bloqueado_hasta > datetime.now(timezone.utc):
            raise HTTPException(status_code=429, detail="Cuenta bloqueada temporalmente por múltiples intentos fallidos")

        if not verify_password(data.password, cred.password_hash):
            self.cred_repo.register_login_fallido(cred)
            self.user_repo.db.commit()
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        self.cred_repo.register_login_exitoso(cred)

        roles = [r.nombre for r in usuario.roles]
        access_token = create_access_token(subject=str(usuario.id), roles=roles)
        refresh_token = create_refresh_token(subject=str(usuario.id))

        ip = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None

        self.session_repo.create_session(
            usuario_id=usuario.id,
            tipo_autenticacion="password",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_delta_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            ip=ip,
            user_agent=user_agent,
        )

        usuario.ultimo_acceso_at = datetime.now(timezone.utc)
        self.user_repo.db.add(usuario)
        self.user_repo.db.commit()

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
