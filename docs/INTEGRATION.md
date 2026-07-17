# Integracion Backend - Frontend

Contrato general entre CronoFinanzas Backend y Flutter.

## Base URL

El backend expone FastAPI sobre HTTP. En local:

```text
http://localhost:8000
```

En el workspace Docker local historico se publica como:

```text
http://localhost:8050
```

## Prefijo API

El prefijo configurado es:

```text
/api/v1
```

## Autenticacion

- Login devuelve access token y refresh token.
- Flutter envia `Authorization: Bearer <access_token>` en endpoints protegidos.
- El backend valida JWT con `SECRET_KEY` y `JWT_ALGORITHM`.
- El refresh se realiza mediante el endpoint de autenticacion correspondiente.

## CORS

Configurar `CORS_ORIGINS` con los origenes permitidos del frontend. Ejemplos seguros:

```text
CORS_ORIGINS=http://localhost:8051
CORS_ORIGINS=https://app.example.com
```

## Variables sensibles

Estas variables pertenecen solo al backend y no deben copiarse al frontend:

- `SECRET_KEY`
- `DB_PASSWORD`
- `RESEND_API_KEY`
- Credenciales de base de datos
- Claves privadas o administrativas de servicios externos

## Modulos principales

El frontend consume endpoints para autenticacion, usuarios, cuentas, categorias, transacciones, presupuestos, reportes, perfil, deudas/prestamos, metas, alertas y capturas rapidas.

Si cambia un endpoint, actualizar la documentacion de ambos repositorios.
