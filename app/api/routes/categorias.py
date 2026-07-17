from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import Usuario
from app.repositories.categoria_repo import CategoriaRepo
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter()


@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(
    flat: bool = False,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Devuelve las categorías del sistema + las propias del usuario.
    Por defecto devuelve árbol (solo raíces con campo 'hijas').
    Con ?flat=true devuelve lista plana (usado por el picker de transacciones)."""
    repo = CategoriaRepo(db)
    if flat:
        return repo.list_by_user_flat(current_user.id)
    return repo.list_by_user(current_user.id)


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: CategoriaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CategoriaRepo(db)
    cat = repo.create(current_user.id, **data.model_dump())
    db.commit()
    db.refresh(cat)
    return cat


@router.patch("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CategoriaRepo(db)
    cat = repo.get_by_id(categoria_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if cat.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    cat = repo.update(cat, **updates)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = CategoriaRepo(db)
    cat = repo.get_by_id(categoria_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if cat.usuario_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    repo.soft_delete(cat)
    db.commit()
