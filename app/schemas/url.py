from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, validator, Field


class URLBase(BaseModel):
    original_url: HttpUrl = Field(..., description="URL original a acortar")

    @validator('original_url')
    def validate_url(cls, v):
        # Implementar validaciones de seguridad adicionales
        blocked_domains = ["malicious.com", "phishing.com", "malware.com"]
        url_str = str(v).lower()

        # Verificar dominios bloqueados
        for domain in blocked_domains:
            if domain in url_str:
                raise ValueError(f"El dominio {domain} está bloqueado por motivos de seguridad")

        # Validar protocolo (solo permitir https y http)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError("Solo se permiten URLs con protocolos HTTP y HTTPS")

        # Límite de longitud para prevenir ataques de DOS
        if len(url_str) > 2048:
            raise ValueError("La URL es demasiado larga (máximo 2048 caracteres)")

        return v


class URLCreate(URLBase):
    pass


class URLResponse(URLBase):
    id: int
    code: str
    created_at: datetime
    access_count: int

    class Config:
        from_attributes = True


class URLList(BaseModel):
    id: int
    code: str
    original_url: str
    created_at: datetime
    access_count: int

    class Config:
        from_attributes = True
