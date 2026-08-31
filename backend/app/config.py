from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://drishtimail_app:change-me-for-local-use@localhost:5432/drishtimail"
    redis_url: str = "redis://localhost:6379/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "drishtimail"
    minio_secret_key: str = "change-me-for-local-use"
    minio_bucket: str = "evidence-originals"
    jwt_secret: str = "replace-this-development-secret"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    api_prefix: str = "/api/v1"


settings = Settings()
