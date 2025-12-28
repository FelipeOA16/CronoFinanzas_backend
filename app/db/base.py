from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ensure models are imported so metadata is populated
try:
    from app.models import user  # noqa: F401
except Exception:
    pass
