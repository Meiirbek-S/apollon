from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AegisScan API"
    app_version: str = "0.2.0"
    api_prefix: str = "/api/v1"

    postgres_dsn: str = Field(default="postgresql+psycopg://aegis:aegis@db:5432/aegisscan")
    redis_url: str = Field(default="redis://redis:6379/0")
    storage_dir: str = Field(default="/data/storage")

    upload_max_mb: int = 20
    dynamic_timeout_seconds: int = 180
    vm_name: str = "WinSandbox"
    vm_snapshot: str = "CleanState"

    jwt_secret: str = Field(default="change-me")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_prefix="AEGIS_")


settings = Settings()
