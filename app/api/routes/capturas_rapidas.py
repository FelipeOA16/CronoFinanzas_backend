from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.captura_rapida import ESTADOS_CAPTURA_RAPIDA, TIPOS_CAPTURA_RAPIDA
from app.models.user import Usuario
from app.repositories.captura_rapida_repo import CapturaRapidaRepo
from app.schemas.captura_rapida import (
    CapturaRapidaCreate,
    CapturaRapidaOut,
    CapturaRapidaResumenOut,
    CapturaRapidaUpdate,
    CompletarCapturaRapida,
)

router = APIRouter()


def _repo(db: Session) -> CapturaRapidaRepo:
    return CapturaRapidaRepo(db)


def _get_or_404(
    repo: CapturaRapidaRepo,
    captura_id: int,
    usuario_id: int,
):
    captura = repo.obtener(captura_id, usuario_id)
    if not captura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Captura rapida no encontrada",
        )
    return captura


def _unprocessable(exc: ValueError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
    )


@router.get("/", response_model=List[CapturaRapidaOut])
def listar_capturas(
    estado: Optional[str] = Query(None),
    tipo: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if estado is not None and estado not in ESTADOS_CAPTURA_RAPIDA:
        raise HTTPException(status_code=422, detail="estado no valido")
    if tipo is not None and tipo not in TIPOS_CAPTURA_RAPIDA:
        raise HTTPException(status_code=422, detail="tipo no valido")
    return _repo(db).listar(current_user.id, estado=estado, tipo=tipo)


@router.post(
    "/",
    response_model=CapturaRapidaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_captura(
    payload: CapturaRapidaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        captura = _repo(db).crear(current_user.id, payload.model_dump())
    except ValueError as exc:
        raise _unprocessable(exc)
    db.commit()
    db.refresh(captura)
    return captura


@router.get("/resumen", response_model=CapturaRapidaResumenOut)
def resumen_capturas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _repo(db).resumen(current_user.id)


@router.get("/{captura_id}", response_model=CapturaRapidaOut)
def obtener_captura(
    captura_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_404(_repo(db), captura_id, current_user.id)


@router.patch("/{captura_id}", response_model=CapturaRapidaOut)
def actualizar_captura(
    captura_id: int,
    payload: CapturaRapidaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    captura = _get_or_404(repo, captura_id, current_user.id)
    try:
        captura = repo.actualizar(
            captura,
            payload.model_dump(exclude_unset=True),
        )
    except ValueError as exc:
        raise _unprocessable(exc)
    db.commit()
    db.refresh(captura)
    return captura


@router.post("/{captura_id}/completar", response_model=CapturaRapidaOut)
def completar_captura(
    captura_id: int,
    payload: CompletarCapturaRapida,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        captura = _repo(db).completar(
            captura_id,
            current_user.id,
            payload.model_dump(exclude_none=True),
        )
    except ValueError as exc:
        db.rollback()
        raise _unprocessable(exc)
    db.commit()
    db.refresh(captura)
    return captura


@router.delete("/{captura_id}", status_code=status.HTTP_204_NO_CONTENT)
def descartar_captura(
    captura_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    captura = _get_or_404(repo, captura_id, current_user.id)
    try:
        repo.descartar(captura)
    except ValueError as exc:
        raise _unprocessable(exc)
    db.commit()
