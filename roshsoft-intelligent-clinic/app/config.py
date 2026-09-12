from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Roshsoft Intelligent Clinic"
    secret_key: str = "development-only-change-me"
    database_url: str = "sqlite:///./clinic.db"
    session_https_only: bool = False
    clinic_name: str = "Roshsoft Free Clinic"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

