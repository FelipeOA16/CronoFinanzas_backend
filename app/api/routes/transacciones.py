from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import Usuario
from app.repositories.categoria_repo import CategoriaRepo
from app.repositories.cuenta_repo import CuentaRepo
from app.repositories.transaccion_repo import TransaccionRepo
from app.schemas.transaccion import (
    TransaccionCreate,
    TransaccionOut,
    TransaccionUpdate,
    TransaccionesPaginadas,
)

router = APIRouter()


def _validar_categoria(categoria_id: int | None, usuario_id: int, db: Session) -> None:
    if categoria_id is None:
        return
    categoria = CategoriaRepo(db).get_by_id(categoria_id)
    if not categoria or (
        categoria.usuario_id is not None and categoria.usuario_id != usuario_id
    ):
        raise HTTPException(status_code=403, detail="Categoria no valida")


def _get_transaccion_or_403(tx_id: int, usuario_id: int, db: Session):
    repo = TransaccionRepo(db)
    tx = repo.get_by_id(tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    if tx.usuario_id != usuario_id:
        raise HTTPException(status_code=403, detail="No autorizado")
    return tx


@router.get("/", response_model=TransaccionesPaginadas)
def listar_transacciones(
    cuenta_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    categoria_id: Optional[int] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = TransaccionRepo(db)
    filters = dict(
        cuenta_id=cuenta_id,
        tipo=tipo,
        categoria_id=categoria_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    items = repo.list_by_user(current_user.id, **filters, limit=limit, offset=offset)
    total = repo.count_by_user(current_user.id, **filters)
    return TransaccionesPaginadas(items=items, total=total, limit=limit, offset=offset)


@router.post("/", response_model=TransaccionOut, status_code=status.HTTP_201_CREATED)
def crear_transaccion(
    data: TransaccionCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validar ownership de la cuenta origen
    cuenta_repo = CuentaRepo(db)
    cuenta = cuenta_repo.get_by_id(data.cuenta_id)
    if not cuenta or cuenta.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cuenta no válida")

    # Validar cuenta destino para transferencias
    if data.tipo == "transferencia":
        if not data.cuenta_destino_id:
            raise HTTPException(status_code=422, detail="cuenta_destino_id es requerido para transferencias")
        destino = cuenta_repo.get_by_id(data.cuenta_destino_id)
        if not destino or destino.usuario_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cuenta destino no válida")

    _validar_categoria(data.categoria_id, current_user.id, db)
    repo = TransaccionRepo(db)
    tx = repo.create(current_user.id, **data.model_dump())
    db.commit()
    db.refresh(tx)
    return tx


@router.get("/{transaccion_id}", response_model=TransaccionOut)
def obtener_transaccion(
    transaccion_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_transaccion_or_403(transaccion_id, current_user.id, db)


@router.patch("/{transaccion_id}", response_model=TransaccionOut)
def actualizar_transaccion(
    transaccion_id: int,
    data: TransaccionUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = _get_transaccion_or_403(transaccion_id, current_user.id, db)
    repo = TransaccionRepo(db)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    _validar_categoria(updates.get("categoria_id"), current_user.id, db)
    final_tipo = updates.get("tipo", tx.tipo)
    final_destino_id = updates.get("cuenta_destino_id", tx.cuenta_destino_id)
    if final_tipo == "transferencia" and not final_destino_id:
        raise HTTPException(status_code=422, detail="cuenta_destino_id es requerido para transferencias")
    if final_tipo != "transferencia":
        updates["cuenta_destino_id"] = None
    tx = repo.update(tx, **updates)
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(
    transaccion_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = _get_transaccion_or_403(transaccion_id, current_user.id, db)
    TransaccionRepo(db).soft_delete(tx)
    db.commit()
