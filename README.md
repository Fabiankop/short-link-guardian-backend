# Spot2 - Servicio de Acortamiento de URLs

Spot2 es un servicio de acortamiento de URLs seguro y robusto construido con FastAPI. Permite crear, gestionar y utilizar URLs cortas con un enfoque prioritario en la seguridad.

## Características Principales

- 🔄 Creación y gestión de URLs cortas
- 🔒 Implementación de múltiples capas de seguridad
- 🚀 Alto rendimiento con operaciones asíncronas
- 📊 Seguimiento de estadísticas de uso
- 🛡️ Protección contra ataques comunes

## Requisitos

- Python 3.9+
- PostgreSQL 13+
- Redis 6+

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuorganizacion/spot2.git
cd spot2/backend
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
# Configuración de la base de datos
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost/spot2

# Configuración de seguridad
SECRET_KEY=tu_clave_secreta_muy_segura
DEBUG=False

# Configuración de Redis (para rate limiting)
REDIS_URL=redis://localhost:6379/0

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000,https://tudominio.com,http://localhost:8080
```

### 5. Ejecutar migraciones

```bash
alembic upgrade head
```

### 6. Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`.

## Uso

### API Endpoints

#### Creación de URL corta

```http
POST /api/v1/urls
```

**Payload:**
```json
{
  "original_url": "https://ejemplo.com/pagina/muy/larga"
}
```

**Respuesta:**
```json
{
  "id": 1,
  "code": "abc123",
  "original_url": "https://ejemplo.com/pagina/muy/larga",
  "created_at": "2023-07-01T12:00:00",
  "access_count": 0
}
```

#### Listar URLs

```http
GET /api/v1/urls
```

#### Obtener detalles de URL

```http
GET /api/v1/urls/{url_id}
```

#### Eliminar URL

```http
DELETE /api/v1/urls/{url_id}
```

#### Redirección

```http
GET /r/{code}
```

## Arquitectura

La aplicación sigue una arquitectura en capas:

1. **Capa de Presentación (API)**: Controladores FastAPI en `app/api/`
2. **Capa de Lógica de Negocio**: Servicios y utilidades en `app/core/`
3. **Capa de Datos**: Modelos y acceso a datos en `app/db/`
4. **Capa de Validación**: Esquemas Pydantic en `app/schemas/`

### Decisiones de Diseño

#### Generación de Códigos Cortos

Se utiliza un algoritmo de generación de códigos aleatorios con verificación de unicidad para evitar colisiones. Esto proporciona un equilibrio óptimo entre longitud del código y probabilidad de colisión.

```python
def generate_short_code(length: int = CODE_LENGTH) -> str:
    return ''.join(secrets.choice(ALLOWED_CHARS) for _ in range(length))
```

#### Operaciones Asíncronas

Todas las operaciones de base de datos utilizan SQLAlchemy con soporte asíncrono (asyncpg) para maximizar el rendimiento y la escalabilidad.

#### Rate Limiting

Se implementa limitación de tasa para prevenir abusos:
- Creación de URLs: 10 por minuto
- Consultas: 30 por minuto
- Eliminaciones: 5 por minuto
- Redirecciones: 60 por minuto

## Seguridad

La seguridad es una prioridad en Spot2:

1. **Validación de URLs**: Todas las URLs son validadas mediante Pydantic con reglas estrictas.
2. **Lista Negra de Dominios**: Se bloquean dominios conocidos por actividades maliciosas.
3. **Cabeceras de Seguridad**: Implementación de cabeceras HTTP de seguridad en todas las respuestas.
4. **Logging de Seguridad**: Registro detallado de actividades sospechosas.
5. **Prevención de SQL Injection**: Uso exclusivo de SQLAlchemy ORM con parámetros seguros.
6. **Rate Limiting**: Protección contra ataques de fuerza bruta y DoS.

Consulta [SECURITY.md](SECURITY.md) para más detalles sobre las políticas de seguridad.

## Despliegue en Producción

### Docker

El proyecto incluye configuración Docker para facilitar el despliegue:

```bash
docker-compose up -d
```

### Kubernetes

Para entornos de producción, recomendamos usar Kubernetes:

```bash
kubectl apply -f kubernetes/
```

### Consideraciones para Producción

1. Utilizar un servicio gestionado para PostgreSQL o configurar alta disponibilidad.
2. Implementar Redis en clúster para el rate limiting.
3. Configurar balanceo de carga y autoescalado.
4. Habilitar HTTPS/TLS en todos los endpoints.
5. Implementar monitoreo y alertas.

## Monitoreo y Logging

La aplicación utiliza un sistema de logging estructurado:

- **Logs de Aplicación**: Información general y errores
- **Logs de Seguridad**: Eventos relacionados con la seguridad
- **Logs de Acceso**: Detalles sobre las redirecciones y uso

Se recomienda integrar con servicios como Datadog, Prometheus o ELK Stack.

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Realiza los cambios necesarios y haz commit (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

Por favor, asegúrate de seguir las [directrices de contribución](CONTRIBUTING.md) y el [código de conducta](CODE_OF_CONDUCT.md).

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Equipo de Desarrollo - dev@tuorganizacion.com

Link del Proyecto: [https://github.com/tuorganizacion/spot2](https://github.com/tuorganizacion/spot2)
