from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.repositories.notificacion_repo import NotificacionRepo
from app.schemas.notificacion import NotificacionOut

router = APIRouter()


@router.get("/", response_model=List[NotificacionOut])
def list_notificaciones(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Devuelve las alertas activas de presupuesto del mes actual."""
    return NotificacionRepo(db).get_alertas_activas(current_user.id)
