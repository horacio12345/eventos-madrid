# backend/core/config.py

"""
Configuración global del proyecto usando Pydantic Settings
"""
import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""

    # ============= APP =============
    app_name: str = "Eventos Mayores Madrid"
    debug: bool = False
    environment: str = "production"

    # ============= BASE DE DATOS =============
    database_url: str = "sqlite:///./data/database.db"

    # ============= SEGURIDAD =============
    secret_key: str = Field(..., min_length=32)
    admin_username: str = "admin"
    admin_password: str = Field(..., min_length=6)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 horas

    # ============= APIS IA =============
    openai_api_key: str = Field(...)
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = "claude-3-haiku-20240307"

    # ============= SCRAPING =============
    request_timeout: int = 120
    max_retries: int = 3
    playwright_headless: bool = True
    playwright_timeout: int = 150000

    # ============= SCHEDULER =============
    scheduler_timezone: str = "Europe/Madrid"
    default_update_frequency: str = "0 9 * * 1"  # Lunes 9:00

    # ============= CORS =============
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        # Construir la ruta absoluta al fichero .env en la raíz del proyecto
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_file = os.path.join(project_root, ".env")


@lru_cache()
def get_settings() -> Settings:
    """Singleton para obtener configuración"""
    return Settings()
