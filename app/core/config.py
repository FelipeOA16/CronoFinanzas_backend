from typing import List, Optional, Any
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "app-finanzas-api"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"
    DB_NAME: str = "appfinanzas"
    DB_USER: str = "dbpostgresfinanzas"
    DB_PASSWORD: str
    DB_HOST: str = "ec2-3-80-233-186.compute-1.amazonaws.com"
    DB_PORT: int = 5433
    CORS_ORIGINS: Optional[Any] = "*"

    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql+psycopg2://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @field_validator("CORS_ORIGINS", mode="before")
    def _split_origins(cls, v):
        if v is None:
            return []
        if isinstance(v, str) and v != "*":
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
