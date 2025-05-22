from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError
from app.core.security import decode_access_token
import os

class DocsProtectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        env = os.getenv("ENV", "development")
        if env == "production" and request.url.path in ["/docs", "/redoc"]:
            token = request.cookies.get("access_token") or request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Not authenticated"})
            try:
                payload = decode_access_token(token)
                if payload.get("role") != "admin":
                    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not enough permissions"})
            except JWTError:
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token"})
        return await call_next(request)
