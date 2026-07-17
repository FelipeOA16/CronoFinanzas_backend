from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.repositories.cuenta_repo import CuentaRepo
from app.schemas.cuenta import CuentaCreate, CuentaOut, CuentaUpdate, CuentasResumen

router = APIRouter()

CUENTA_CON_HISTORIAL_MSG = (
    "No puedes eliminar esta cuenta porque tiene movimientos o deudas vinculadas. "
    "Puedes desactivarla para conservar el historial."
)


def _get_cuenta_or_403(cuenta_id: int, usuario_id: int, db: Session):
    cuenta = CuentaRepo(db).get_by_id(cuenta_id)
    if not cuenta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
    if cuenta.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return cuenta


@router.get("/resumen", response_model=CuentasResumen)
def get_resumen(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CuentaRepo(db).resumen(current_user.id)


@router.get("/", response_model=List[CuentaOut])
def list_cuentas(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return CuentaRepo(db).list_by_user(current_user.id)


@router.post("/", response_model=CuentaOut, status_code=status.HTTP_201_CREATED)
def create_cuenta(
    payload: CuentaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = CuentaRepo(db)
    if repo.nombre_exists(current_user.id, payload.nombre):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una cuenta con el nombre '{payload.nombre}'",
        )
    cuenta = repo.create(current_user.id, **payload.model_dump())
    db.commit()
    db.refresh(cuenta)
    return cuenta


@router.get("/{cuenta_id}", response_model=CuentaOut)
def get_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return _get_cuenta_or_403(cuenta_id, current_user.id, db)


@router.patch("/{cuenta_id}", response_model=CuentaOut)
def update_cuenta(
    cuenta_id: int,
    payload: CuentaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = CuentaRepo(db)
    cuenta = _get_cuenta_or_403(cuenta_id, current_user.id, db)
    changes = payload.model_dump(exclude_none=True)
    if "nombre" in changes and changes["nombre"] != cuenta.nombre:
        if repo.nombre_exists(current_user.id, changes["nombre"], exclude_id=cuenta_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una cuenta con el nombre '{changes['nombre']}'",
            )
    repo.update(cuenta, **changes)
    db.commit()
    db.refresh(cuenta)
    return cuenta


@router.delete("/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = CuentaRepo(db)
    cuenta = _get_cuenta_or_403(cuenta_id, current_user.id, db)
    if repo.has_linked_history(cuenta.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=CUENTA_CON_HISTORIAL_MSG,
        )
    repo.soft_delete(cuenta)
    db.commit()
