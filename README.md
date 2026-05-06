# VotaCiudadano - Sistema de Participacion Ciudadana

VotaCiudadano es una plataforma modular disenada para facilitar la participacion democratica a nivel local. El sistema permite a los ciudadanos registrarse, votar por propuestas urbanas de forma identificada o anonima, y a los administradores gestionar nuevas iniciativas.

## Caracteristicas Principales

- Arquitectura modular con separacion de frontend y backend.
- Sistema de autenticacion con validacion de contrasenas seguras.
- Dos modalidades de votacion: Identificada (con cuenta) y Anonima (sin cuenta).
- Panel de administracion para la creacion de propuestas.
- Modo claro y oscuro persistente.
- Sistema de auditoria de votos mediante hashing SHA-256.
- Respaldos automaticos de la base de datos cada 24 horas.

## Tecnologias Utilizadas

- Frontend: HTML5, CSS3 (Vanilla), JavaScript (Vanilla).
- Backend: Python 3 con Flask.
- Base de Datos: SQLite 3.
- Seguridad: Flask-Bcrypt (Hashing) y PyJWT (Sesiones).

## Requisitos Previos

- Python 3.8 o superior instalado.
- Administrador de paquetes pip.

## Instalacion y Ejecucion

1. Clonar el repositorio:
   git clone https://github.com/SoyPhilips/VotAndo.git

2. Navegar al directorio del proyecto:
   cd VotAndo

3. Instalar las dependencias necesarias:
   pip install -r requirements.txt

4. Ejecutar la aplicacion:
   python app.py

5. Acceder en el navegador:
   Abra la direccion http://localhost:5000 en su navegador web.

## Credenciales de Administrador por Defecto

Para acceder al panel de administracion y crear nuevas propuestas, utilice las siguientes credenciales:

- Correo: admin@vota.com
- Contrasena: Admin123

## Estructura del Proyecto

- app.py: Punto de entrada de la aplicacion y servicio de backups.
- backend/: Contiene los modelos, rutas de API y logica de autenticacion.
- frontend/: Archivos estaticos (HTML, CSS, JS).
- data/: Directorio para la base de datos y respaldos.
- docs/: Documentacion detallada de la API y manuales.

## Seguridad y Auditoria

El sistema utiliza hashing para proteger las contrasenas y garantizar la integridad de cada voto. Cada accion critica es registrada en la tabla de auditoria con la direccion IP y marca de tiempo correspondiente para prevenir fraudes y ataques de fuerza bruta.
