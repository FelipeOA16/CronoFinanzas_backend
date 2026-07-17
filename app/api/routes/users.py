from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.repositories.user_repo import UserRepo
from app.repositories.credential_repo import CredentialRepo
from app.repositories.role_repo import RoleRepo
from app.repositories.auth_provider_repo import AuthProviderRepo
from app.repositories.session_repo import SessionRepo
from app.schemas.user import UserOut, UpdatePerfilRequest, ChangePasswordRequest, ProveedorAuthOut
from app.schemas.auth import SesionOut
from app.core.security import hash_password, verify_password

router = APIRouter()


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return [UserOut.from_orm_with_roles(u) for u in UserRepo(db).list_users()]


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    usuario = UserRepo(db).get_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserOut.from_orm_with_roles(usuario)


@router.patch("/{user_id}/perfil", response_model=UserOut)
def update_perfil(
    user_id: int,
    payload: UpdatePerfilRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    usuario = UserRepo(db).get_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(usuario, field, value)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return UserOut.from_orm_with_roles(usuario)


@router.patch("/{user_id}/password", response_model=UserOut)
def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    usuario = UserRepo(db).get_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cred = CredentialRepo(db).get_by_usuario(user_id)
    if not cred:
        raise HTTPException(status_code=404, detail="Credenciales no encontradas")
    if not verify_password(payload.current_password, cred.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    CredentialRepo(db).update_password(cred, hash_password(payload.new_password))
    return UserOut.from_orm_with_roles(usuario)


@router.delete("/{user_id}", response_model=UserOut)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    usuario = UserRepo(db).get_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserOut.from_orm_with_roles(UserRepo(db).soft_delete(usuario))


# ─── Roles (solo admin) ─────────────────────────────────────────────────────


@router.post("/{user_id}/roles/{nombre_rol}", response_model=UserOut)
def assign_role(
    user_id: int,
    nombre_rol: str,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    usuario = UserRepo(db).get_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    try:
        RoleRepo(db).assign_role(usuario, nombre_rol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(usuario)
    return UserOut.from_orm_with_roles(usuario)


@router.delete("/{user_id}/roles/{nombre_rol}", response_model=UserOut)
def remove_role(
    user_id: int,
    nombre_rol: str,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin")),
):
    usuario = UserRepo(db).get_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    RoleRepo(db).remove_role(usuario, nombre_rol)
    db.commit()
    db.refresh(usuario)
    return UserOut.from_orm_with_roles(usuario)


# ─── Proveedores de autenticación ───────────────────────────────────────────


@router.get("/{user_id}/providers", response_model=List[ProveedorAuthOut])
def list_providers(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return AuthProviderRepo(db).list_by_user(user_id)


@router.delete("/{user_id}/providers/{proveedor}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_provider(
    user_id: int,
    proveedor: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    found = AuthProviderRepo(db).unlink_provider(user_id, proveedor)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
    db.commit()


# ─── Sesiones activas ───────────────────────────────────────────────────────


@router.get("/{user_id}/sessions", response_model=List[SesionOut])
def list_sessions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return SessionRepo(db).list_active_for_user(user_id)


@router.delete("/{user_id}/sessions/{session_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(
    user_id: int,
    session_uuid: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    session_repo = SessionRepo(db)
    sesion = session_repo.get_by_uuid(session_uuid)
    if not sesion or sesion.usuario_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    session_repo.revoke_session(sesion, motivo="revoked_by_user")
    db.commit()


@router.delete("/{user_id}/sessions", status_code=status.HTTP_204_NO_CONTENT)
def revoke_all_sessions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    SessionRepo(db).revoke_all_for_user(user_id, motivo="revoked_all_by_user")
    db.commit()
