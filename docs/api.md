# Documentación de la API Interna - VotaCiudadano

## Autenticación

### POST `/api/auth/register`
Registra un nuevo usuario.
- **Body**: `{ "email": "...", "password": "..." }`
- **Validación**: Email único, password >= 8 chars, 1 upper, 1 lower, 1 digit.

### POST `/api/auth/login`
Inicia sesión.
- **Body**: `{ "email": "...", "password": "..." }`
- **Response**: `{ "token": "JWT_TOKEN", "user": { "email": "...", "is_admin": bool } }`

### DELETE `/api/auth/me`
Elimina la cuenta del usuario autenticado.
- **Headers**: `Authorization: Bearer <token>`

## Propuestas

### GET `/api/proposals`
Lista todas las propuestas.
- **Response**: Array de objetos de propuesta.

### POST `/api/proposals`
Crea una nueva propuesta (Solo Admin).
- **Headers**: `Authorization: Bearer <token>`
- **Body**: `{ "title", "description", "category", "start_date", "end_date" }`

## Votación

### POST `/api/vote`
Registra un voto.
- **Body**: `{ "proposal_id": int }`
- **Identificado**: Requiere header `Authorization`.
- **Anónimo**: Requiere header `X-Anon-Voter-ID` (manejado automáticamente por el cliente).
- **Regla**: 1 voto por usuario/anon_id por propuesta.
