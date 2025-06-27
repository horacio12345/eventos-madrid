# backend/core/__init__.py

"""
Módulo core - Configuración base del proyecto
"""
from .config import get_settings
from .database import (Base, SessionLocal, create_tables, drop_tables, engine,
                       get_db)
from .models import Configuracion, Evento, FuenteWeb, LogScraping
