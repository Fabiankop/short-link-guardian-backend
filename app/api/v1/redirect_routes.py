from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import logging
from app.db.session import get_session
from app.db.models.url import URL
from app.core.security import set_security_headers
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()

# Lista de dominios potencialmente maliciosos
BLOCKED_DOMAINS: List[str] = [
    "malicious.com",
    "phishing.com",
    "malware.com",
    # Agregar más dominios a la lista negra según sea necesario
]

# Logger configurado para seguridad
security_logger = logging.getLogger("security")

# Configuración del rate limiter
limiter = Limiter(key_func=get_remote_address)

def is_url_safe(url: str) -> bool:
    """Verifica si una URL es segura para redireccionar."""
    url_lower = url.lower()

    # Verificar dominios bloqueados
    for domain in BLOCKED_DOMAINS:
        if domain in url_lower:
            security_logger.warning(f"Intento de redirección a dominio bloqueado: {url}")
            return False

    # Verificar protocolo (solo permitir https y http)
    if not url_lower.startswith(('http://', 'https://')):
        security_logger.warning(f"Intento de redirección con protocolo no permitido: {url}")
        return False

    return True

@router.get("/api/url/{code}", response_model=dict)
@limiter.limit("60/minute")
async def get_url_info(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_session)
):
    """Devuelve la URL original desde un código corto (uso AJAX)."""
    
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    security_logger.info(f"Consulta AJAX: code={code}, ip={client_ip}, user_agent={user_agent}")

    q = select(URL).where(URL.code == code)
    result = await db.execute(q)
    url = result.scalars().first()

    if not url:
        security_logger.warning(f"Código inexistente: {code} desde {client_ip}")
        raise HTTPException(status_code=404, detail="URL no encontrada")

    if not is_url_safe(url.original_url):
        security_logger.error(f"URL insegura: {url.original_url}")
        raise HTTPException(status_code=403, detail="URL bloqueada por seguridad")

    # Registrar acceso (opcional para AJAX)
    await db.execute(
        update(URL)
        .where(URL.id == url.id)
        .values(access_count=URL.access_count + 1)
    )
    await db.commit()

    return {"url": url.original_url}
