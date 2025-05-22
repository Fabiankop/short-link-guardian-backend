from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from redis.asyncio import Redis
import logging

from app.api.v1 import user_routes, ws_routes, url_routes, redirect_routes
from app.core.config import get_settings
from app.middleware.error_handler import add_error_handling
from app.middleware.docs_protect import DocsProtectMiddleware

settings = get_settings()

app = FastAPI(title="FastAPI Project Base")

# Logging setup
logging_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

# Redis connection
redis = Redis.from_url(settings.redis_url, decode_responses=True)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling
add_error_handling(app)

# Routers
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
app.include_router(url_routes.router, prefix="/api/v1/urls", tags=["urls"])
app.include_router(redirect_routes.router, prefix="/r", tags=["redirect"])
app.include_router(ws_routes.router)

app.add_middleware(DocsProtectMiddleware)
