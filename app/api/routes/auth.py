from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.auth import (
    ForgotPasswordRequest,
    RegisterRequest,
    LoginRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.token import TokenResponse, RefreshRequest, LogoutRequest
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.services.email_service import send_reset_password_email, send_verification_email
from app.repositories.user_repo import UserRepo
from app.repositories.credential_repo import CredentialRepo
from app.repositories.session_repo import SessionRepo
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_password
from app.core.config import Settings

import secrets
from datetime import datetime, timedelta, timezone

router = APIRouter()
settings = Settings()

_RESET_TOKEN_TTL_HOURS = 1
_VERIF_TOKEN_TTL_HOURS = 24


def _make_service(db: Session) -> AuthService:
    return AuthService(
        user_repo=UserRepo(db),
        cred_repo=CredentialRepo(db),
        session_repo=SessionRepo(db),
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    svc = _make_service(db)
    try:
        usuario = svc.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Send email verification automatically after registration
    cred = CredentialRepo(db).get_by_usuario(usuario.id)
    if cred:
        token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=_VERIF_TOKEN_TTL_HOURS)
        CredentialRepo(db).set_email_verification_token(cred, token, expires_at)
        db.commit()
        await send_verification_email(usuario.email, token)

    return UserOut.from_orm_with_roles(usuario)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    svc = _make_service(db)
    return svc.login(data, request=request)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    old_token = payload.refresh_token
    session_repo = SessionRepo(db)

    sesion = session_repo.get_by_refresh_token(old_token)
    if not sesion:
        raise HTTPException(status_code=401, detail="Refresh token inválido o revocado")

    try:
        data = decode_refresh_token(old_token)
        usuario_id = int(data.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    usuario = UserRepo(db).get_by_id(usuario_id)
    if not usuario or usuario.estado_cuenta != "activo":
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    new_access = create_access_token(
        subject=str(usuario_id),
        roles=[r.nombre for r in usuario.roles],
    )
    new_refresh = create_refresh_token(subject=str(usuario_id))

    session_repo.rotate_session(
        sesion=sesion,
        new_access_token=new_access,
        new_refresh_token=new_refresh,
        expires_delta_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )
    db.commit()

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    sesion = SessionRepo(db).get_by_refresh_token(payload.refresh_token)
    if sesion:
        SessionRepo(db).revoke_session(sesion, motivo="logout")
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut)
def me(usuario=Depends(get_current_user)):
    return UserOut.from_orm_with_roles(usuario)


# ── Forgot / Reset password ────────────────────────────────────────────────────

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Always returns 200 regardless of whether the email exists,
    to prevent user enumeration attacks.
    """
    usuario = UserRepo(db).get_by_email(data.email)
    if usuario:
        cred = CredentialRepo(db).get_by_usuario(usuario.id)
        if cred:
            token = secrets.token_hex(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=_RESET_TOKEN_TTL_HOURS)
            CredentialRepo(db).set_reset_token(cred, token, expires_at)
            db.commit()
            await send_reset_password_email(usuario.email, token)
    return {"detail": "Si el correo existe, recibirás un enlace en breve."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    cred_repo = CredentialRepo(db)
    cred = cred_repo.get_by_reset_token(data.token)
    if not cred:
        raise HTTPException(
            status_code=400,
            detail="El enlace de recuperación es inválido o ha expirado.",
        )
    new_hash = hash_password(data.new_password)
    cred_repo.update_password(cred, new_hash)
    cred_repo.clear_reset_token(cred)
    # Revoke all active sessions so any attacker is logged out
    SessionRepo(db).revoke_all_for_user(cred.usuario_id, motivo="password_reset")
    db.commit()
    return {"detail": "Contraseña restablecida correctamente. Inicia sesión con tu nueva contraseña."}


# ── Email verification ──────────────────────────────────────────────────────────

@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    cred_repo = CredentialRepo(db)
    cred = cred_repo.get_by_email_verification_token(data.token)
    if not cred:
        raise HTTPException(
            status_code=400,
            detail="El enlace de verificación es inválido o ha expirado.",
        )
    cred_repo.mark_email_verified(cred)
    db.commit()
    return {"detail": "Correo verificado correctamente."}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    db: Session = Depends(get_db),
    usuario=Depends(get_current_user),
):
    cred = CredentialRepo(db).get_by_usuario(usuario.id)
    if not cred:
        raise HTTPException(status_code=404, detail="Credenciales no encontradas")
    if cred.email_verificado:
        return {"detail": "El correo ya está verificado."}
    token = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=_VERIF_TOKEN_TTL_HOURS)
    CredentialRepo(db).set_email_verification_token(cred, token, expires_at)
    db.commit()
    await send_verification_email(usuario.email, token)
    return {"detail": "Correo de verificación enviado."}
