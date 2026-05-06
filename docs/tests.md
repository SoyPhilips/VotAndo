# Casos de Prueba - VotaCiudadano

## 1. Autenticación
| ID | Descripción | Entrada | Resultado Esperado |
|---|---|---|---|
| AUTH-01 | Registro con password débil | Email: test@test.com, Pass: 123 | Error: Validación de contraseña |
| AUTH-02 | Registro exitoso | Email: user@test.com, Pass: Valid123 | Éxito: Usuario creado |
| AUTH-03 | Login exitoso | Email: user@test.com, Pass: Valid123 | Éxito: JWT retornado |
| AUTH-04 | Eliminar cuenta | Usuario autenticado | Éxito: Datos eliminados de DB |

## 2. Votación
| ID | Descripción | Entrada | Resultado Esperado |
|---|---|---|---|
| VOTE-01 | Voto anónimo duplicado | Clic en "Votar" dos veces | Error: Ya has votado por esta propuesta |
| VOTE-02 | Voto identificado | Usuario logueado, clic en "Votar" | Éxito: Voto con user_id |
| VOTE-03 | Integridad de voto | Realizar voto | Hash SHA256 generado y guardado |

## 3. Administración
| ID | Descripción | Entrada | Resultado Esperado |
|---|---|---|---|
| ADMIN-01 | Crear propuesta (No admin) | Usuario estándar intentando POST | Error 403: Forbidden |
| ADMIN-02 | Crear propuesta (Admin) | Admin logueado, datos válidos | Éxito: Propuesta aparece en Dashboard |

## 4. Sistema
| ID | Descripción | Acción | Resultado Esperado |
|---|---|---|---|
| SYS-01 | Backup automático | Dejar app corriendo | Archivo .db en /data/backups cada 24h |
| SYS-02 | Modo Oscuro | Clic en icono 🌓 | Atributo data-theme cambia y se guarda en localStorage |
