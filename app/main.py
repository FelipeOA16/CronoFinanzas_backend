from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.core.cors import get_cors_origins
from app.api.routes import health, auth, users, cuentas, categorias, transacciones, presupuestos, reportes, notificaciones, deudas_prestamos, metas, capturas_rapidas

settings = Settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(settings.CORS_ORIGINS),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=f"{settings.API_PREFIX}")
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])
app.include_router(cuentas.router, prefix=f"{settings.API_PREFIX}/cuentas", tags=["cuentas"])
app.include_router(categorias.router, prefix=f"{settings.API_PREFIX}/categorias", tags=["categorias"])
app.include_router(transacciones.router, prefix=f"{settings.API_PREFIX}/transacciones", tags=["transacciones"])
app.include_router(presupuestos.router, prefix=f"{settings.API_PREFIX}/presupuestos", tags=["presupuestos"])
app.include_router(reportes.router, prefix=f"{settings.API_PREFIX}/reportes", tags=["reportes"])
app.include_router(notificaciones.router, prefix=f"{settings.API_PREFIX}/notificaciones", tags=["notificaciones"])
app.include_router(deudas_prestamos.router, prefix=f"{settings.API_PREFIX}/deudas-prestamos", tags=["deudas-prestamos"])
app.include_router(metas.router, prefix=f"{settings.API_PREFIX}/metas", tags=["metas"])
app.include_router(
    capturas_rapidas.router,
    prefix=f"{settings.API_PREFIX}/capturas-rapidas",
    tags=["capturas-rapidas"],
)


@app.get("/health", include_in_schema=False)
def health_check():
    return health.health()


@app.get("/", include_in_schema=False)
def root():
    return {"app": settings.APP_NAME}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="API",
        routes=app.routes,
    )
    # ensure HTTP Bearer security scheme appears with bearerFormat=JWT
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes.setdefault(
        "HTTPBearer",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
