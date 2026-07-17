from typing import List, Optional, Any
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "app-finanzas-api"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    JWT_ALGORITHM: str = "HS256"
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_SSLMODE: str = ""  # e.g. "require" for Supabase
    CORS_ORIGINS: Optional[Any] = "*"

    # ── Email ──────────────────────────────────────────────────────────────────
    # Set EMAIL_PROVIDER=resend and RESEND_API_KEY to enable real delivery.
    # Leave EMAIL_PROVIDER=dev to log emails to console (no sending).
    EMAIL_PROVIDER: str = "dev"           # "dev" | "resend"
    RESEND_API_KEY: Optional[str] = None
    EMAIL_FROM: str = "CronoFinanzas <no-reply@cronofinanzas.com>"
    APP_FRONTEND_URL: str = "http://localhost:8051"

    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.DB_PASSWORD)
        url = f"postgresql+psycopg://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        if self.DB_SSLMODE:
            url += f"?sslmode={self.DB_SSLMODE}"
        return url

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
