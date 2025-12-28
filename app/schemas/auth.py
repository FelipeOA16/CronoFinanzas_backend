from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str | None = None
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    identifier: str
    password: str
