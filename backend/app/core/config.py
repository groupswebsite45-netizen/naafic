from functools import lru_cache
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    APP_NAME: str = "Education Management System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:123@localhost:5432/hawlwadaag_school_db"

    JWT_SECRET: str = "hawlwadaag_super_secret_jwt_key_change_in_production_2026_xyz"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    INITIAL_ADMIN_EMAIL: str = "admin@hawlwadaagschool.edu.so"
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_PASSWORD: str = "Admin@Hawlwadaag2026"
    INITIAL_ADMIN_FULL_NAME: str = "System Administrator"

    # Hormuud SMS REST API Configuration
    HORMUUD_SMS_BASE_URL: str = "https://smsapi.hormuud.com"
    HORMUUD_SMS_USERNAME: str = ""
    HORMUUD_SMS_PASSWORD: str = ""
    HORMUUD_SMS_SENDER_ID: str = "EMS"
    HORMUUD_SMS_ENABLED: bool = False
    HORMUUD_WEBHOOK_SECRET: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
