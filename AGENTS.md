# AGENTS.md - CronoFinanzas Backend

Trabaja siempre tomando `backend/` como raiz.

## Comandos

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest
alembic current
alembic upgrade head
```

## Reglas

- No incluir secretos, tokens, claves service_role, contrasenas ni `.env`.
- No modificar migraciones ya aplicadas sin justificarlo.
- Documentar todo cambio de endpoint en README o documentacion de integracion.
- Mantener `alembic.ini` y `alembic/` relativos a `backend/`.
- No cambiar reglas financieras para tareas de infraestructura/documentacion.
- Validar imports con `python -c "from app.main import app"` cuando sea posible.

## Convenciones

- Rutas FastAPI en `app/api/routes/`.
- Modelos SQLAlchemy en `app/models/`.
- Schemas Pydantic en `app/schemas/`.
- Repositorios en `app/repositories/`.
- Configuracion en `app/core/config.py`.
