# AUTH INTEGRATION PACK
## API de Autenticación - Guía Completa para Frontend

**Versión**: 1.0.0
**Última actualización**: Enero 2026
**Backend**: FastAPI + PostgreSQL
**Autenticación**: JWT (Bearer Token)

---

## A) API CONTRACT

### Base URL

| Entorno | URL |
|---------|-----|
| **Desarrollo** | `http://127.0.0.1:8000` |
| **Producción** | `https://tu-dominio.com` (a configurar) |

**API Prefix**: `/api/v1`

---

### 1. LOGIN

#### Endpoint
```
POST /api/v1/auth/login
```

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "identifier": "user1",
  "password": "Password123!"
}
```

**Notas de validación**:
- `identifier`: string, requerido. Puede ser email o username.
- `password`: string, requerido. Mínimo 6 caracteres, máximo 72 bytes (UTF-8).

#### Response 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZGFlMDBhMi0xNDlmLTQ0OWQtYjBmYi04OTQ2YzJmOGY0YTQiLCJyb2xlIjoiVVNFUiIsImV4cCI6MTczNjk0OTE4MCwidHlwIjoiYWNjZXNzIn0.abcd...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZGFlMDBhMi0xNDlmLTQ0OWQtYjBmYi04OTQ2YzJmOGY0YTQiLCJyb2xlIjoiVVNFUiIsImV4cCI6MTczNzU0NDE4MCwidHlwIjoicmVmcmVzaCJ9.xyz...",
  "token_type": "bearer"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Invalid credentials"
}
```

#### Response 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "identifier"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### 2. REGISTER

#### Endpoint
```
POST /api/v1/auth/register
```

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "SecurePass123!"
}
```

**Notas de validación**:
- `email`: string, requerido. Debe ser email válido (RFC 5322).
- `username`: string, opcional. Si no se proporciona, se genera automáticamente.
- `password`: string, requerido. Mínimo 6 caracteres, máximo 72 bytes (UTF-8).

#### Response 201 Created
```json
{
  "id": "5dafc0aa-149f-449d-b0fb-8946c2f8f4a4",
  "email": "newuser@example.com",
  "username": "newuser",
  "role": "USER",
  "is_active": true,
  "created_at": "2026-01-16T12:34:56.789Z"
}
```

#### Response 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

o

```json
{
  "detail": "password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])"
}
```

#### Response 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

### 3. GET CURRENT USER (ME)

#### Endpoint
```
GET /api/v1/auth/me
```

#### Headers
```
Authorization: Bearer {access_token}
```

#### Request Body
(ninguno)

#### Response 200 OK
```json
{
  "id": "5dafc0aa-149f-449d-b0fb-8946c2f8f4a4",
  "email": "user@example.com",
  "username": "user1",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2025-12-01T10:20:30.123Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

**Headers de respuesta**:
```
WWW-Authenticate: Bearer
```

#### Response 400 Bad Request
```json
{
  "detail": "Inactive user"
}
```

---

### 4. REFRESH TOKEN

#### Endpoint
```
POST /api/v1/auth/refresh
```

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Notas de validación**:
- `refresh_token`: string, requerido. Debe ser un refresh token válido (no access token).

#### Response 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Nota**: Cuando se hace refresh, el servidor revoca el refresh token anterior y emite uno nuevo (token rotation).

#### Response 401 Unauthorized
```json
{
  "detail": "Invalid refresh token"
}
```

o

```json
{
  "detail": "Refresh token revoked"
}
```

#### Response 400 Bad Request
```json
{
  "detail": "Inactive user"
}
```

---

### 5. LOGOUT

#### Endpoint
```
POST /api/v1/auth/logout
```

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Notas de validación**:
- `refresh_token`: string, requerido.

#### Response 204 No Content
(sin body)

---

### 6. DUMMY (Protected Endpoint - Test)

#### Endpoint
```
GET /api/v1/auth/dummy
```

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response 200 OK
```json
{
  "ok": true,
  "user": "user@example.com"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

---

## B) OPENAPI

### Acceso a la documentación interactiva

#### Swagger UI
```
GET http://127.0.0.1:8000/docs
```

Permite probar endpoints interactivamente. Usa el botón **"Authorize"** en la parte superior derecha para pegar el token Bearer.

#### ReDoc
```
GET http://127.0.0.1:8000/redoc
```

Documentación en formato ReadOnly.

#### OpenAPI JSON
```
GET http://127.0.0.1:8000/openapi.json
```

Respuesta (ejemplo parcial):
```json
{
  "openapi": "3.0.2",
  "info": {
    "title": "app-finanzas-api",
    "version": "1.0.0"
  },
  "paths": {
    "/api/v1/auth/login": {
      "post": {
        "operationId": "login_api_v1_auth_login_post",
        "requestBody": { ... },
        "responses": { ... }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "HTTPBearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      }
    }
  }
}
```

---

## C) AUTH FLOW

### Esquema de Autenticación: JWT Bearer Token

#### 1. Flujo de Autenticación (Login)

```
Frontend                              Backend
   |                                    |
   +---> POST /api/v1/auth/login ------>|
   |     { identifier, password }       |
   |                                    | Validar credenciales
   |                                    | Generar access_token (15 min)
   |                                    | Generar refresh_token (7 días)
   |<----- 200 OK <-----+               |
   |      {                             |
   |        access_token,               |
   |        refresh_token,              |
   |        token_type: "bearer"        |
   |      }                             |
```

#### 2. Acceso a Recursos Protegidos

```
Frontend                              Backend
   |                                    |
   +---> GET /api/v1/auth/me -------->|
   |     Authorization: Bearer {token}  |
   |                                    | Decodificar JWT
   |                                    | Validar firma (SECRET_KEY)
   |                                    | Validar exp (expiración)
   |                                    | Validar typ: "access"
   |<----- 200 OK <-----+               |
   |      { user data }                 |
```

#### 3. Refresh Token (cuando access_token expira)

```
Frontend                              Backend
   |                                    |
   +---> POST /api/v1/auth/refresh --->|
   |     { refresh_token }              |
   |                                    | Decodificar refresh_token
   |                                    | Validar firma y exp
   |                                    | Verificar si está revocado
   |                                    | Revocar refresh_token anterior
   |                                    | Generar nuevo access_token
   |                                    | Generar nuevo refresh_token
   |<----- 200 OK <-----+               |
   |      {                             |
   |        access_token (nuevo),       |
   |        refresh_token (nuevo),      |
   |        token_type: "bearer"        |
   |      }                             |
```

#### 4. Logout (Revocación de Token)

```
Frontend                              Backend
   |                                    |
   +---> POST /api/v1/auth/logout ----->|
   |     { refresh_token }              |
   |                                    | Agregar refresh_token a lista de revocados
   |                                    | (en memoria en dev; persistente en prod)
   |<----- 204 No Content <-----+       |
   |                                    |
   | (Access token sigue siendo válido  |
   |  hasta que expire - 15 min)        |
```

### Detalles del Token JWT

#### Access Token (tipo: "access")
- **Expiración**: 15 minutos (configurable en `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Algoritmo**: HS256
- **Claims** (payload):
  ```json
  {
    "sub": "5dafc0aa-149f-449d-b0fb-8946c2f8f4a4",  // user_id (UUID)
    "role": "USER",                                   // "ADMIN" | "USER"
    "exp": 1736949180,                               // Unix timestamp (expiración)
    "typ": "access"                                  // Tipo de token
  }
  ```

#### Refresh Token (tipo: "refresh")
- **Expiración**: 10080 minutos = 7 días (configurable en `REFRESH_TOKEN_EXPIRE_MINUTES`)
- **Algoritmo**: HS256
- **Claims** (payload):
  ```json
  {
    "sub": "5dafc0aa-149f-449d-b0fb-8946c2f8f4a4",  // user_id (UUID)
    "role": "USER",                                   // "ADMIN" | "USER"
    "exp": 1737544180,                               // Unix timestamp (expiración)
    "typ": "refresh"                                 // Tipo de token
  }
  ```

#### Validación en Backend

El backend valida:
1. **Firma**: Token debe ser firmado con `SECRET_KEY` correcta.
2. **Expiración (`exp`)**: Token no debe estar expirado.
3. **Tipo (`typ`)**: Access token vs. refresh token.
4. **Usuario activo**: El usuario debe existir en DB y estar activo (`is_active=true`).

Si alguna validación falla → **401 Unauthorized**.

---

## D) CORS & Cookies

### Configuración CORS Actual

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| **allow_origins** | `"*"` (por defecto) o valores de `.env` (ej: `"http://localhost:3000,http://localhost:8080"`) | Orígenes permitidos para CORS |
| **allow_credentials** | `true` | Permite enviar credentials (Authorization header, cookies) |
| **allow_methods** | `["*"]` | Todos los métodos HTTP permitidos |
| **allow_headers** | `["*"]` | Todos los headers permitidos |

### Variable `.env` para CORS

En `.env` configura:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://midominio.com
```

o

```
CORS_ORIGINS=*
```

### Status de Cookies

**No se usan cookies actualmente.**

El frontend **debe almacenar tokens en**:
- **localStorage**: Para persistencia entre sesiones (menos seguro, vulnerable a XSS).
- **sessionStorage**: Para sesión actual (se limpia al cerrar navegador).
- **Memory (variable)**: Para máxima seguridad pero se pierde en recargas.

**Recomendación**: Usar `localStorage` para desarrollo; en producción considerar:
- HttpOnly cookies (requiere cambios en backend).
- Service workers con encriptación.
- Almacenamiento seguro nativo en apps móviles (flutter_secure_storage).

---

## E) EJEMPLOS CURL

### 1. Registrarse

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Respuesta esperada (201 Created)**:
```json
{
  "id": "5dafc0aa-149f-449d-b0fb-8946c2f8f4a4",
  "email": "testuser@example.com",
  "username": "testuser",
  "role": "USER",
  "is_active": true,
  "created_at": "2026-01-16T12:34:56.789Z"
}
```

---

### 2. Login (Obtener Tokens)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "testuser",
    "password": "SecurePass123!"
  }'
```

**Respuesta esperada (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZGFmYzBhYS0xNDlmLTQ0OWQtYjBmYi04OTQ2YzJmOGY0YTQiLCJyb2xlIjoiVVNFUiIsImV4cCI6MTczNjk0OTE4MCwidHlwIjoiYWNjZXNzIn0.xxx",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZGFmYzBhYS0xNDlmLTQ0OWQtYjBmYi04OTQ2YzJmOGY0YTQiLCJyb2xlIjoiVVNFUiIsImV4cCI6MTczNzU0NDE4MCwidHlwIjoicmVmcmVzaCJ9.yyy",
  "token_type": "bearer"
}
```

**Guarda los tokens** en la sesión del frontend.

---

### 3. GET /auth/me (Obtener Datos del Usuario)

```bash
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Respuesta esperada (200 OK)**:
```json
{
  "id": "5dafc0aa-149f-449d-b0fb-8946c2f8f4a4",
  "email": "testuser@example.com",
  "username": "testuser",
  "role": "USER",
  "is_active": true,
  "created_at": "2026-01-16T12:34:56.789Z"
}
```

---

### 4. Refresh Token

```bash
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }"
```

**Respuesta esperada (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(nuevo)",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(nuevo)",
  "token_type": "bearer"
}
```

---

### 5. Logout (Revocar Refresh Token)

```bash
REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://127.0.0.1:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }"
```

**Respuesta esperada (204 No Content)**:
(sin body)

---

## F) FRONTEND NOTES

### Resumen Ejecutivo para el Equipo Frontend

#### 1. Headers Requeridos

Todo request a endpoint protegido debe incluir:

```
Authorization: Bearer {access_token}
```

**Ejemplo**:
```javascript
fetch('http://127.0.0.1:8000/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
})
```

#### 2. Nombres Exactos de Campos

| Campo | Tipo | Uso |
|-------|------|-----|
| `access_token` | string | Incluir en `Authorization: Bearer <access_token>` |
| `refresh_token` | string | Guardar; usar en `/auth/refresh` y `/auth/logout` |
| `token_type` | string | Siempre `"bearer"` |
| `identifier` | string | En login; puede ser email o username |
| `password` | string | Contraseña; máximo 72 bytes UTF-8 |
| `email` | string | Email válido; se valida en registro |
| `username` | string | Username; opcional en registro |
| `id` | UUID | ID del usuario; viene en respuesta `/me` |
| `role` | string | `"ADMIN"` o `"USER"`; viene en respuesta `/me` |
| `is_active` | boolean | `true` = usuario activo; se requiere para endpoints protegidos |

#### 3. Manejo de 401 Unauthorized

**Caso**: El access token ha expirado (15 minutos) o es inválido.

**Acción recomendada**:
1. Detecta 401 en cualquier endpoint protegido.
2. Intenta refrescar el token: `POST /api/v1/auth/refresh` con el `refresh_token`.
3. Si el refresh es exitoso (200 OK): guarda los nuevos tokens y reintenta el request original.
4. Si el refresh falla (401): el refresh token también expiró (7 días) → redirige a login.

**Ejemplo (Pseudocódigo)**:
```javascript
async function fetchWithRefresh(url, options = {}) {
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${getAccessToken()}`
    }
  });

  if (response.status === 401) {
    // Intenta refresh
    const refreshResp = await fetch('http://127.0.0.1:8000/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: getRefreshToken() })
    });

    if (refreshResp.ok) {
      const data = await refreshResp.json();
      saveTokens(data.access_token, data.refresh_token);
      // Reintenta request original
      response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${getAccessToken()}`
        }
      });
    } else {
      // Refresh falló → redirige a login
      window.location.href = '/login';
    }
  }

  return response;
}
```

#### 4. Almacenamiento de Tokens

**Opción A: localStorage (para desarrollo rápido)**
```javascript
// Guardar después de login
function saveTokens(accessToken, refreshToken) {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
}

// Recuperar
function getAccessToken() {
  return localStorage.getItem('access_token');
}

function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

// Limpiar (en logout)
function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}
```

**Opción B: sessionStorage (menos seguro, pero se limpia al cerrar pestaña)**
```javascript
sessionStorage.setItem('access_token', token);
```

**Opción C: Variable global / State (React, Vue, etc.)**
```javascript
// React Hook
const [tokens, setTokens] = useState({ accessToken: null, refreshToken: null });
```

**Nota**: En producción con aplicación nativa (Flutter, React Native), usa almacenamiento seguro:
- Flutter: `flutter_secure_storage`
- React Native: `react-native-keychain`

#### 5. Flujo de Login Completo (Ejemplo)

```javascript
async function login(identifier, password) {
  const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ identifier, password })
  });

  if (response.ok) {
    const { access_token, refresh_token, token_type } = await response.json();

    // Guarda tokens
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // Obtén datos del usuario
    const userResp = await fetch('http://127.0.0.1:8000/api/v1/auth/me', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    });
    const user = await userResp.json();

    // Almacena usuario en estado/contexto
    setUser(user);

    return { success: true, user };
  } else {
    const error = await response.json();
    return { success: false, error: error.detail };
  }
}
```

#### 6. Flujo de Logout Completo

```javascript
async function logout() {
  const refreshToken = localStorage.getItem('refresh_token');

  // Notifica al backend que revoque el refresh token
  await fetch('http://127.0.0.1:8000/api/v1/auth/logout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });

  // Limpia almacenamiento local
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  setUser(null);

  // Redirige a login
  window.location.href = '/login';
}
```

#### 7. Detección de Rol (Admin vs. User)

El token contiene el `role` en el payload:
```javascript
// Después de login, la respuesta de /auth/me incluye:
{
  "role": "ADMIN"  // o "USER"
}

// Úsalo para mostrar/ocultar features
if (user.role === 'ADMIN') {
  // Mostrar panel de administración
}
```

O decodifica el JWT sin enviar al backend:
```javascript
function decodeToken(token) {
  const parts = token.split('.');
  const payload = JSON.parse(atob(parts[1]));
  return payload;
}

const tokenData = decodeToken(accessToken);
console.log(tokenData.role); // "ADMIN" | "USER"
```

#### 8. Validación de Formulario (Password)

**Restricción**: Password máximo 72 bytes (UTF-8).

```javascript
function validatePassword(password) {
  const bytes = new TextEncoder().encode(password);
  if (bytes.length > 72) {
    return { valid: false, error: "Password no puede exceder 72 bytes" };
  }
  if (password.length < 6) {
    return { valid: false, error: "Password mínimo 6 caracteres" };
  }
  return { valid: true };
}
```

#### 9. Endpoints Protegidos (Requieren Token)

| Endpoint | Método | Requiere | Roles Permitidos |
|----------|--------|----------|-----------------|
| `/api/v1/auth/me` | GET | access_token | All |
| `/api/v1/auth/dummy` | GET | access_token | All |
| `/api/v1/auth/refresh` | POST | refresh_token | All |
| `/api/v1/auth/logout` | POST | refresh_token | All |
| `/api/v1/users/` | GET | access_token | ADMIN |
| `/api/v1/users/` | POST | access_token | ADMIN |
| `/api/v1/users/{id}/password` | PATCH | access_token | ADMIN, Owner |
| `/api/v1/users/{id}/role` | PATCH | access_token | ADMIN |
| `/api/v1/users/{id}` | DELETE | access_token | ADMIN |

#### 10. Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `"detail": "Could not validate credentials"` | Token inválido, expirado o malformado | Refresca el token o redirige a login |
| `"detail": "Invalid credentials"` | Email/username o password incorrecto | Verifica credenciales en UI |
| `"detail": "Email already registered"` | Email existe en registro | Usa email diferente o intenta login |
| `"detail": "Inactive user"` | Usuario está desactivado | Contacta a administrador |
| `"detail": "password cannot be longer than 72 bytes..."` | Password supera 72 bytes | Reduce la longitud de password |
| `401 Unauthorized` | No envió Authorization header | Incluye `Authorization: Bearer <token>` |
| `403 Forbidden` | No tiene permisos (ej: no es ADMIN) | Verifica rol del usuario |

---

## RESUMEN RÁPIDO

1. **Login**: POST `/api/v1/auth/login` → obtienes `access_token` (15 min) y `refresh_token` (7 días).
2. **Protegidos**: Incluye `Authorization: Bearer {access_token}` en todos los headers.
3. **Expiración**: Si acceso falla con 401, usa `refresh_token` en POST `/api/v1/auth/refresh`.
4. **Logout**: POST `/api/v1/auth/logout` con `refresh_token` para revocar.
5. **Storage**: Guarda tokens en `localStorage` o estado (no en cookies; backend no las emite).
6. **Me**: GET `/api/v1/auth/me` para obtener datos del usuario actual.

---

**¿Preguntas?** Revisa OpenAPI en `http://127.0.0.1:8000/docs` (Swagger UI) o `http://127.0.0.1:8000/openapi.json`.
