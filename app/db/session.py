from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

#echo = getattr(settings, "db_echo", False) #Todo: Cambiar a True cuando se esté en producción

engine = create_async_engine(
    settings.database_url,
    echo=False,  # Controlado por variable de entorno/configuración
    future=True,
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
