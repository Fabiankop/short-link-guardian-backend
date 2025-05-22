FROM python:3.11-slim

WORKDIR /app

# Instalar herramientas necesarias
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Configurar el script de entrypoint
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Cambiar a un solo CMD que usa el entrypoint
CMD ["/app/entrypoint.sh"]
