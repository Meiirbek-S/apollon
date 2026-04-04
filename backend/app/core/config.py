from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Apollon API"
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_db: str = "apollon"
    postgres_user: str = "apollon"
    postgres_password: str = "apollon_pass"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    minio_host: str = "minio"
    minio_port: int = 9000
    minio_bucket: str = "samples"


settings = Settings()
