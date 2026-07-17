from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.repositories.categoria_repo import CategoriaRepo
from app.repositories.presupuesto_repo import PresupuestoRepo
from app.schemas.presupuesto import PresupuestoCreate, PresupuestoOut, PresupuestoUpdate

router = APIRouter()


def _validar_categoria(categoria_id: int | None, usuario_id: int, db: Session) -> None:
    if categoria_id is None:
        return
    categoria = CategoriaRepo(db).get_by_id(categoria_id)
    if not categoria or (
        categoria.usuario_id is not None and categoria.usuario_id != usuario_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Categoria no valida")


def _get_presupuesto_or_403(presupuesto_id: int, usuario_id: int, db: Session):
    p = PresupuestoRepo(db).get_by_id(presupuesto_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presupuesto no encontrado")
    if p.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return p


@router.get("/", response_model=List[PresupuestoOut])
def list_presupuestos(
    mes: Optional[int] = Query(None),
    anio: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return PresupuestoRepo(db).list_by_usuario(current_user.id, mes=mes, anio=anio)


@router.post("/", response_model=PresupuestoOut, status_code=status.HTTP_201_CREATED)
def create_presupuesto(
    body: PresupuestoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _validar_categoria(body.categoria_id, current_user.id, db)
    return PresupuestoRepo(db).create(current_user.id, body.model_dump())


@router.put("/{presupuesto_id}", response_model=PresupuestoOut)
def update_presupuesto(
    presupuesto_id: int,
    body: PresupuestoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = _get_presupuesto_or_403(presupuesto_id, current_user.id, db)
    return PresupuestoRepo(db).update(p, body.model_dump(exclude_none=True))


@router.delete("/{presupuesto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presupuesto(
    presupuesto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = _get_presupuesto_or_403(presupuesto_id, current_user.id, db)
    PresupuestoRepo(db).delete(p)
