import secrets
import string
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.db.session import get_session
from app.db.models.url import URL
from app.schemas.url import URLCreate, URLResponse, URLList
from app.core.security import set_security_headers
import logging
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()

# Configuración del logger para seguridad
security_logger = logging.getLogger("security")

# Configuración del rate limiter
limiter = Limiter(key_func=get_remote_address)

# Configuración para la generación de códigos cortos
CODE_LENGTH = 6
ALLOWED_CHARS = string.ascii_letters + string.digits

def generate_short_code(length: int = CODE_LENGTH) -> str:
    """Genera un código aleatorio para la URL corta."""
    return ''.join(secrets.choice(ALLOWED_CHARS) for _ in range(length))

async def check_code_exists(db: AsyncSession, code: str) -> bool:
    """Verifica si un código ya existe en la base de datos."""
    result = await db.execute(select(URL).where(URL.code == code))
    return result.scalars().first() is not None

@router.post("/", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_url(
    url_data: URLCreate,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Crea una nueva URL corta."""
    # Registrar la creación para análisis de seguridad
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    security_logger.info(f"Intento de creación de URL: ip={client_ip}, user_agent={user_agent}")

    # Generar un código único
    code = generate_short_code()
    while await check_code_exists(db, code):
        code = generate_short_code()

    # Crear la nueva URL
    new_url = URL(
        original_url=str(url_data.original_url),
        code=code,
        access_count=0
    )

    # Guardar en la base de datos
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)

    # Crear respuesta con cabeceras de seguridad
    response = JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=URLResponse.from_orm(new_url).model_dump(mode="json")
    )

    # Agregar cabeceras de seguridad
    set_security_headers(response)

    return response

@router.get("/", response_model=List[URLList])
@limiter.limit("30/minute")
async def list_urls(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """Lista todas las URLs creadas con paginación."""
    query = select(URL).offset(skip).limit(limit)
    result = await db.execute(query)
    urls = result.scalars().all()

    return urls

@router.get("/{url_id}", response_model=URLResponse)
@limiter.limit("30/minute")
async def get_url(
    url_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Obtiene los detalles de una URL específica por su ID."""
    query = select(URL).where(URL.id == url_id)
    result = await db.execute(query)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL no encontrada"
        )

    return url

@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_url(
    url_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Elimina una URL corta por su ID."""
    # Registrar el intento de eliminación para análisis de seguridad
    client_ip = request.client.host if request.client else "unknown"
    security_logger.info(f"Intento de eliminación de URL: id={url_id}, ip={client_ip}")

    # Verificar que la URL existe
    query = select(URL).where(URL.id == url_id)
    result = await db.execute(query)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL no encontrada"
        )

    # Eliminar la URL
    await db.execute(delete(URL).where(URL.id == url_id))
    await db.commit()

    return None
