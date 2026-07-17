from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import Usuario
from app.repositories.reporte_repo import ReporteRepo
from app.schemas.reporte import (
    FlujoMes,
    GastoCategoria,
    ReporteResumenResponse,
    ResumenMes,
)

router = APIRouter()


@router.get("/resumen", response_model=ReporteResumenResponse)
def get_reporte_resumen(
    mes: int = Query(default=None, ge=1, le=12),
    anio: int = Query(default=None, ge=2000),
    meses_flujo: int = Query(default=6, ge=1, le=24),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna en una sola llamada:
    - Resumen del mes (ingresos, gastos, neto, balance total)
    - Gastos por categoría del mes
    - Flujo de los últimos `meses_flujo` meses
    """
    today = date.today()
    mes_target = mes or today.month
    anio_target = anio or today.year

    repo = ReporteRepo(db)

    resumen_data = repo.get_resumen_mes(current_user.id, mes_target, anio_target)
    gastos_data = repo.get_gastos_por_categoria(
        current_user.id, mes_target, anio_target
    )
    flujo_data = repo.get_flujo_mensual(current_user.id, meses_flujo)

    return ReporteResumenResponse(
        resumen=ResumenMes(**resumen_data),
        gastos_por_categoria=[GastoCategoria(**g) for g in gastos_data],
        flujo_mensual=[FlujoMes(**f) for f in flujo_data],
    )
