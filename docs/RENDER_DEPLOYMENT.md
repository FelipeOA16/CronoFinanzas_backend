# CronoFinanzas Backend - Render Deployment

Esta guia prepara el backend FastAPI de CronoFinanzas para ejecutarse como Web Service en Render usando Docker. La base PostgreSQL continua en Supabase.

No incluye despliegue automatico, GitHub Actions ni bases de datos de Render.

## Arquitectura

- Render Web Service ejecuta el contenedor Docker del backend.
- FastAPI expone la API HTTP.
- Uvicorn escucha en `0.0.0.0` y usa la variable `PORT` entregada por Render.
- Supabase aloja PostgreSQL.
- Alembic se usa para migraciones, pero no se ejecuta automaticamente al iniciar el contenedor.

Flujo:

```text
Frontend -> Render Web Service -> FastAPI -> SQLAlchemy -> Supabase PostgreSQL
```

## Plan gratuito de Render

El plan gratuito puede suspender el servicio despues de inactividad. El primer request tras una pausa puede tardar mas por cold start.

Recomendaciones:

- Mantener `/health` como health check liviano.
- Evitar tareas largas en startup.
- No ejecutar migraciones en el comando de arranque.
- Mantener un solo worker inicialmente.

## Docker

El Dockerfile:

- Usa `python:3.12-slim`.
- Instala `requirements.txt`.
- No instala `requirements-dev.txt`.
- Copia el codigo de la app.
- Expone `10000` como puerto local de respaldo.
- Arranca con:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
```

El comando usa `sh -c` para que `${PORT:-10000}` se expanda correctamente en runtime.

## Construccion local

Desde la raiz del repositorio independiente `CronoFinanzas_backend`:

```bash
docker build -t cronofinanzas-api:render-test .
```

## Ejecucion local sin .env real

Usar valores ficticios para pruebas de arranque y health check:

```powershell
docker run --rm -p 10000:10000 `
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

Reemplazar `<PUERTO-FRONTEND>` por el puerto local real donde este corriendo el frontend. No usar `.env` real para validar la imagen de Render.

## Puerto

Render define `PORT` automaticamente. El contenedor debe escuchar en ese valor.

Fallback local:

```text
PORT=10000
```

## Health check

Endpoint recomendado para Render:

```http
GET /health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "cronofinanzas-api"
}
```

Tambien existe:

```http
GET /api/v1/health
```

El endpoint no consulta PostgreSQL y no expone secretos, versiones internas ni cadenas de conexion.

## Variables normales

Variables no sensibles o de configuracion operativa:

- `APP_NAME`
- `API_PREFIX`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `JWT_ALGORITHM`
- `DB_NAME`
- `DB_USER`
- `DB_HOST`
- `DB_PORT`
- `DB_SSLMODE`
- `CORS_ORIGINS`
- `EMAIL_PROVIDER`
- `EMAIL_FROM`
- `APP_FRONTEND_URL`

## Variables sensibles

Configurar como secrets/environment variables privadas en Render:

- `SECRET_KEY`
- `DB_PASSWORD`
- `RESEND_API_KEY`, solo si `EMAIL_PROVIDER=resend`

No colocar valores reales en el repositorio.

## Configuracion futura en Render

Crear un Web Service:

- Runtime: Docker.
- Repository: `CronoFinanzas_backend`.
- Language: Docker.
- Branch: `main`.
- Root Directory: dejar vacio.
- Dockerfile Path: `./Dockerfile`.
- Docker Build Context: `.`.
- Health Check Path: `/health`.
- Instance Type: Free.
- Region: la mas cercana a Supabase y usuarios.
- Plan: Free para pruebas.

Variables minimas:

```text
SECRET_KEY=<valor-seguro>
DB_HOST=<host-de-supabase>
DB_PORT=5432
DB_NAME=<nombre-db>
DB_USER=<usuario-db>
DB_PASSWORD=<password-db>
DB_SSLMODE=require
CORS_ORIGINS=<origen-frontend>
APP_FRONTEND_URL=<url-frontend>
EMAIL_PROVIDER=dev
EMAIL_FROM=<remitente>
```

No usar `CORS_ORIGINS=*` en produccion. Usar uno o varios origenes separados por coma.

## Supabase y SQLAlchemy

La URL se arma desde:

- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_SSLMODE`

Si `DB_SSLMODE` tiene valor, se agrega como query string, por ejemplo:

```text
?sslmode=require
```

Estado actual de pool:

- `pool_pre_ping`: no configurado explicitamente.
- `pool_size`: valor default de SQLAlchemy.
- `max_overflow`: valor default de SQLAlchemy.
- `pool_recycle`: no configurado explicitamente.

El engine se crea al importar `app.db.session`, pero SQLAlchemy no abre conexion real hasta que una sesion o consulta necesita conectarse. Por eso FastAPI puede iniciar y responder `/health` sin conectar obligatoriamente a PostgreSQL.

## Migraciones Alembic

No ejecutar migraciones automaticamente en el `CMD` del contenedor.

Estrategia recomendada:

1. Revisar migraciones localmente.
2. Hacer backup o snapshot en Supabase antes de cambios sensibles.
3. Ejecutar migraciones manualmente desde un entorno controlado.
4. Desplegar el servicio despues de confirmar que la base esta en la revision esperada.

Comandos de inspeccion seguros:

```bash
python -m alembic heads
python -m alembic current
```

No ejecutar `alembic upgrade head` contra produccion sin una ventana de cambio controlada.

## Rollback

Opciones:

- Volver a desplegar una version anterior del servicio en Render.
- Revertir el commit que cambio configuracion de despliegue.
- Si una migracion fue aplicada, preparar una migracion de reversa o restaurar snapshot de Supabase segun criticidad.

No confiar en rollback de contenedor para revertir cambios ya aplicados en base de datos.

## Recomendaciones de seguridad

- Generar `SECRET_KEY` largo y aleatorio para Render.
- No usar secrets en Docker build args.
- No copiar `.env` dentro de la imagen.
- No imprimir tokens ni cadenas de conexion.
- Configurar `CORS_ORIGINS` con dominios concretos.
- Usar `DB_SSLMODE=require` con Supabase.
- Mantener `/health` sin datos internos.
- Revisar logs despues del primer despliegue.
