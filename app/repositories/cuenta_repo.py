from typing import List, Optional

from sqlalchemy import Integer as sqlalchemy_Integer, func, or_, select
from sqlalchemy.orm import Session

from app.models.cuenta import Cuenta
from app.models.deuda_prestamo import DeudaPrestamo, PagoDeudaPrestamo
from app.models.meta_financiera import AporteMeta, MetaFinanciera
from app.models.transaccion import Transaccion


class CuentaRepo:
    def __init__(self, db: Session):
        self.db = db

    def list_by_user(self, usuario_id: int) -> List[Cuenta]:
        return (
            self.db.execute(
                select(Cuenta)
                .where(
                    Cuenta.usuario_id == usuario_id,
                    Cuenta.deleted_at.is_(None),
                )
                .order_by(Cuenta.id)
            )
            .scalars()
            .all()
        )

    def get_by_id(self, cuenta_id: int) -> Optional[Cuenta]:
        return self.db.execute(
            select(Cuenta).where(
                Cuenta.id == cuenta_id,
                Cuenta.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def create(self, usuario_id: int, **kwargs) -> Cuenta:
        cuenta = Cuenta(
            usuario_id=usuario_id,
            saldo_actual=kwargs.get("saldo_inicial", 0),
            **kwargs,
        )
        self.db.add(cuenta)
        self.db.flush()
        return cuenta

    def update(self, cuenta: Cuenta, **kwargs) -> Cuenta:
        for field, value in kwargs.items():
            setattr(cuenta, field, value)
        self.db.add(cuenta)
        return cuenta

    def soft_delete(self, cuenta: Cuenta) -> None:
        from datetime import datetime, timezone
        cuenta.deleted_at = datetime.now(timezone.utc)
        self.db.add(cuenta)

    def has_linked_history(self, cuenta_id: int, usuario_id: int) -> bool:
        transacciones = self.db.scalar(
            select(func.count(Transaccion.id)).where(
                Transaccion.usuario_id == usuario_id,
                or_(
                    Transaccion.cuenta_id == cuenta_id,
                    Transaccion.cuenta_destino_id == cuenta_id,
                ),
            )
        ) or 0
        if transacciones > 0:
            return True

        deudas = self.db.scalar(
            select(func.count(DeudaPrestamo.id)).where(
                DeudaPrestamo.usuario_id == usuario_id,
                DeudaPrestamo.cuenta_id == cuenta_id,
            )
        ) or 0
        if deudas > 0:
            return True

        pagos = self.db.scalar(
            select(func.count(PagoDeudaPrestamo.id)).where(
                PagoDeudaPrestamo.usuario_id == usuario_id,
                PagoDeudaPrestamo.cuenta_id == cuenta_id,
            )
        ) or 0
        if pagos > 0:
            return True

        metas = self.db.scalar(
            select(func.count(MetaFinanciera.id)).where(
                MetaFinanciera.usuario_id == usuario_id,
                MetaFinanciera.cuenta_id == cuenta_id,
            )
        ) or 0
        if metas > 0:
            return True

        aportes = self.db.scalar(
            select(func.count(AporteMeta.id)).where(
                AporteMeta.usuario_id == usuario_id,
                AporteMeta.cuenta_id == cuenta_id,
            )
        ) or 0
        return aportes > 0

    def resumen(self, usuario_id: int) -> dict:
        from decimal import Decimal as D
        from sqlalchemy import func as sqlfunc

        rows = (
            self.db.execute(
                select(
                    sqlfunc.coalesce(sqlfunc.sum(Cuenta.saldo_actual), 0).label("total"),
                    sqlfunc.count(Cuenta.id).label("total_cuentas"),
                    sqlfunc.sum(
                        sqlfunc.cast(
                            Cuenta.es_activa, sqlalchemy_Integer
                        )
                    ).label("activas"),
                ).where(
                    Cuenta.usuario_id == usuario_id,
                    Cuenta.deleted_at.is_(None),
                    Cuenta.incluir_en_total == True,  # noqa: E712
                )
            )
            .mappings()
            .one()
        )
        return {
            "total_patrimonio": D(str(rows["total"] or 0)),
            "total_cuentas": rows["total_cuentas"] or 0,
            "total_cuentas_activas": rows["activas"] or 0,
        }

    def nombre_exists(self, usuario_id: int, nombre: str, exclude_id: Optional[int] = None) -> bool:
        q = select(Cuenta).where(
            Cuenta.usuario_id == usuario_id,
            Cuenta.nombre == nombre,
            Cuenta.deleted_at.is_(None),
        )
        if exclude_id is not None:
            q = q.where(Cuenta.id != exclude_id)
        return self.db.execute(q).scalar_one_or_none() is not None
