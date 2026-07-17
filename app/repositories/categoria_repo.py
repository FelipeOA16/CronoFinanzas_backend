from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria


class CategoriaRepo:
    def __init__(self, db: Session):
        self.db = db

    # ── consultas ────────────────────────────────────────────────────────────

    def list_sistema(self) -> list[Categoria]:
        """Categorías del sistema (usuario_id IS NULL)."""
        return self.db.execute(
            select(Categoria)
            .where(Categoria.usuario_id.is_(None), Categoria.deleted_at.is_(None))
            .order_by(Categoria.tipo, Categoria.nombre)
        ).scalars().all()

    def list_by_user(self, usuario_id: int) -> list[Categoria]:
        """Categorías raíz (padre_id IS NULL) del sistema + propias, con hijas cargadas."""
        todas = self.db.execute(
            select(Categoria)
            .where(
                (Categoria.usuario_id.is_(None) | (Categoria.usuario_id == usuario_id)),
                Categoria.deleted_at.is_(None),
            )
            .order_by(Categoria.tipo, Categoria.nombre)
        ).scalars().all()

        # Devolver solo raíces; las hijas quedan en .hijas (ORM relationship)
        return [c for c in todas if c.padre_id is None]

    def list_by_user_flat(self, usuario_id: int) -> list[Categoria]:
        """Lista plana de todas las categorías sin jerarquía (para pickers)."""
        return self.db.execute(
            select(Categoria)
            .where(
                (Categoria.usuario_id.is_(None) | (Categoria.usuario_id == usuario_id)),
                Categoria.deleted_at.is_(None),
            )
            .order_by(Categoria.tipo, Categoria.nombre)
        ).scalars().all()

    def get_by_id(self, categoria_id: int) -> Categoria | None:
        return self.db.execute(
            select(Categoria).where(
                Categoria.id == categoria_id,
                Categoria.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    # ── mutaciones ───────────────────────────────────────────────────────────

    def create(self, usuario_id: int, **kwargs) -> Categoria:
        cat = Categoria(usuario_id=usuario_id, **kwargs)
        self.db.add(cat)
        self.db.flush()
        return cat

    def update(self, cat: Categoria, **kwargs) -> Categoria:
        for k, v in kwargs.items():
            setattr(cat, k, v)
        self.db.flush()
        return cat

    def soft_delete(self, cat: Categoria) -> None:
        from sqlalchemy.sql import func
        cat.deleted_at = func.now()
        self.db.flush()
