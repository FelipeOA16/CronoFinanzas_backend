# Render Readiness Report - CronoFinanzas Backend

Fecha: 2026-07-17

Alcance: preparar y validar el backend FastAPI para Render Free usando Docker, sin desplegar.

Repositorio objetivo: `CronoFinanzas_backend`, repositorio independiente del backend.

Configuracion esperada en Render:

- Root Directory: vacio.
- Dockerfile Path: `./Dockerfile`.
- Docker Build Context: `.`.

## Estado inicial

- Rama actual: `main`.
- Working tree inicial: limpio.
- Dockerfile inicial ejecutaba `alembic upgrade head` antes de iniciar Uvicorn.
- Dockerfile inicial fijaba puerto `8000`.
- `.dockerignore` inicial excluia `*.md` y no cubria todas las entradas solicitadas.
- Health existente estaba disponible bajo el prefijo API como `/api/v1/health`, pero no como `/health`.

## Archivos inspeccionados

- `Dockerfile`
- `.dockerignore`
- `requirements.txt`
- `requirements-dev.txt`
- `app/main.py`
- `app/api/routes/health.py`
- `app/core/config.py`
- `app/core/cors.py`
- `app/db/session.py`
- `app/api/deps.py`
- `alembic/env.py`
- `tests/test_app_smoke.py`
- `tests/test_security.py`

## Archivos modificados

- `Dockerfile`
- `.dockerignore`
- `app/api/routes/health.py`
- `app/main.py`
- `tests/test_app_smoke.py`
- `docs/RENDER_DEPLOYMENT.md`
- `RENDER_READINESS_REPORT.md`

## Correcciones realizadas

- Dockerfile ahora instala solo `requirements.txt`.
- Dockerfile no instala `requirements-dev.txt`.
- Dockerfile ya no ejecuta migraciones automaticamente.
- Dockerfile arranca `app.main:app` con Uvicorn sin `--reload`.
- Dockerfile escucha en `0.0.0.0`.
- Dockerfile usa `${PORT:-10000}` con `sh -c`.
- Dockerfile mantiene un solo worker.
- `.dockerignore` excluye `.env`, `.env.*`, `.venv/`, `.git/`, caches, logs y `tests/`.
- `.dockerignore` conserva `!.env.example`.
- Se agrego `/health` raiz para Render.
- `/health` y `/api/v1/health` devuelven `status` y `service` sin consultar DB.

## Variables usadas por el codigo

- `APP_NAME`
- `API_PREFIX`
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `JWT_ALGORITHM`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_SSLMODE`
- `CORS_ORIGINS`
- `EMAIL_PROVIDER`
- `RESEND_API_KEY`
- `EMAIL_FROM`
- `APP_FRONTEND_URL`

## Seguridad de variables

- `SECRET_KEY` no tiene default en codigo; debe definirse en Render con un valor seguro.
- `APP_FRONTEND_URL` es configurable.
- `API_PREFIX` mantiene `/api/v1`, compatible con el frontend.
- `CORS_ORIGINS` acepta un string con uno o varios origenes separados por coma.
- Para produccion no se debe configurar `CORS_ORIGINS=*`.

## Conexion con Supabase

- SQLAlchemy construye la URL desde las variables `DB_*`.
- `DB_PASSWORD` se escapa con `quote_plus`.
- Si `DB_SSLMODE` existe, se agrega a la URL como `?sslmode=<valor>`.
- `pool_pre_ping`: no configurado explicitamente.
- `pool_size`: default de SQLAlchemy.
- `max_overflow`: default de SQLAlchemy.
- `pool_recycle`: no configurado explicitamente.
- El engine se crea al importar `app.db.session`, pero la conexion real se abre cuando una sesion/consulta la necesita.
- FastAPI puede iniciar y responder `/health` sin conectarse inmediatamente a PostgreSQL.

## Validaciones Python

### Pytest

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Resultado:

```text
6 passed, 4 warnings
```

Warnings:

- `PydanticDeprecatedSince20` por `class Config`.
- `DeprecationWarning` por `datetime.utcnow()`.

### Compileall

Comando:

```powershell
.\.venv\Scripts\python.exe -m compileall app
```

Resultado: OK.

### Import FastAPI

Comando:

```powershell
.\.venv\Scripts\python.exe -c "from app.main import app; print(app.title)"
```

Resultado:

```text
app-finanzas-api
```

### Alembic heads

Comando:

```powershell
.\.venv\Scripts\python.exe -m alembic heads
```

Resultado:

```text
0014_capturas_rapidas (head)
```

No se ejecuto `alembic upgrade`.

## Validacion Docker

### Build

Comando:

```powershell
docker build -t cronofinanzas-api:render-test .
```

Resultado: OK. Imagen construida como `cronofinanzas-api:render-test`.

Nota: primero Docker fallo porque Docker Desktop no estaba iniciado. Se inicio Docker Desktop y se repitio el build correctamente.

### Run local con variables ficticias

Comando usado:

```powershell
docker run --rm -d --name cronofinanzas-render-test -p 10000:10000 `
  -e PORT=10000 `
  -e SECRET_KEY=dummy-secret-only-for-local-test `
  -e DB_HOST=localhost `
  -e DB_PORT=5432 `
  -e DB_NAME=dummy `
  -e DB_USER=dummy `
  -e DB_PASSWORD=dummy `
  -e DB_SSLMODE= `
  -e CORS_ORIGINS=http://localhost:<PUERTO-FRONTEND> `
  -e EMAIL_PROVIDER=dev `
  -e EMAIL_FROM="CronoFinanzas <no-reply@example.com>" `
  -e APP_FRONTEND_URL=http://localhost:<PUERTO-FRONTEND> `
  cronofinanzas-api:render-test
```

Resultado: contenedor iniciado correctamente en `0.0.0.0:10000`.

Confirmacion: no se uso `.env` real dentro de Docker.

### Health

Comandos:

```powershell
Invoke-RestMethod -Uri http://localhost:10000/health
Invoke-RestMethod -Uri http://localhost:10000/api/v1/health
```

Resultado:

```text
status: ok
service: cronofinanzas-api
```

HTTP observado en logs:

```text
GET /health HTTP/1.1 200 OK
GET /api/v1/health HTTP/1.1 200 OK
```

El contenedor fue detenido con:

```powershell
docker stop cronofinanzas-render-test
```

Al estar creado con `--rm`, se elimino al detenerlo.

### Contenido sensible excluido de la imagen

Comando:

```powershell
docker run --rm --entrypoint sh cronofinanzas-api:render-test -c "test ! -e /app/.env && test ! -d /app/.git && test ! -d /app/.venv && test ! -d /app/tests && echo clean"
```

Resultado:

```text
clean
```

## Variables requeridas en Render

Minimas:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_SSLMODE`
- `CORS_ORIGINS`
- `APP_FRONTEND_URL`
- `EMAIL_PROVIDER`
- `EMAIL_FROM`

Opcionales segun uso:

- `APP_NAME`
- `API_PREFIX`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `JWT_ALGORITHM`
- `RESEND_API_KEY`

## Riesgos y advertencias

- `CORS_ORIGINS=*` no debe usarse en Render produccion.
- `pool_pre_ping`, `pool_size`, `max_overflow` y `pool_recycle` no estan configurados explicitamente.
- Render Free puede tener cold starts.
- Las migraciones Alembic deben ejecutarse manualmente y de forma controlada.
- `APP_NAME` conserva el valor actual `app-finanzas-api`; el health usa `cronofinanzas-api` como nombre publico del servicio.
- Quedan warnings no bloqueantes de Pydantic y `datetime.utcnow()`.

## Confirmaciones

- No se crearon ramas.
- No se cambio de rama.
- No se hizo commit.
- No se hizo push.
- No se hizo merge.
- No se modifico `.env`.
- No se mostraron secretos.
- No se ejecuto `alembic upgrade`.
- No se accedio deliberadamente a base de produccion.
- No se cambiaron reglas de negocio.
- No se agregaron servicios de pago.
- No se agregaron bases de datos de Render.
- No se agregaron GitHub Actions.
- No se uso `.env` real dentro de Docker.

## Conclusion

El backend esta listo para crear un Web Service gratuito en Render usando el Dockerfile existente, manteniendo PostgreSQL en Supabase.

Antes del despliegue real, configurar variables seguras en Render y definir `CORS_ORIGINS` con el dominio real del frontend.
