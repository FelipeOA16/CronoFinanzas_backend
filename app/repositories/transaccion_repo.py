from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.cuenta import Cuenta
from app.models.transaccion import Transaccion


class TransaccionRepo:
    def __init__(self, db: Session):
        self.db = db

    # ── consultas ────────────────────────────────────────────────────────────

    def list_by_user(
        self,
        usuario_id: int,
        *,
        cuenta_id: int | None = None,
        tipo: str | None = None,
        categoria_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaccion]:
        q = (
            select(Transaccion)
            .where(
                Transaccion.usuario_id == usuario_id,
                Transaccion.deleted_at.is_(None),
            )
            .order_by(Transaccion.fecha.desc(), Transaccion.id.desc())
        )
        if cuenta_id:
            q = q.where(Transaccion.cuenta_id == cuenta_id)
        if tipo:
            q = q.where(Transaccion.tipo == tipo)
        if categoria_id:
            q = q.where(Transaccion.categoria_id == categoria_id)
        if fecha_desde:
            q = q.where(Transaccion.fecha >= fecha_desde)
        if fecha_hasta:
            q = q.where(Transaccion.fecha <= fecha_hasta)
        return self.db.execute(q.limit(limit).offset(offset)).scalars().all()

    def count_by_user(
        self,
        usuario_id: int,
        *,
        cuenta_id: int | None = None,
        tipo: str | None = None,
        categoria_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> int:
        from sqlalchemy import func as sqlfunc
        q = (
            select(sqlfunc.count())
            .select_from(Transaccion)
            .where(
                Transaccion.usuario_id == usuario_id,
                Transaccion.deleted_at.is_(None),
            )
        )
        if cuenta_id:
            q = q.where(Transaccion.cuenta_id == cuenta_id)
        if tipo:
            q = q.where(Transaccion.tipo == tipo)
        if categoria_id:
            q = q.where(Transaccion.categoria_id == categoria_id)
        if fecha_desde:
            q = q.where(Transaccion.fecha >= fecha_desde)
        if fecha_hasta:
            q = q.where(Transaccion.fecha <= fecha_hasta)
        return self.db.execute(q).scalar_one()

    def get_by_id(self, transaccion_id: int) -> Transaccion | None:
        return self.db.execute(
            select(Transaccion).where(
                Transaccion.id == transaccion_id,
                Transaccion.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    # ── mutaciones con actualización de saldo ────────────────────────────────

    def create(self, usuario_id: int, **kwargs) -> Transaccion:
        tx = Transaccion(usuario_id=usuario_id, **kwargs)
        self.db.add(tx)
        self.db.flush()
        self._apply_saldo(tx, reverse=False)
        return tx

    def update(self, tx: Transaccion, **kwargs) -> Transaccion:
        """Revierte el efecto anterior, aplica los datos nuevos y recalcula."""
        self._apply_saldo(tx, reverse=True)
        for k, v in kwargs.items():
            setattr(tx, k, v)
        self.db.flush()
        self._apply_saldo(tx, reverse=False)
        return tx

    def soft_delete(self, tx: Transaccion) -> None:
        self._apply_saldo(tx, reverse=True)
        tx.deleted_at = func.now()
        self.db.flush()

    # ── lógica de saldo ──────────────────────────────────────────────────────

    def _apply_saldo(self, tx: Transaccion, *, reverse: bool) -> None:
        """Ajusta saldo_actual en la(s) cuenta(s) según el tipo de transacción."""
        sign = Decimal("-1") if reverse else Decimal("1")
        monto = Decimal(str(tx.monto))

        cuenta = self.db.get(Cuenta, tx.cuenta_id)
        if not cuenta:
            return

        if tx.tipo == "ingreso":
            cuenta.saldo_actual = Decimal(str(cuenta.saldo_actual)) + sign * monto
        elif tx.tipo == "gasto":
            cuenta.saldo_actual = Decimal(str(cuenta.saldo_actual)) - sign * monto
        elif tx.tipo == "transferencia":
            cuenta.saldo_actual = Decimal(str(cuenta.saldo_actual)) - sign * monto
            if tx.cuenta_destino_id:
                destino = self.db.get(Cuenta, tx.cuenta_destino_id)
                if destino:
                    destino.saldo_actual = Decimal(str(destino.saldo_actual)) + sign * monto
                    self.db.add(destino)

        self.db.add(cuenta)
        self.db.flush()
