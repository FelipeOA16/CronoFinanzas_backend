from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.token import TokenResponse
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepo

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    svc = AuthService(UserRepo(db))
    try:
        user = svc.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    svc = AuthService(UserRepo(db))
    token = svc.login(data)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token


@router.get("/me", response_model=UserOut)
def me(user: object = Depends(get_current_user)):
    return user
