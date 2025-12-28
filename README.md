# app-finanzas-api

Stack: FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Pydantic v2, python-jose, passlib.

Pasos:

1) Crear y activar virtualenv
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias
```powershell
pip install -r requirements.txt
```

3) Configurar `.env` usando `.env.example` (NO comitear `.env`).

4) Ejecutar migraciones
```powershell
alembic revision --autogenerate -m "create users"
alembic upgrade head
```

5) Levantar servidor
```powershell
cd app-finanzas-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ejemplos curl:

- Register
```sh
curl -X POST http://localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{"email":"a@b.com","password":"secret"}'
```
- Login
```sh
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"identifier":"a@b.com","password":"secret"}'
```
- Me
```sh
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/auth/me
```

Notas: No commitear `.env`. Ajusta `alembic.ini` si es necesario.
