# backend/core/config.py

"""
Configuración global del proyecto usando Pydantic Settings
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración principal de la aplicación"""
    
    # ============= APP =============
    app_name: str = "Eventos Mayores Madrid"
    debug: bool = False
    
    # ============= BASE DE DATOS =============
    database_url: str = "sqlite:///./database.db"
    
    # ============= SEGURIDAD =============
    secret_key: str = Field(..., min_length=32)
    admin_username: str = "admin"
    admin_password: str = Field(..., min_length=6)
    
    # ============= APIS IA =============
    openai_api_key: str = Field(...)
    openai_model: str = "gpt-4o-mini"
    
    # ============= SCRAPING =============
    request_timeout: int = 30
    max_retries: int = 3
    playwright_headless: bool = True
    
    # ============= SCHEDULER =============
    scheduler_timezone: str = "Europe/Madrid"
    default_update_frequency: str = "0 9 * * 1"  # Lunes 9:00
    
    # ============= CORS =============
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Singleton para obtener configuración"""
    return Settings()