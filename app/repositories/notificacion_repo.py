from datetime import date
from typing import List

from sqlalchemy.orm import Session

from app.repositories.presupuesto_repo import PresupuestoRepo
from app.schemas.notificacion import NotificacionOut


class NotificacionRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_alertas_activas(self, usuario_id: int) -> List[NotificacionOut]:
        today = date.today()
        presupuestos = PresupuestoRepo(self.db).list_by_usuario(
            usuario_id, mes=today.month, anio=today.year
        )
        resultado: List[NotificacionOut] = []
        for p in presupuestos:
            if p.estado not in ("alerta", "excedido"):
                continue
            nombre_cat = (
                p.categoria.nombre
                if p.categoria_id is not None and p.categoria is not None
                else "Global"
            )
            excedido = p.estado == "excedido"
            resultado.append(
                NotificacionOut(
                    tipo=p.estado,
                    titulo="Presupuesto excedido" if excedido else "Presupuesto en alerta",
                    mensaje=f"{nombre_cat}: {p.porcentaje:.0f}% del límite mensual",
                    presupuesto_id=p.id,
                    porcentaje=float(p.porcentaje),
                )
            )
        return resultado
