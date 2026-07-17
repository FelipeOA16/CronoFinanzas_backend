from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import Usuario
from app.repositories.deuda_prestamo_repo import DeudaPrestamoRepo
from app.schemas.deuda_prestamo import (
    DeudaPrestamoCreate,
    DeudaPrestamoListOut,
    DeudaPrestamoOut,
    DeudaPrestamoResumenOut,
    DeudaPrestamoUpdate,
    PagoDeudaPrestamoCreate,
    PagoDeudaPrestamoOut,
)

router = APIRouter()


def _repo(db: Session) -> DeudaPrestamoRepo:
    return DeudaPrestamoRepo(db)


def _get_or_404(repo: DeudaPrestamoRepo, deuda_id: int, usuario_id: int):
    deuda = repo.obtener(deuda_id, usuario_id)
    if not deuda:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deuda/prestamo no encontrado")
    return deuda


@router.get("/", response_model=List[DeudaPrestamoListOut])
def listar_deudas_prestamos(
    tipo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    vencen_hasta: Optional[date] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _repo(db).listar(
        current_user.id,
        tipo=tipo,
        estado=estado,
        prioridad=prioridad,
        vencen_hasta=vencen_hasta,
        search=search,
    )


@router.post("/", response_model=DeudaPrestamoOut, status_code=status.HTTP_201_CREATED)
def crear_deuda_prestamo(
    payload: DeudaPrestamoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    try:
        deuda = repo.crear(current_user.id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    db.refresh(deuda)
    return deuda


@router.get("/resumen", response_model=DeudaPrestamoResumenOut)
def resumen_deudas_prestamos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _repo(db).resumen(current_user.id)


@router.get("/{deuda_id}", response_model=DeudaPrestamoOut)
def obtener_deuda_prestamo(
    deuda_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_404(_repo(db), deuda_id, current_user.id)


@router.patch("/{deuda_id}", response_model=DeudaPrestamoOut)
def actualizar_deuda_prestamo(
    deuda_id: int,
    payload: DeudaPrestamoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    deuda = _get_or_404(repo, deuda_id, current_user.id)
    try:
        deuda = repo.actualizar(deuda, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    db.refresh(deuda)
    return deuda


@router.delete("/{deuda_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_deuda_prestamo(
    deuda_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    deuda = _get_or_404(repo, deuda_id, current_user.id)
    repo.soft_delete(deuda)
    db.commit()


@router.get("/{deuda_id}/pagos", response_model=List[PagoDeudaPrestamoOut])
def listar_pagos(
    deuda_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    _get_or_404(repo, deuda_id, current_user.id)
    return repo.listar_pagos(deuda_id, current_user.id)


@router.post("/{deuda_id}/pagos", response_model=PagoDeudaPrestamoOut, status_code=status.HTTP_201_CREATED)
def registrar_pago(
    deuda_id: int,
    payload: PagoDeudaPrestamoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    deuda = _get_or_404(repo, deuda_id, current_user.id)
    try:
        pago = repo.registrar_pago(deuda, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    db.refresh(pago)
    return pago


@router.delete("/{deuda_id}/pagos/{pago_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_pago(
    deuda_id: int,
    pago_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    deuda = _get_or_404(repo, deuda_id, current_user.id)
    try:
        repo.eliminar_pago(deuda, pago_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
