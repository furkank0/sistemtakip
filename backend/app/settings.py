from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_version: str = "0.1.0"
    app_secret_key: str = "development-only-change-me"
    database_url: str = "postgresql+psycopg://sistemtakip:sistemtakip@localhost:5432/sistemtakip"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
