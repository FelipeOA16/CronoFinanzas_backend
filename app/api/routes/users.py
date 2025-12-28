from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.repositories.user_repo import UserRepo
from app.schemas.user import UserOut, UpdateRoleRequest

router = APIRouter()


@router.get("/", response_model=List[UserOut], dependencies=[Depends(require_roles(["ADMIN"]))])
def list_users(db: Session = Depends(get_db)):
    return UserRepo(db).list_users()


@router.patch("/{user_id}/role", dependencies=[Depends(require_roles(["ADMIN"]))], response_model=UserOut)
def change_role(user_id: UUID, payload: UpdateRoleRequest, db: Session = Depends(get_db)):
    repo = UserRepo(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return repo.update_role(user, payload.role)
