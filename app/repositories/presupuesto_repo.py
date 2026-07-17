from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.presupuesto import Presupuesto
from app.models.transaccion import Transaccion


class PresupuestoRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_by_usuario(self, usuario_id: int, mes: Optional[int] = None, anio: Optional[int] = None) -> List[Presupuesto]:
        q = self.db.query(Presupuesto).filter(Presupuesto.usuario_id == usuario_id)
        if mes:
            q = q.filter(Presupuesto.mes == mes)
        if anio:
            q = q.filter(Presupuesto.anio == anio)
        presupuestos = q.order_by(Presupuesto.categoria_id.asc().nullsfirst(), Presupuesto.id).all()
        # Añadir campos calculados
        for p in presupuestos:
            p.monto_gastado, p.porcentaje, p.estado = self._calcular_gasto(p)
        return presupuestos

    def get_by_id(self, presupuesto_id: int) -> Optional[Presupuesto]:
        return self.db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()

    def create(self, usuario_id: int, data: dict) -> Presupuesto:
        presupuesto = Presupuesto(usuario_id=usuario_id, **data)
        self.db.add(presupuesto)
        self.db.commit()
        self.db.refresh(presupuesto)
        presupuesto.monto_gastado, presupuesto.porcentaje, presupuesto.estado = self._calcular_gasto(presupuesto)
        return presupuesto

    def update(self, presupuesto: Presupuesto, data: dict) -> Presupuesto:
        for key, value in data.items():
            setattr(presupuesto, key, value)
        self.db.commit()
        self.db.refresh(presupuesto)
        presupuesto.monto_gastado, presupuesto.porcentaje, presupuesto.estado = self._calcular_gasto(presupuesto)
        return presupuesto

    def delete(self, presupuesto: Presupuesto) -> None:
        self.db.delete(presupuesto)
        self.db.commit()

    def _calcular_gasto(self, p: Presupuesto):
        """Suma los gastos del usuario en el mes/año del presupuesto."""
        from sqlalchemy import extract
        q = self.db.query(func.coalesce(func.sum(Transaccion.monto), 0)).filter(
            Transaccion.usuario_id == p.usuario_id,
            Transaccion.tipo == "gasto",
            Transaccion.deleted_at.is_(None),
            extract("month", Transaccion.fecha) == p.mes,
            extract("year", Transaccion.fecha) == p.anio,
        )
        if p.categoria_id is not None:
            # Presupuesto por categoría
            q = q.filter(Transaccion.categoria_id == p.categoria_id)
        # else: presupuesto global — suma todos los gastos del mes

        gastado = Decimal(str(q.scalar() or 0))
        limite = Decimal(str(p.monto_limite))
        porcentaje = float(gastado / limite * 100) if limite > 0 else 0.0

        if porcentaje >= 100:
            estado = "excedido"
        elif porcentaje >= 80:
            estado = "alerta"
        else:
            estado = "ok"

        return gastado, round(porcentaje, 1), estado
