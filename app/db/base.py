from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ensure models are imported so metadata is populated
try:
    from app.models import user  # noqa: F401
    from app.models import credential  # noqa: F401
    from app.models import auth_provider  # noqa: F401
    from app.models import session  # noqa: F401
    from app.models import role  # noqa: F401
    from app.models import cuenta  # noqa: F401
    from app.models import categoria  # noqa: F401
    from app.models import transaccion  # noqa: F401
    from app.models import presupuesto  # noqa: F401
    from app.models import deuda_prestamo  # noqa: F401
    from app.models import meta_financiera  # noqa: F401
    from app.models import captura_rapida  # noqa: F401
except Exception:
    pass
