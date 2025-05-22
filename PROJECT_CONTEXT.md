# Proyecto Base FastAPI – Documentación para el Dueño del Proyecto

## 1. Arquitectura General

Este proyecto está diseñado para ser un punto de partida robusto, seguro y escalable para APIs modernas con FastAPI. Incluye autenticación JWT, gestión avanzada de usuarios, integración con Redis, tareas en background (Celery), internacionalización, rate limiting, protección de documentación, métricas Prometheus, tests automáticos y más.

### Estructura de Carpetas
- `app/` – Código principal de la aplicación
  - `api/v1/` – Rutas de la API (users, items, websockets)
  - `core/` – Configuración, seguridad, logging, i18n, celery, health, prometheus
  - `db/` – Modelos y sesión de base de datos
  - `schemas/` – Esquemas Pydantic para validación y serialización
  - `services/` – Lógica de negocio y utilidades (usuarios, items, email, etc.)
  - `middleware/` – Middlewares personalizados (errores, protección de docs)
- `alembic/` – Migraciones de base de datos
- `tests/` – Tests automáticos

## 2. Flujos y Funcionalidades Clave

### Autenticación y Usuarios
- Registro, login y protección de rutas con JWT.
- Roles y permisos (admin, user).
- Verificación de email y recuperación de contraseña (emails enviados en background con Celery).
- Rate limiting global y por usuario usando Redis.

### Items y CRUD
- CRUD completo de items, paginación y protección por usuario propietario.
- Subida y descarga de archivos.

### WebSockets
- Endpoint de ejemplo (`/ws/echo`) protegido por JWT.

### Background Tasks
- Celery configurado con Redis para tareas asíncronas (ejemplo: envío de emails).

### Internacionalización (i18n)
- Mensajes de error y notificaciones traducibles (es/en) usando Babel y archivos `.po`.

### Seguridad y Observabilidad
- Headers de seguridad, CSRF stub, protección de `/docs` y `/redoc` en producción (solo admin).
- Health check (`/health`) y métricas Prometheus (`/metrics`).
- Logging estructurado y configurable, integración opcional con Sentry.

### Calidad y DevOps
- Tests automáticos con pytest y httpx.
- Linting y formateo con black, isort, flake8, pre-commit.
- Docker y docker-compose para desarrollo y producción.
- Ejemplo de configuración en `.env.example`.

## 3. Mantenimiento y Escalabilidad

- **Agregar módulos:** Crea nuevos routers, modelos, servicios y esquemas siguiendo la estructura modular.
- **Migraciones:** Usa Alembic para cambios en el esquema de la base de datos.
- **Background tasks:** Añade nuevas tareas en `core/celery_app.py` y llama desde servicios.
- **Internacionalización:** Agrega nuevos mensajes en los archivos `.po` y compílalos con Babel.
- **Seguridad:** Mantén las dependencias actualizadas y revisa los logs de Sentry.
- **Tests:** Añade tests para nuevas rutas y lógica de negocio en la carpeta `tests/`.

## 4. Recomendaciones
- Revisa y actualiza las dependencias periódicamente.
- Configura correctamente las variables de entorno en producción.
- Realiza code reviews para cambios críticos.
- Usa los ejemplos del README para validar la API rápidamente.
- Documenta cualquier integración externa adicional (pagos, notificaciones, etc.).

---

Para dudas técnicas o ampliaciones, consulta la documentación en el código y el README.
