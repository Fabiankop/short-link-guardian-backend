# Makefile para entorno local

.PHONY: help install run migrate test worker clean

help:
	@echo "Comandos disponibles:"
	@echo "  install      Instala dependencias en entorno local"
	@echo "  run          Inicia la app FastAPI localmente"
	@echo "  migrate      Aplica migraciones Alembic"
	@echo "  test         Ejecuta los tests automáticos"
	@echo "  worker       Inicia el worker de Celery"
	@echo "  clean        Elimina archivos pyc y carpetas __pycache__"
	@echo "  docker-up    Levanta todo el stack con Docker Compose"
	@echo "  docker-down  Detiene los contenedores Docker"
	@echo "  docker-migrate Ejecuta migraciones dentro del contenedor Docker"
	@echo "  docker-test  Ejecuta los tests dentro del contenedor Docker"

install:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head

test:
	pytest

worker:
	celery -A app.core.celery_app.celery_app worker --loglevel=info

clean:
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

# Comandos para Docker

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-migrate:
	docker-compose exec app alembic upgrade head

docker-test:
	docker-compose exec app pytest
