from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import Usuario
from app.repositories.meta_financiera_repo import MetaFinancieraRepo
from app.schemas.meta_financiera import (
    AporteMetaCreate,
    AporteMetaOut,
    MetaFinancieraCreate,
    MetaFinancieraListOut,
    MetaFinancieraOut,
    MetaFinancieraResumenOut,
    MetaFinancieraUpdate,
)

router = APIRouter()


def _repo(db: Session) -> MetaFinancieraRepo:
    return MetaFinancieraRepo(db)


def _get_or_404(repo: MetaFinancieraRepo, meta_id: int, usuario_id: int):
    meta = repo.obtener(meta_id, usuario_id)
    if not meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta financiera no encontrada")
    return meta


@router.get("/", response_model=List[MetaFinancieraListOut])
def listar_metas(
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _repo(db).listar(
        current_user.id,
        estado=estado,
        prioridad=prioridad,
        search=search,
    )


@router.post("/", response_model=MetaFinancieraOut, status_code=status.HTTP_201_CREATED)
def crear_meta(
    payload: MetaFinancieraCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    try:
        meta = repo.crear(current_user.id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    db.refresh(meta)
    return meta


@router.get("/resumen", response_model=MetaFinancieraResumenOut)
def resumen_metas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _repo(db).resumen(current_user.id)


@router.get("/{meta_id}", response_model=MetaFinancieraOut)
def obtener_meta(
    meta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_404(_repo(db), meta_id, current_user.id)


@router.patch("/{meta_id}", response_model=MetaFinancieraOut)
def actualizar_meta(
    meta_id: int,
    payload: MetaFinancieraUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    meta = _get_or_404(repo, meta_id, current_user.id)
    try:
        meta = repo.actualizar(meta, payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    db.refresh(meta)
    return meta


@router.delete("/{meta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_meta(
    meta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    meta = _get_or_404(repo, meta_id, current_user.id)
    repo.soft_delete(meta)
    db.commit()


@router.get("/{meta_id}/aportes", response_model=List[AporteMetaOut])
def listar_aportes(
    meta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    _get_or_404(repo, meta_id, current_user.id)
    return repo.listar_aportes(meta_id, current_user.id)


@router.post("/{meta_id}/aportes", response_model=AporteMetaOut, status_code=status.HTTP_201_CREATED)
def registrar_aporte(
    meta_id: int,
    payload: AporteMetaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    meta = _get_or_404(repo, meta_id, current_user.id)
    try:
        aporte = repo.registrar_aporte(meta, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    db.refresh(aporte)
    return aporte


@router.delete("/{meta_id}/aportes/{aporte_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_aporte(
    meta_id: int,
    aporte_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = _repo(db)
    meta = _get_or_404(repo, meta_id, current_user.id)
    try:
        repo.eliminar_aporte(meta, aporte_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
