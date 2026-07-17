from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.cuenta import Cuenta
from app.models.deuda_prestamo import DeudaPrestamo, PagoDeudaPrestamo
from app.models.transaccion import Transaccion
from app.repositories.transaccion_repo import TransaccionRepo


class DeudaPrestamoRepo:
    def __init__(self, db: Session):
        self.db = db

    def listar(
        self,
        usuario_id: int,
        *,
        tipo: Optional[str] = None,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        vencen_hasta: Optional[date] = None,
        search: Optional[str] = None,
    ) -> list[DeudaPrestamo]:
        q = select(DeudaPrestamo).where(
            DeudaPrestamo.usuario_id == usuario_id,
            DeudaPrestamo.deleted_at.is_(None),
        )
        if tipo:
            q = q.where(DeudaPrestamo.tipo == tipo)
        if estado:
            q = q.where(DeudaPrestamo.estado == estado)
        if prioridad:
            q = q.where(DeudaPrestamo.prioridad == prioridad)
        if vencen_hasta:
            q = q.where(DeudaPrestamo.fecha_proxima <= vencen_hasta)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(
                or_(
                    DeudaPrestamo.nombre.ilike(pattern),
                    DeudaPrestamo.contraparte.ilike(pattern),
                    DeudaPrestamo.descripcion.ilike(pattern),
                )
            )
        q = q.order_by(
            DeudaPrestamo.estado,
            DeudaPrestamo.fecha_proxima.asc().nullslast(),
            DeudaPrestamo.prioridad.desc(),
            DeudaPrestamo.id.desc(),
        )
        items = self.db.execute(q).scalars().all()
        for item in items:
            item.total_pagado = Decimal(str(item.monto_original)) - Decimal(str(item.saldo_pendiente))
        return items

    def obtener(self, deuda_id: int, usuario_id: int) -> Optional[DeudaPrestamo]:
        deuda = self.db.execute(
            select(DeudaPrestamo).where(
                DeudaPrestamo.id == deuda_id,
                DeudaPrestamo.usuario_id == usuario_id,
                DeudaPrestamo.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if deuda:
            deuda.total_pagado = Decimal(str(deuda.monto_original)) - Decimal(str(deuda.saldo_pendiente))
        return deuda

    def crear(self, usuario_id: int, data: dict) -> DeudaPrestamo:
        self._validar_cuenta(usuario_id, data.get("cuenta_id"), required=False)
        self._validar_categoria(usuario_id, data.get("categoria_id"))
        deuda = DeudaPrestamo(
            usuario_id=usuario_id,
            saldo_pendiente=data["monto_original"],
            estado="activa",
            **data,
        )
        self.db.add(deuda)
        self.db.flush()
        return deuda

    def actualizar(self, deuda: DeudaPrestamo, data: dict) -> DeudaPrestamo:
        if "cuenta_id" in data:
            self._validar_cuenta(deuda.usuario_id, data.get("cuenta_id"), required=False)
        if "categoria_id" in data:
            self._validar_categoria(deuda.usuario_id, data.get("categoria_id"))
        for key, value in data.items():
            setattr(deuda, key, value)
        self.db.add(deuda)
        self.db.flush()
        return deuda

    def soft_delete(self, deuda: DeudaPrestamo) -> None:
        deuda.deleted_at = datetime.now(timezone.utc)
        self.db.add(deuda)
        self.db.flush()

    def resumen(self, usuario_id: int) -> dict:
        rows = self.db.execute(
            select(
                DeudaPrestamo.tipo,
                func.coalesce(func.sum(DeudaPrestamo.saldo_pendiente), 0),
                func.count(DeudaPrestamo.id),
            )
            .where(
                DeudaPrestamo.usuario_id == usuario_id,
                DeudaPrestamo.deleted_at.is_(None),
                DeudaPrestamo.estado == "activa",
            )
            .group_by(DeudaPrestamo.tipo)
        ).all()
        total_debo = Decimal("0")
        total_me_deben = Decimal("0")
        cantidad_activas = 0
        for tipo, total, count in rows:
            cantidad_activas += count
            if tipo == "debo":
                total_debo = Decimal(str(total or 0))
            elif tipo == "me_deben":
                total_me_deben = Decimal(str(total or 0))

        cantidad_criticas = self.db.execute(
            select(func.count(DeudaPrestamo.id)).where(
                DeudaPrestamo.usuario_id == usuario_id,
                DeudaPrestamo.deleted_at.is_(None),
                DeudaPrestamo.estado == "activa",
                DeudaPrestamo.prioridad == "critica",
            )
        ).scalar_one()

        proximas = self.db.execute(
            select(DeudaPrestamo)
            .where(
                DeudaPrestamo.usuario_id == usuario_id,
                DeudaPrestamo.deleted_at.is_(None),
                DeudaPrestamo.estado == "activa",
                DeudaPrestamo.fecha_proxima.is_not(None),
            )
            .order_by(DeudaPrestamo.fecha_proxima.asc(), DeudaPrestamo.id.desc())
            .limit(5)
        ).scalars().all()

        return {
            "total_debo": total_debo,
            "total_me_deben": total_me_deben,
            "balance_neto": total_me_deben - total_debo,
            "cantidad_activas": cantidad_activas,
            "cantidad_criticas": cantidad_criticas or 0,
            "proximas": proximas,
        }

    def listar_pagos(self, deuda_id: int, usuario_id: int) -> list[PagoDeudaPrestamo]:
        return self.db.execute(
            select(PagoDeudaPrestamo)
            .where(
                PagoDeudaPrestamo.deuda_prestamo_id == deuda_id,
                PagoDeudaPrestamo.usuario_id == usuario_id,
            )
            .order_by(PagoDeudaPrestamo.fecha_pago.desc(), PagoDeudaPrestamo.id.desc())
        ).scalars().all()

    def registrar_pago(self, deuda: DeudaPrestamo, data: dict) -> PagoDeudaPrestamo:
        if deuda.estado != "activa":
            raise ValueError("Solo se pueden registrar pagos/cobros en registros activos")

        cuenta = self._validar_cuenta(deuda.usuario_id, data["cuenta_id"], required=True)
        monto = Decimal(str(data["monto"]))
        saldo = Decimal(str(deuda.saldo_pendiente))
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        if monto > saldo:
            raise ValueError("El monto no puede ser mayor al saldo pendiente")

        tipo_tx = "gasto" if deuda.tipo == "debo" else "ingreso"
        descripcion = (
            f"Pago deuda: {deuda.nombre}"
            if deuda.tipo == "debo"
            else f"Cobro prestamo: {deuda.nombre}"
        )

        tx = TransaccionRepo(self.db).create(
            usuario_id=deuda.usuario_id,
            cuenta_id=cuenta.id,
            tipo=tipo_tx,
            monto=monto,
            moneda=data.get("moneda") or deuda.moneda,
            fecha=data["fecha_pago"],
            categoria_id=deuda.categoria_id,
            descripcion=descripcion,
            pagado_a=deuda.contraparte,
            notas=data.get("notas"),
            es_recurrente=False,
        )

        pago = PagoDeudaPrestamo(
            deuda_prestamo_id=deuda.id,
            usuario_id=deuda.usuario_id,
            transaccion_id=tx.id,
            cuenta_id=cuenta.id,
            monto=monto,
            moneda=data.get("moneda") or deuda.moneda,
            fecha_pago=data["fecha_pago"],
            notas=data.get("notas"),
        )
        deuda.saldo_pendiente = saldo - monto
        if Decimal(str(deuda.saldo_pendiente)) <= 0:
            deuda.saldo_pendiente = Decimal("0")
            deuda.estado = "pagada"
        self.db.add(deuda)
        self.db.add(pago)
        self.db.flush()
        return pago

    def eliminar_pago(self, deuda: DeudaPrestamo, pago_id: int) -> None:
        pago = self.db.execute(
            select(PagoDeudaPrestamo).where(
                PagoDeudaPrestamo.id == pago_id,
                PagoDeudaPrestamo.deuda_prestamo_id == deuda.id,
                PagoDeudaPrestamo.usuario_id == deuda.usuario_id,
            )
        ).scalar_one_or_none()
        if not pago:
            raise ValueError("Pago/cobro no encontrado")

        tx = self.db.execute(
            select(Transaccion).where(
                Transaccion.id == pago.transaccion_id,
                Transaccion.usuario_id == deuda.usuario_id,
                Transaccion.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if not tx:
            raise ValueError("Transaccion vinculada no encontrada o ya eliminada")

        TransaccionRepo(self.db).soft_delete(tx)
        deuda.saldo_pendiente = Decimal(str(deuda.saldo_pendiente)) + Decimal(str(pago.monto))
        if deuda.estado == "pagada" and deuda.saldo_pendiente > 0:
            deuda.estado = "activa"
        self.db.add(deuda)
        self.db.delete(pago)
        self.db.flush()

    def _validar_cuenta(self, usuario_id: int, cuenta_id: Optional[int], *, required: bool) -> Optional[Cuenta]:
        if cuenta_id is None:
            if required:
                raise ValueError("cuenta_id es requerido")
            return None
        cuenta = self.db.execute(
            select(Cuenta).where(
                Cuenta.id == cuenta_id,
                Cuenta.usuario_id == usuario_id,
                Cuenta.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if not cuenta:
            raise ValueError("Cuenta no valida")
        return cuenta

    def _validar_categoria(self, usuario_id: int, categoria_id: Optional[int]) -> Optional[Categoria]:
        if categoria_id is None:
            return None
        categoria = self.db.execute(
            select(Categoria).where(
                Categoria.id == categoria_id,
                Categoria.deleted_at.is_(None),
                or_(Categoria.usuario_id == usuario_id, Categoria.usuario_id.is_(None)),
            )
        ).scalar_one_or_none()
        if not categoria:
            raise ValueError("Categoria no valida")
        return categoria
