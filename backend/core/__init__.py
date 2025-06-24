# core/__init__.py

"""
Módulo core - Configuración base del proyecto
"""
from .config import get_settings
from .database import Base, SessionLocal, engine, get_db, create_tables, drop_tables
from .models import Evento, FuenteWeb, LogScraping, Configuracion