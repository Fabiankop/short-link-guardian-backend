# Documento de Diseño Técnico - Spot2

Este documento describe la arquitectura, decisiones técnicas y consideraciones de seguridad del servicio de acortamiento de URLs Spot2.

## Arquitectura General

Spot2 está construido como una aplicación de API REST moderna utilizando FastAPI y siguiendo una arquitectura en capas para mantener el código modular, testeable y fácil de mantener.

```
app/
├── api/              # Capa de presentación (controladores)
│   └── v1/           # Endpoints de la versión 1 de la API
├── core/             # Configuración y utilidades centrales
├── db/               # Capa de acceso a datos
│   ├── models/       # Modelos SQLAlchemy
│   └── session.py    # Gestión de sesiones de BD
├── schemas/          # Modelos Pydantic para validación
├── middleware/       # Middleware personalizado
└── main.py           # Punto de entrada de la aplicación
```

### Principios Arquitectónicos

1. **Separación de Responsabilidades**: Cada capa tiene una responsabilidad específica.
2. **Inmutabilidad**: Los modelos Pydantic garantizan validación e inmutabilidad de datos.
3. **Fail-Fast**: Validación temprana de errores para evitar fallos en capas profundas.
4. **Testabilidad**: Código modular fácil de probar mediante inyección de dependencias.
5. **Seguridad por Diseño**: Medidas de seguridad integradas desde el inicio.

## Decisiones Técnicas Clave

### 1. FastAPI como Framework

FastAPI fue seleccionado por sus ventajas significativas:

- Alto rendimiento basado en Starlette y Pydantic
- Soporte nativo para operaciones asíncronas
- Validación automática de datos con Pydantic
- Documentación automática (OpenAPI)
- Tipado estático para seguridad del código

### 2. Base de Datos y ORM

Se eligió PostgreSQL como base de datos principal por:

- Soporte robusto para índices y búsquedas
- Alta confiabilidad y rendimiento
- Amplio ecosistema y soporte

SQLAlchemy se usa como ORM con las siguientes consideraciones:

- Uso de SQLAlchemy 2.0 con sintaxis asíncrona moderna
- Operaciones asíncronas vía asyncpg para mayor rendimiento
- Abstracción consistente de operaciones de base de datos
- Migraciones gestionadas con Alembic

### 3. Diseño del Modelo de Datos

```
URL
├── id: Integer (PK)
├── code: String (unique, indexed)
├── original_url: Text
├── created_at: DateTime
└── access_count: Integer
```

Consideraciones:
- `code` está indexado para búsquedas rápidas
- `original_url` usa tipo Text para URLs largas
- `access_count` permite seguimiento de estadísticas
- Todos los campos tienen restricciones NOT NULL

### 4. Generación de Códigos Cortos

Se implementó un algoritmo de generación de códigos con las siguientes características:

- Longitud predeterminada de 6 caracteres (configurable)
- Conjunto de caracteres alfanuméricos (62 posibles caracteres)
- Probabilidad de colisión extremadamente baja (~3.5e10 combinaciones)
- Verificación de unicidad en la base de datos

### 5. Operaciones Asíncronas

Toda la aplicación utiliza operaciones asíncronas para:

- Maximizar el rendimiento bajo carga
- Manejar múltiples conexiones concurrentes
- Optimizar operaciones de E/S (BD, Redis, etc.)
- Escalar eficientemente con recursos limitados

### 6. Sistema de Rate Limiting

Se implementó un sistema de limitación de tasa basado en Redis:

- Protección contra abusos y ataques DoS
- Configuración específica por tipo de operación
- Seguimiento por dirección IP
- Almacenamiento en Redis para persistencia

## Consideraciones de Seguridad

### 1. Validación de URLs

Se implementaron múltiples capas de validación:

- Validación básica con Pydantic (HttpUrl)
- Verificación adicional de dominios bloqueados
- Limitación de longitud (máx. 2048 caracteres)
- Verificación de protocolos permitidos (http/https)

### 2. Protección contra Ataques

- **Inyección SQL**: Uso exclusivo de SQLAlchemy ORM con parámetros
- **XSS**: Cabeceras de seguridad y validación estricta
- **CSRF**: Tokens de protección para operaciones sensibles
- **Rate Limiting**: Protección contra ataques de fuerza bruta

### 3. Cabeceras de Seguridad

Todas las respuestas incluyen cabeceras de seguridad:

```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'"
response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
```

### 4. Logging de Seguridad

Se implementó un sistema de logging específico para eventos de seguridad:

- Registro de todos los intentos de creación/redirección
- Almacenamiento de información contextual (IP, user-agent)
- Alertas para comportamientos sospechosos
- No incluye información sensible en logs

## Escalabilidad y Rendimiento

### 1. Estrategia de Escalado Horizontal

La aplicación está diseñada para escalar horizontalmente:

- Sin estado entre solicitudes
- Almacenamiento compartido en Redis para rate limiting
- Base de datos centralizada con conexiones eficientes
- Compatible con despliegue en contenedores

### 2. Optimizaciones de Rendimiento

- Operaciones asíncronas para maximizar concurrencia
- Índices optimizados en la base de datos
- Conexiones pooling para la base de datos
- Esquema de datos denormalizado para optimizar lecturas

### 3. Estrategia de Caché

Para implementaciones de alto tráfico, se recomienda:

- Caché de Redis para códigos de URL frecuentes
- Caché de CDN para redirecciones populares
- TTL configurables según patrones de uso

## Monitoreo y Observabilidad

El sistema incluye instrumentación para:

- Logging estructurado para debugging
- Métricas de rendimiento (tiempos de respuesta, tasas de error)
- Seguimiento de uso (estadísticas de redirección)
- Alertas para comportamientos anómalos

## Futuras Mejoras y Consideraciones

1. **Autenticación de Usuarios**:
   - Implementar sistema de usuarios para URLs privadas
   - Permitir a usuarios gestionar sus propias URLs

2. **Funcionalidades Avanzadas**:
   - URLs con expiración temporal
   - Análisis detallado de uso (geografía, dispositivos)
   - Personalización de códigos cortos

3. **Optimizaciones**:
   - Sistema de caché distribuido
   - Sharding de base de datos para escalabilidad extrema
   - Implementación de GraphQL para consultas complejas

4. **Herramientas Administrativas**:
   - Panel de administración para gestión de URLs
   - Herramientas de detección de abuso
   - Reportes y análisis de uso

## Conclusión

Spot2 está diseñado como un servicio de acortamiento de URLs robusto, seguro y de alto rendimiento. La arquitectura modular y las decisiones técnicas tomadas permiten un sistema fácilmente mantenible y escalable para satisfacer necesidades futuras.
