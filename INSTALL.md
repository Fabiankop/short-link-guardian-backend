# Guía de Instalación y Configuración - Spot2

Esta guía proporciona instrucciones detalladas para instalar, configurar y ejecutar el servicio de acortamiento de URLs Spot2 en diferentes entornos.

## Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Local](#instalación-local)
3. [Configuración](#configuración)
4. [Ejecución](#ejecución)
5. [Despliegue con Docker](#despliegue-con-docker)
6. [Despliegue en Kubernetes](#despliegue-en-kubernetes)
7. [Configuración de Base de Datos](#configuración-de-base-de-datos)
8. [Solución de Problemas](#solución-de-problemas)

## Requisitos Previos

### Requisitos de Software

- Python 3.9 o superior
- PostgreSQL 13 o superior
- Redis 6 o superior
- Git

### Dependencias del Sistema (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y build-essential libpq-dev
```

### Dependencias del Sistema (macOS con Homebrew)

```bash
brew install python
brew install postgresql
brew install redis
```

## Instalación Local

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tuorganizacion/spot2.git
cd spot2/backend
```

### 2. Crear y Activar Entorno Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del directorio `backend` con el siguiente contenido:

```
# Configuración de la aplicación
DEBUG=False
SECRET_KEY=tu_clave_secreta_muy_segura
ENVIRONMENT=development  # development, testing, production

# Configuración de la base de datos
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost/spot2
# O configuración por componentes
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=spot2

# Configuración de Redis
REDIS_URL=redis://localhost:6379/0

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000,https://tudominio.com,http://localhost:8080

# Configuración de Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_CREATE_URL=10/minute
RATE_LIMIT_REDIRECT=60/minute

# Configuración de seguridad
TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### 2. Configuración de la Base de Datos

#### Crear Base de Datos en PostgreSQL

```bash
sudo -u postgres psql
```

En la consola de PostgreSQL:

```sql
CREATE DATABASE spot2;
CREATE USER usuario WITH ENCRYPTED PASSWORD 'contraseña';
GRANT ALL PRIVILEGES ON DATABASE spot2 TO usuario;
\q
```

#### Aplicar Migraciones

```bash
alembic upgrade head
```

## Ejecución

### 1. Iniciar Redis

Asegúrate de que Redis esté ejecutándose:

```bash
# En Ubuntu/Debian
sudo systemctl start redis-server

# En macOS
brew services start redis
```

### 2. Iniciar la Aplicación

Para desarrollo:

```bash
uvicorn app.main:app --reload --port 8000
```

Para producción:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

## Despliegue con Docker

### 1. Construir y Ejecutar con Docker Compose

Asegúrate de tener Docker y Docker Compose instalados.

```bash
docker-compose up --build -d
```

Esto iniciará:
- La aplicación FastAPI
- PostgreSQL
- Redis

### 2. Aplicar Migraciones en Docker

```bash
docker-compose exec app alembic upgrade head
```

### 3. Verificar Logs

```bash
docker-compose logs -f app
```

## Despliegue en Kubernetes

### 1. Requisitos

- Cluster Kubernetes configurado
- kubectl instalado y configurado
- Helm (opcional, para gestionar releases)

### 2. Desplegar Recursos

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/postgresql.yaml
kubectl apply -f kubernetes/redis.yaml
kubectl apply -f kubernetes/app-deployment.yaml
kubectl apply -f kubernetes/app-service.yaml
kubectl apply -f kubernetes/ingress.yaml
```

### 3. Verificar Despliegue

```bash
kubectl get pods -n spot2
kubectl get services -n spot2
kubectl get ingress -n spot2
```

### 4. Aplicar Migraciones

```bash
kubectl exec -it $(kubectl get pods -n spot2 -l app=spot2 -o jsonpath="{.items[0].metadata.name}") -n spot2 -- alembic upgrade head
```

## Configuración de Base de Datos

### Estructura de Migraciones

Las migraciones se gestionan con Alembic. La estructura de archivos es:

```
alembic/
├── versions/       # Archivos de migración
├── env.py          # Entorno de migraciones
└── alembic.ini     # Configuración de Alembic
```

### Crear Nueva Migración

```bash
alembic revision --autogenerate -m "descripción de la migración"
```

### Aplicar Migraciones

```bash
alembic upgrade head  # Aplicar todas las migraciones pendientes
alembic upgrade +1    # Aplicar solo la siguiente migración
```

### Revertir Migraciones

```bash
alembic downgrade -1  # Revertir última migración
alembic downgrade base  # Revertir todas las migraciones
```

## Solución de Problemas

### Problemas de Conexión a la Base de Datos

1. **Error de conexión rechazada**:
   - Verifica que PostgreSQL esté en ejecución
   - Comprueba las credenciales en `.env`
   - Verifica la configuración de `pg_hba.conf` para permitir conexiones

2. **Error de migración**:
   - Verifica que la base de datos exista
   - Comprueba los permisos del usuario de la base de datos
   - Revisa los logs de Alembic para errores específicos

### Problemas de Rate Limiting

1. **Rate limiting no funciona**:
   - Verifica que Redis esté en ejecución
   - Comprueba la URL de conexión a Redis
   - Asegúrate de que la configuración del limiter esté correcta

### Logs y Diagnóstico

Para habilitar logs detallados en desarrollo:

```
DEBUG=True
LOG_LEVEL=DEBUG
```

Ubicación de archivos de log:
- Logs de aplicación: `logs/app.log`
- Logs de seguridad: `logs/security.log`

## Recursos Adicionales

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentación de Alembic](https://alembic.sqlalchemy.org/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Documentación de Kubernetes](https://kubernetes.io/docs/)
