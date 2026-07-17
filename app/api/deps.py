from typing import Callable, Generator, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.repositories.user_repo import UserRepo
from app.models.user import Usuario

settings = Settings()
bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials or not credentials.scheme or credentials.scheme.lower() != "bearer":
        raise credentials_exception

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        usuario_id = int(payload.get("sub"))
    except Exception:
        raise credentials_exception

    usuario = UserRepo(db).get_by_id(usuario_id)
    if not usuario:
        raise credentials_exception
    if usuario.estado_cuenta != "activo":
        raise HTTPException(status_code=403, detail="Cuenta inactiva")
    return usuario


def require_roles(*roles: str) -> Callable:
    """Returns a FastAPI dependency that verifies the user has at least one of the required roles."""
    def _check(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if not roles:
            return usuario
        user_roles = {r.nombre for r in usuario.roles}
        if not user_roles.intersection(roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los roles: {list(roles)}",
            )
        return usuario
    return _check
