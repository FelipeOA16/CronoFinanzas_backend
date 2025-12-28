from typing import Optional

from app.repositories.user_repo import UserRepo
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.token import TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import RoleEnum


class AuthService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    def register(self, data: RegisterRequest):
        if self.repo.get_by_email(data.email):
            raise ValueError("Email already registered")
        if data.username and self.repo.get_by_username(data.username):
            raise ValueError("Username already registered")
        password_hash = hash_password(data.password)
        return self.repo.create_user(email=data.email, username=data.username, password_hash=password_hash, role=RoleEnum.USER)

    def login(self, data: LoginRequest) -> Optional[TokenResponse]:
        user = self.repo.get_by_email(data.identifier) or self.repo.get_by_username(data.identifier)
        if not user:
            return None
        if not verify_password(data.password, user.password_hash):
            return None
        token = create_access_token(subject=str(user.id), role=user.role.value)
        return TokenResponse(access_token=token)
