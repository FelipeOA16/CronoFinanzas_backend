from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.cuenta import Cuenta
from app.models.meta_financiera import AporteMeta, MetaFinanciera
from app.models.transaccion import Transaccion
from app.repositories.transaccion_repo import TransaccionRepo


class MetaFinancieraRepo:
    def __init__(self, db: Session):
        self.db = db

    def listar(
        self,
        usuario_id: int,
        *,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[MetaFinanciera]:
        q = select(MetaFinanciera).where(
            MetaFinanciera.usuario_id == usuario_id,
            MetaFinanciera.deleted_at.is_(None),
        )
        if estado:
            q = q.where(MetaFinanciera.estado == estado)
        if prioridad:
            q = q.where(MetaFinanciera.prioridad == prioridad)
        if search:
            pattern = f"%{search.strip()}%"
            q = q.where(
                or_(
                    MetaFinanciera.nombre.ilike(pattern),
                    MetaFinanciera.descripcion.ilike(pattern),
                    MetaFinanciera.notas.ilike(pattern),
                )
            )
        q = q.order_by(
            MetaFinanciera.estado,
            MetaFinanciera.fecha_objetivo.asc().nullslast(),
            MetaFinanciera.prioridad.desc(),
            MetaFinanciera.id.desc(),
        )
        items = self.db.execute(q).scalars().all()
        for item in items:
            self._set_calculated(item)
        return items

    def obtener(self, meta_id: int, usuario_id: int) -> Optional[MetaFinanciera]:
        meta = self.db.execute(
            select(MetaFinanciera).where(
                MetaFinanciera.id == meta_id,
                MetaFinanciera.usuario_id == usuario_id,
                MetaFinanciera.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if meta:
            self._set_calculated(meta)
        return meta

    def crear(self, usuario_id: int, data: dict) -> MetaFinanciera:
        self._validar_cuenta(usuario_id, data.get("cuenta_id"), required=False)
        self._validar_categoria(usuario_id, data.get("categoria_id"))
        monto_objetivo = Decimal(str(data["monto_objetivo"]))
        monto_actual = Decimal(str(data.pop("monto_actual", 0) or 0))
        if monto_actual > monto_objetivo:
            raise ValueError("monto_actual no puede superar el monto_objetivo")
        estado = "completada" if monto_actual >= monto_objetivo else "activa"
        meta = MetaFinanciera(
            usuario_id=usuario_id,
            monto_actual=monto_actual,
            estado=estado,
            **data,
        )
        self.db.add(meta)
        self.db.flush()
        self._set_calculated(meta)
        return meta

    def actualizar(self, meta: MetaFinanciera, data: dict) -> MetaFinanciera:
        if "cuenta_id" in data:
            self._validar_cuenta(meta.usuario_id, data.get("cuenta_id"), required=False)
        if "categoria_id" in data:
            self._validar_categoria(meta.usuario_id, data.get("categoria_id"))
        if "monto_objetivo" in data:
            objetivo = Decimal(str(data["monto_objetivo"]))
            if objetivo < Decimal(str(meta.monto_actual)):
                raise ValueError("monto_objetivo no puede ser menor al monto_actual")
        for key, value in data.items():
            setattr(meta, key, value)
        if Decimal(str(meta.monto_actual)) >= Decimal(str(meta.monto_objetivo)):
            meta.estado = "completada"
        elif meta.estado == "completada":
            meta.estado = "activa"
        self.db.add(meta)
        self.db.flush()
        self._set_calculated(meta)
        return meta

    def soft_delete(self, meta: MetaFinanciera) -> None:
        meta.deleted_at = datetime.now(timezone.utc)
        self.db.add(meta)
        self.db.flush()

    def resumen(self, usuario_id: int) -> dict:
        rows = self.db.execute(
            select(
                func.coalesce(func.sum(MetaFinanciera.monto_objetivo), 0),
                func.coalesce(func.sum(MetaFinanciera.monto_actual), 0),
                func.count(MetaFinanciera.id),
            ).where(
                MetaFinanciera.usuario_id == usuario_id,
                MetaFinanciera.deleted_at.is_(None),
                MetaFinanciera.estado == "activa",
            )
        ).one()
        total_objetivo = Decimal(str(rows[0] or 0))
        total_actual = Decimal(str(rows[1] or 0))
        cantidad_activas = rows[2] or 0
        completadas = self.db.execute(
            select(func.count(MetaFinanciera.id)).where(
                MetaFinanciera.usuario_id == usuario_id,
                MetaFinanciera.deleted_at.is_(None),
                MetaFinanciera.estado == "completada",
            )
        ).scalar_one()

        top = self.db.execute(
            select(MetaFinanciera)
            .where(
                MetaFinanciera.usuario_id == usuario_id,
                MetaFinanciera.deleted_at.is_(None),
                MetaFinanciera.estado == "activa",
            )
            .order_by(
                MetaFinanciera.prioridad.desc(),
                MetaFinanciera.fecha_objetivo.asc().nullslast(),
                MetaFinanciera.id.desc(),
            )
            .limit(2)
        ).scalars().all()

        top_items = []
        for item in top:
            self._set_calculated(item)
            top_items.append(
                {
                    "id": item.id,
                    "nombre": item.nombre,
                    "monto_objetivo": item.monto_objetivo,
                    "monto_actual": item.monto_actual,
                    "porcentaje": item.porcentaje,
                    "prioridad": item.prioridad,
                    "fecha_objetivo": item.fecha_objetivo,
                }
            )

        return {
            "total_objetivo": total_objetivo,
            "total_actual": total_actual,
            "porcentaje_global": self._porcentaje(total_actual, total_objetivo),
            "cantidad_activas": cantidad_activas,
            "cantidad_completadas": completadas or 0,
            "top_metas": top_items,
        }

    def listar_aportes(self, meta_id: int, usuario_id: int) -> list[AporteMeta]:
        return self.db.execute(
            select(AporteMeta)
            .where(
                AporteMeta.meta_id == meta_id,
                AporteMeta.usuario_id == usuario_id,
            )
            .order_by(AporteMeta.fecha_aporte.desc(), AporteMeta.id.desc())
        ).scalars().all()

    def registrar_aporte(self, meta: MetaFinanciera, data: dict) -> AporteMeta:
        if meta.estado not in {"activa", "pausada"}:
            raise ValueError("Solo se pueden registrar aportes en metas activas o pausadas")

        cuenta = self._validar_cuenta(meta.usuario_id, data["cuenta_id"], required=True)
        monto = Decimal(str(data["monto"]))
        objetivo = Decimal(str(meta.monto_objetivo))
        actual = Decimal(str(meta.monto_actual))
        faltante = objetivo - actual
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        if monto > faltante:
            raise ValueError("El monto no puede superar el faltante de la meta")

        tx = TransaccionRepo(self.db).create(
            usuario_id=meta.usuario_id,
            cuenta_id=cuenta.id,
            tipo="gasto",
            monto=monto,
            moneda=data.get("moneda") or meta.moneda,
            fecha=data["fecha_aporte"],
            categoria_id=meta.categoria_id,
            descripcion=f"Aporte a meta: {meta.nombre}",
            pagado_a=meta.nombre,
            notas=data.get("notas"),
            es_recurrente=False,
        )

        aporte = AporteMeta(
            meta_id=meta.id,
            usuario_id=meta.usuario_id,
            transaccion_id=tx.id,
            cuenta_id=cuenta.id,
            monto=monto,
            moneda=data.get("moneda") or meta.moneda,
            fecha_aporte=data["fecha_aporte"],
            notas=data.get("notas"),
        )
        meta.monto_actual = actual + monto
        if Decimal(str(meta.monto_actual)) >= objetivo:
            meta.monto_actual = objetivo
            meta.estado = "completada"
        elif meta.estado == "pausada":
            meta.estado = "activa"
        self.db.add(meta)
        self.db.add(aporte)
        self.db.flush()
        return aporte

    def eliminar_aporte(self, meta: MetaFinanciera, aporte_id: int) -> None:
        aporte = self.db.execute(
            select(AporteMeta).where(
                AporteMeta.id == aporte_id,
                AporteMeta.meta_id == meta.id,
                AporteMeta.usuario_id == meta.usuario_id,
            )
        ).scalar_one_or_none()
        if not aporte:
            raise ValueError("Aporte no encontrado")

        tx = self.db.execute(
            select(Transaccion).where(
                Transaccion.id == aporte.transaccion_id,
                Transaccion.usuario_id == meta.usuario_id,
                Transaccion.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if not tx:
            raise ValueError("Transaccion vinculada no encontrada o ya eliminada")

        TransaccionRepo(self.db).soft_delete(tx)
        meta.monto_actual = Decimal(str(meta.monto_actual)) - Decimal(str(aporte.monto))
        if meta.monto_actual < 0:
            meta.monto_actual = Decimal("0")
        if meta.estado == "completada" and meta.monto_actual < Decimal(str(meta.monto_objetivo)):
            meta.estado = "activa"
        self.db.add(meta)
        self.db.delete(aporte)
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

    def _set_calculated(self, meta: MetaFinanciera) -> None:
        objetivo = Decimal(str(meta.monto_objetivo))
        actual = Decimal(str(meta.monto_actual))
        meta.porcentaje = self._porcentaje(actual, objetivo)
        meta.faltante = max(objetivo - actual, Decimal("0"))

    def _porcentaje(self, actual: Decimal, objetivo: Decimal) -> Decimal:
        if objetivo <= 0:
            return Decimal("0")
        return (actual / objetivo * Decimal("100")).quantize(Decimal("0.01"))
