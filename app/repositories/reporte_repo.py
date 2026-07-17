from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy import and_, extract, func, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.cuenta import Cuenta
from app.models.transaccion import Transaccion


class ReporteRepo:
    def __init__(self, db: Session):
        self.db = db

    # ── Resumen del mes ───────────────────────────────────────────────────────

    def get_resumen_mes(self, usuario_id: int, mes: int, anio: int) -> dict:
        base = and_(
            Transaccion.usuario_id == usuario_id,
            Transaccion.deleted_at.is_(None),
            extract("month", Transaccion.fecha) == mes,
            extract("year", Transaccion.fecha) == anio,
        )

        ingresos: Decimal = self.db.execute(
            select(func.coalesce(func.sum(Transaccion.monto), Decimal("0")))
            .where(base, Transaccion.tipo == "ingreso")
        ).scalar()

        gastos: Decimal = self.db.execute(
            select(func.coalesce(func.sum(Transaccion.monto), Decimal("0")))
            .where(base, Transaccion.tipo == "gasto")
        ).scalar()

        balance: Decimal = self.db.execute(
            select(func.coalesce(func.sum(Cuenta.saldo_actual), Decimal("0")))
            .where(
                Cuenta.usuario_id == usuario_id,
                Cuenta.deleted_at.is_(None),
                Cuenta.es_activa.is_(True),
                Cuenta.incluir_en_total.is_(True),
            )
        ).scalar()

        return {
            "mes": mes,
            "anio": anio,
            "total_ingresos": ingresos,
            "total_gastos": gastos,
            "neto": ingresos - gastos,
            "balance_total_cuentas": balance,
        }

    # ── Gastos por categoría ──────────────────────────────────────────────────

    def get_gastos_por_categoria(
        self, usuario_id: int, mes: int, anio: int
    ) -> List[dict]:
        rows = self.db.execute(
            select(
                Transaccion.categoria_id,
                func.coalesce(Categoria.nombre, "Sin categoría").label("nombre"),
                func.coalesce(Categoria.color, "#607D8B").label("color"),
                func.sum(Transaccion.monto).label("monto"),
            )
            .outerjoin(Categoria, Transaccion.categoria_id == Categoria.id)
            .where(
                Transaccion.usuario_id == usuario_id,
                Transaccion.deleted_at.is_(None),
                Transaccion.tipo == "gasto",
                extract("month", Transaccion.fecha) == mes,
                extract("year", Transaccion.fecha) == anio,
            )
            .group_by(Transaccion.categoria_id, Categoria.nombre, Categoria.color)
            .order_by(func.sum(Transaccion.monto).desc())
        ).all()

        total = sum(r.monto for r in rows) if rows else Decimal("0")

        return [
            {
                "categoria_id": r.categoria_id,
                "nombre": r.nombre,
                "color": r.color,
                "monto": r.monto,
                "porcentaje": float(r.monto / total * 100) if total > 0 else 0.0,
            }
            for r in rows
        ]

    # ── Flujo mensual (últimos N meses) ───────────────────────────────────────

    def get_flujo_mensual(self, usuario_id: int, meses: int) -> List[dict]:
        today = date.today()
        result = []

        for i in range(meses - 1, -1, -1):
            # Calculate target month going backwards
            mes_offset = today.month - i
            anio_target = today.year
            while mes_offset <= 0:
                mes_offset += 12
                anio_target -= 1

            base = and_(
                Transaccion.usuario_id == usuario_id,
                Transaccion.deleted_at.is_(None),
                extract("month", Transaccion.fecha) == mes_offset,
                extract("year", Transaccion.fecha) == anio_target,
            )

            ingresos: Decimal = self.db.execute(
                select(func.coalesce(func.sum(Transaccion.monto), Decimal("0")))
                .where(base, Transaccion.tipo == "ingreso")
            ).scalar()

            gastos: Decimal = self.db.execute(
                select(func.coalesce(func.sum(Transaccion.monto), Decimal("0")))
                .where(base, Transaccion.tipo == "gasto")
            ).scalar()

            result.append(
                {
                    "mes": mes_offset,
                    "anio": anio_target,
                    "ingresos": ingresos,
                    "gastos": gastos,
                    "neto": ingresos - gastos,
                }
            )

        return result
