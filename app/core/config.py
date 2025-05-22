from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field

class Settings(BaseSettings):
    """
    Settings for the application.
    """
    # Database
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="postgres")
    db_host: str = Field(default="db")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="app_db")

    # Redis
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)

    # Application
    app_port: int = Field(default=8000)
    secret_key: SecretStr = Field(default="your-secret-key")
    cors_origins: list[str] = Field(default=["http://localhost", "http://localhost:3000", "http://localhost:8080"])

    # Environment
    debug: bool = Field(default=True)
    environment: str = Field(default="development")

    # Superadmin
    superadmin_email: str = Field(default="admin@example.com")
    superadmin_password: str = Field(default="supersecret")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()
