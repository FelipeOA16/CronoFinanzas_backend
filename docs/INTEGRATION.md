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


## Gobierno de CronoFinanzas V1

El contrato de alcance y el progreso oficial de la V1 se mantienen únicamente en el repositorio coordinador:

- [Plan maestro de ejecución V1](https://github.com/FelipeOA16/CronoFinanzas_Frontend/blob/main/docs/v1/MASTER_EXECUTION_PLAN.md)
- [Contrato de alcance y salida V1 v0.2](https://github.com/FelipeOA16/CronoFinanzas_Frontend/blob/main/docs/v1/CONTRACT_SCOPE_RELEASE_V1_v0.2.md)

No crear una copia del plan en este repositorio. Los bloques del backend deben registrar su estado y evidencia en el documento canónico mediante el proceso de revisión correspondiente.
