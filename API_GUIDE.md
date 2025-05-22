# Guía de API - Spot2

Esta guía proporciona información detallada sobre los endpoints disponibles en la API de Spot2, un servicio de acortamiento de URLs.

## Índice

1. [Información General](#información-general)
2. [Autenticación](#autenticación)
3. [Endpoints de URLs](#endpoints-de-urls)
4. [Endpoints de Redirección](#endpoints-de-redirección)
5. [Códigos de Error](#códigos-de-error)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Buenas Prácticas](#buenas-prácticas)
8. [Limitaciones](#limitaciones)

## Información General

**URL Base**: `https://api.tudominio.com` (producción) o `http://localhost:8000` (desarrollo)

**Formatos de Respuesta**: Todas las respuestas son en formato JSON, excepto las redirecciones que usan cabeceras HTTP.

**Versionado de API**: Los endpoints están versionados con el prefijo `/api/v1/`.

**Límites de Tasa**: Existen límites de tasa para prevenir abusos. Consulta la sección de [Limitaciones](#limitaciones) para más detalles.

**Documentación OpenAPI**: Disponible en `/docs` (Swagger UI) o `/redoc` (ReDoc).

## Autenticación

Actualmente, la API no requiere autenticación para operaciones básicas. Las restricciones se basan principalmente en limitaciones de tasa por dirección IP.

En futuras versiones, se implementará autenticación mediante JWT para permitir a los usuarios gestionar sus propias URLs.

## Endpoints de URLs

### Crear URL Corta

**Endpoint**: `POST /api/v1/urls/`

**Descripción**: Crea una nueva URL corta a partir de una URL original.

**Request Body**:
```json
{
  "original_url": "https://ejemplo.com/pagina/muy/larga"
}
```

**Respuesta Exitosa** (201 Created):
```json
{
  "id": 1,
  "code": "abc123",
  "original_url": "https://ejemplo.com/pagina/muy/larga",
  "created_at": "2023-07-01T12:00:00",
  "access_count": 0
}
```

**Errores**:
- 400 Bad Request: URL inválida o bloqueada
- 422 Unprocessable Entity: Datos de entrada inválidos
- 429 Too Many Requests: Límite de tasa excedido

### Listar URLs

**Endpoint**: `GET /api/v1/urls/`

**Descripción**: Recupera una lista de URLs cortas con paginación.

**Parámetros de Query**:
- `skip` (opcional): Número de elementos a omitir (default: 0)
- `limit` (opcional): Número máximo de elementos a retornar (default: 100, max: 100)

**Respuesta Exitosa** (200 OK):
```json
[
  {
    "id": 1,
    "code": "abc123",
    "original_url": "https://ejemplo.com/pagina/muy/larga",
    "created_at": "2023-07-01T12:00:00",
    "access_count": 5
  },
  {
    "id": 2,
    "code": "def456",
    "original_url": "https://otro-ejemplo.com/otra/pagina/larga",
    "created_at": "2023-07-02T14:30:00",
    "access_count": 2
  }
]
```

**Errores**:
- 429 Too Many Requests: Límite de tasa excedido

### Obtener Detalles de URL

**Endpoint**: `GET /api/v1/urls/{url_id}`

**Descripción**: Recupera los detalles de una URL específica por su ID.

**Parámetros de Path**:
- `url_id`: ID numérico de la URL

**Respuesta Exitosa** (200 OK):
```json
{
  "id": 1,
  "code": "abc123",
  "original_url": "https://ejemplo.com/pagina/muy/larga",
  "created_at": "2023-07-01T12:00:00",
  "access_count": 5
}
```

**Errores**:
- 404 Not Found: URL no encontrada
- 429 Too Many Requests: Límite de tasa excedido

### Eliminar URL

**Endpoint**: `DELETE /api/v1/urls/{url_id}`

**Descripción**: Elimina una URL específica por su ID.

**Parámetros de Path**:
- `url_id`: ID numérico de la URL

**Respuesta Exitosa** (204 No Content)

**Errores**:
- 404 Not Found: URL no encontrada
- 429 Too Many Requests: Límite de tasa excedido

## Endpoints de Redirección

### Redireccionar a URL Original

**Endpoint**: `GET /r/{code}`

**Descripción**: Redirecciona al usuario a la URL original correspondiente al código corto.

**Parámetros de Path**:
- `code`: Código corto de la URL

**Respuesta Exitosa**: Redirección 307 Temporary Redirect

**Errores**:
- 404 Not Found: Código de URL no encontrado
- 403 Forbidden: URL bloqueada por motivos de seguridad
- 429 Too Many Requests: Límite de tasa excedido

## Códigos de Error

La API utiliza códigos de estado HTTP estándar para indicar el resultado de las solicitudes:

- **200 OK**: Solicitud exitosa
- **201 Created**: Recurso creado exitosamente
- **204 No Content**: Solicitud exitosa, sin contenido para retornar
- **400 Bad Request**: Solicitud inválida o datos mal formados
- **403 Forbidden**: Acceso prohibido
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Datos de entrada no válidos
- **429 Too Many Requests**: Límite de tasa excedido
- **500 Internal Server Error**: Error interno del servidor

Los errores incluyen un cuerpo JSON con detalles adicionales:

```json
{
  "detail": "Mensaje descriptivo del error"
}
```

## Ejemplos de Uso

### Crear y Acceder a una URL Corta (cURL)

```bash
# Crear una URL corta
curl -X POST "http://localhost:8000/api/v1/urls/" \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://ejemplo.com/pagina/muy/larga"}'

# Respuesta
# {
#   "id": 1,
#   "code": "abc123",
#   "original_url": "https://ejemplo.com/pagina/muy/larga",
#   "created_at": "2023-07-01T12:00:00",
#   "access_count": 0
# }

# Acceder a la URL corta (esto redirigirá al navegador)
curl -L "http://localhost:8000/r/abc123"
```

### Crear y Acceder a una URL Corta (Python)

```python
import requests

# Crear una URL corta
response = requests.post(
    "http://localhost:8000/api/v1/urls/",
    json={"original_url": "https://ejemplo.com/pagina/muy/larga"}
)
data = response.json()
code = data["code"]
print(f"URL corta creada: http://localhost:8000/r/{code}")

# Acceder a la URL corta (en un navegador o con seguimiento de redirecciones)
redirect_response = requests.get(
    f"http://localhost:8000/r/{code}",
    allow_redirects=False
)
print(f"Redirección a: {redirect_response.headers['Location']}")
```

### Integración Web (JavaScript)

```javascript
// Crear una URL corta
async function createShortUrl(originalUrl) {
  const response = await fetch("http://localhost:8000/api/v1/urls/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ original_url: originalUrl })
  });

  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }

  const data = await response.json();
  return `http://localhost:8000/r/${data.code}`;
}

// Uso
createShortUrl("https://ejemplo.com/pagina/muy/larga")
  .then(shortUrl => {
    console.log(`URL corta: ${shortUrl}`);
    // Actualizar la interfaz de usuario
  })
  .catch(error => {
    console.error("Error al crear URL corta:", error);
  });
```

## Buenas Prácticas

1. **Manejo de Errores**: Implementa manejo adecuado de errores para todos los códigos de estado posibles.

2. **Limitación de Tasa**: Respeta los límites de tasa y añade espera exponencial para reintentos.

3. **Validación de URLs**: Valida las URLs en el cliente antes de enviarlas al servidor.

4. **Caché**: Considera almacenar en caché las respuestas para URLs frecuentemente accedidas.

5. **Timeouts**: Configura timeouts adecuados para las solicitudes a la API.

6. **Seguridad**: Verifica la seguridad de las URLs antes de permitir su acortamiento.

## Limitaciones

### Límites de Tasa

Para prevenir abusos, la API implementa los siguientes límites de tasa:

- Creación de URLs: 10 solicitudes por minuto por IP
- Consulta de URLs: 30 solicitudes por minuto por IP
- Eliminación de URLs: 5 solicitudes por minuto por IP
- Redirecciones: 60 solicitudes por minuto por IP

### Restricciones de Contenido

La API bloquea URLs que:
- Contienen dominios conocidos por actividades maliciosas
- No utilizan protocolos http o https
- Exceden 2048 caracteres de longitud

### Limitaciones Técnicas

- Tamaño máximo de carga útil: 1MB
- Tiempo máximo de respuesta: 30 segundos
- Número máximo de URLs por consulta: 100
