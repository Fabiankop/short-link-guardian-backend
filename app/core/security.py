from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Response, Request, HTTPException, status
from app.core.config import get_settings
from typing import Any, Optional, Dict
import secrets
import re

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hashing

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Validación de contraseñas seguras
def validate_password_strength(password: str) -> bool:
    """
    Valida que la contraseña cumpla con requisitos mínimos de seguridad:
    - Al menos 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

# JWT

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # Tiempo de expiración máximo de 30 minutos
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "jti": secrets.token_hex(16)  # JWT ID único para prevenir reutilización
    })
    return jwt.encode(to_encode, settings.secret_key.get_secret_value(), algorithm="HS256")

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Security headers

def set_security_headers(response: Response) -> None:
    # Prevenir XSS
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Reforzar HTTPS
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

    # Política de seguridad de contenido
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'"

    # Política de referencia
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"

    # Control de caché para información sensible
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"

# CSRF protection
def generate_csrf_token() -> str:
    return secrets.token_hex(32)

def validate_csrf_token(request: Request, token: str) -> bool:
    # Implementar validación real del token CSRF
    stored_token = request.session.get("csrf_token")
    if not stored_token:
        return False
    return secrets.compare_digest(stored_token, token)
