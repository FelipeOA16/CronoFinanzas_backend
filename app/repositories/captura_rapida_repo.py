from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.captura_rapida import CapturaRapida
from app.models.categoria import Categoria
from app.models.cuenta import Cuenta
from app.repositories.transaccion_repo import TransaccionRepo


class CapturaRapidaRepo:
    def __init__(self, db: Session):
        self.db = db

    def listar(
        self,
        usuario_id: int,
        *,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> list[CapturaRapida]:
        query = select(CapturaRapida).where(
            CapturaRapida.usuario_id == usuario_id,
            CapturaRapida.deleted_at.is_(None),
        )
        if estado:
            query = query.where(CapturaRapida.estado == estado)
        if tipo:
            query = query.where(CapturaRapida.tipo == tipo)
        return (
            self.db.execute(
                query.order_by(
                    CapturaRapida.created_at.desc(),
                    CapturaRapida.id.desc(),
                )
            )
            .scalars()
            .all()
        )

    def obtener(
        self,
        captura_id: int,
        usuario_id: int,
        *,
        for_update: bool = False,
    ) -> Optional[CapturaRapida]:
        query = select(CapturaRapida).where(
            CapturaRapida.id == captura_id,
            CapturaRapida.usuario_id == usuario_id,
            CapturaRapida.deleted_at.is_(None),
        )
        if for_update:
            query = query.with_for_update()
        return self.db.execute(query).scalar_one_or_none()

    def crear(self, usuario_id: int, data: dict) -> CapturaRapida:
        self._validar_cuenta(usuario_id, data.get("cuenta_id"))
        self._validar_cuenta(usuario_id, data.get("cuenta_destino_id"))
        self._validar_cuentas_distintas(
            data.get("cuenta_id"),
            data.get("cuenta_destino_id"),
        )
        captura = CapturaRapida(
            usuario_id=usuario_id,
            estado="pendiente",
            **data,
        )
        self.db.add(captura)
        self.db.flush()
        return captura

    def actualizar(self, captura: CapturaRapida, data: dict) -> CapturaRapida:
        self._validar_pendiente(captura)
        if "cuenta_id" in data:
            self._validar_cuenta(captura.usuario_id, data.get("cuenta_id"))
        if "cuenta_destino_id" in data:
            self._validar_cuenta(
                captura.usuario_id,
                data.get("cuenta_destino_id"),
            )
        cuenta_id = data.get("cuenta_id", captura.cuenta_id)
        destino_id = data.get("cuenta_destino_id", captura.cuenta_destino_id)
        self._validar_cuentas_distintas(cuenta_id, destino_id)
        for key, value in data.items():
            setattr(captura, key, value)
        if captura.tipo != "transferencia":
            captura.cuenta_destino_id = None
        self.db.add(captura)
        self.db.flush()
        return captura

    def resumen(self, usuario_id: int) -> dict:
        pendientes, total = self.db.execute(
            select(
                func.count(CapturaRapida.id),
                func.coalesce(func.sum(CapturaRapida.monto), 0),
            ).where(
                CapturaRapida.usuario_id == usuario_id,
                CapturaRapida.estado == "pendiente",
                CapturaRapida.deleted_at.is_(None),
            )
        ).one()
        ultima = self.db.execute(
            select(CapturaRapida)
            .where(
                CapturaRapida.usuario_id == usuario_id,
                CapturaRapida.estado == "pendiente",
                CapturaRapida.deleted_at.is_(None),
            )
            .order_by(CapturaRapida.created_at.desc(), CapturaRapida.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        return {
            "pendientes": int(pendientes or 0),
            "total_pendiente": Decimal(str(total or 0)),
            "ultima_captura": ultima,
        }

    def completar(
        self,
        captura_id: int,
        usuario_id: int,
        data: dict,
    ) -> CapturaRapida:
        captura = self.obtener(captura_id, usuario_id, for_update=True)
        if not captura:
            raise ValueError("Captura rapida no encontrada")
        self._validar_pendiente(captura)

        cuenta_id = data.get("cuenta_id") or captura.cuenta_id
        destino_id = data.get("cuenta_destino_id") or captura.cuenta_destino_id
        cuenta = self._validar_cuenta(usuario_id, cuenta_id, required=True)
        destino = self._validar_cuenta(
            usuario_id,
            destino_id,
            required=captura.tipo == "transferencia",
        )
        if captura.tipo == "transferencia":
            self._validar_cuentas_distintas(cuenta.id, destino.id)
        else:
            destino = None

        categoria = self._validar_categoria(
            usuario_id,
            data.get("categoria_id"),
        )
        descripcion = data.get("descripcion") or captura.descripcion
        notas = data.get("notas") or captura.nota_rapida

        transaccion = TransaccionRepo(self.db).create(
            usuario_id=usuario_id,
            cuenta_id=cuenta.id,
            cuenta_destino_id=destino.id if destino else None,
            categoria_id=categoria.id if categoria else None,
            tipo=captura.tipo,
            monto=Decimal(str(captura.monto)),
            moneda=captura.moneda,
            fecha=data.get("fecha") or date.today(),
            descripcion=descripcion,
            pagado_a=data.get("pagado_a"),
            notas=notas,
            es_recurrente=False,
        )
        captura.estado = "completada"
        captura.transaccion_id = transaccion.id
        self.db.add(captura)
        self.db.flush()
        return captura

    def descartar(self, captura: CapturaRapida) -> None:
        self._validar_pendiente(captura)
        captura.estado = "descartada"
        captura.deleted_at = datetime.now(timezone.utc)
        self.db.add(captura)
        self.db.flush()

    def _validar_pendiente(self, captura: CapturaRapida) -> None:
        if captura.estado != "pendiente" or captura.transaccion_id is not None:
            raise ValueError("Solo se puede modificar una captura pendiente")

    def _validar_cuenta(
        self,
        usuario_id: int,
        cuenta_id: Optional[int],
        *,
        required: bool = False,
    ) -> Optional[Cuenta]:
        if cuenta_id is None:
            if required:
                raise ValueError("cuenta_id es requerido para completar")
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

    def _validar_categoria(
        self,
        usuario_id: int,
        categoria_id: Optional[int],
    ) -> Optional[Categoria]:
        if categoria_id is None:
            return None
        categoria = self.db.execute(
            select(Categoria).where(
                Categoria.id == categoria_id,
                Categoria.deleted_at.is_(None),
                (Categoria.usuario_id == usuario_id)
                | (Categoria.usuario_id.is_(None)),
            )
        ).scalar_one_or_none()
        if not categoria:
            raise ValueError("Categoria no valida")
        return categoria

    def _validar_cuentas_distintas(
        self,
        cuenta_id: Optional[int],
        destino_id: Optional[int],
    ) -> None:
        if cuenta_id is not None and cuenta_id == destino_id:
            raise ValueError("La cuenta origen y destino deben ser distintas")
