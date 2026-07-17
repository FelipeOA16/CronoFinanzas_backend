# CronoFinanzas Backend

Backend FastAPI de CronoFinanzas. Esta carpeta esta preparada para funcionar como repositorio independiente tomando `backend/` como raiz del proyecto.

## Requisitos

- Python 3.12 recomendado.
- PostgreSQL accesible localmente o mediante proveedor gestionado.
- `pip`.
- Docker opcional.

## Entorno virtual

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

## Instalacion

```bash
pip install -r requirements.txt
```

## Configuracion

1. Copia `.env.example` como `.env`.
2. Completa los valores reales solo en `.env`.
3. No agregues `.env` al repositorio.

Variables usadas por el backend:

- `APP_NAME`
- `API_PREFIX`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `JWT_ALGORITHM`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_SSLMODE`
- `CORS_ORIGINS`
- `EMAIL_PROVIDER`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `APP_FRONTEND_URL`

`DATABASE_URL` se construye internamente desde las variables `DB_*`.

## Ejecucion local

Desde `backend/`:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger queda disponible en:

```text
http://localhost:8000/docs
```

## Pruebas

Si existen tests en el checkout:

```bash
pytest
```

Validacion basica de import:

```bash
python -c "from app.main import app; print(app.title)"
```

## Alembic

`alembic.ini` vive en la raiz de `backend/` y usa `script_location = alembic`.

Comandos:

```bash
alembic current
alembic upgrade head
alembic revision --autogenerate -m "descripcion"
```

No edites migraciones ya aplicadas sin una justificacion clara. Crea una nueva migracion para cambios de esquema.

## Docker

Construir desde `backend/`:

```bash
docker build -t cronofinanzas-backend .
```

Ejecutar con variables externas:

```bash
docker run --env-file .env -p 8000:8000 cronofinanzas-backend
```

El `Dockerfile` ejecuta:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Estructura

```text
app/
  api/routes/       Rutas FastAPI
  core/             Configuracion y seguridad
  db/               Sesion SQLAlchemy y metadata
  models/           Modelos SQLAlchemy
  repositories/     Acceso a datos y reglas de persistencia
  schemas/          Pydantic schemas
  services/         Servicios externos o dominio transversal
alembic/            Migraciones
scripts/            Utilidades de desarrollo
dev/                Apoyo local/desarrollo
```

## Comunicacion con frontend

El frontend consume la API por HTTP usando el prefijo `/api/v1`. La URL publica o local del backend se configura en Flutter con `API_BASE_URL`.

Configura `CORS_ORIGINS` con los origenes del frontend. En desarrollo local con Docker suele ser:

```text
CORS_ORIGINS=http://localhost:8051
```

Ver tambien `docs/INTEGRATION.md`.
