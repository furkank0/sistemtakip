from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_version: str = "0.1.0"
    app_secret_key: str = "development-only-change-me"
    # Local development works without Docker; Compose overrides this with PostgreSQL.
    database_url: str = "sqlite:///./sistemtakip.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
