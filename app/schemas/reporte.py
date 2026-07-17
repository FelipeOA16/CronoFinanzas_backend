from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class ResumenMes(BaseModel):
    mes: int
    anio: int
    total_ingresos: Decimal
    total_gastos: Decimal
    neto: Decimal
    balance_total_cuentas: Decimal


class GastoCategoria(BaseModel):
    categoria_id: Optional[int] = None
    nombre: str
    color: str
    monto: Decimal
    porcentaje: float


class FlujoMes(BaseModel):
    mes: int
    anio: int
    ingresos: Decimal
    gastos: Decimal
    neto: Decimal


class ReporteResumenResponse(BaseModel):
    resumen: ResumenMes
    gastos_por_categoria: List[GastoCategoria]
    flujo_mensual: List[FlujoMes]
