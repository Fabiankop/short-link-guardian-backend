#!/bin/sh

# Esperar a que la base de datos esté disponible
echo "Esperando a que la base de datos esté disponible..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "Base de datos disponible"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
alembic upgrade head

# Iniciar la aplicación
echo "Iniciando aplicación..."
exec uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT