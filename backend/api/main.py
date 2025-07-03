# api/main.py

"""
Servidor FastAPI simplificado para Eventos Mayores Madrid
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import admin, eventos
from core import get_settings, create_tables

# Configuración
settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title="Eventos Mayores Madrid API",
    description="API simplificada para eventos específicos por fuente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo, permitir todo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al iniciar
create_tables()

# Incluir routers
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(eventos.router, prefix="/api", tags=["eventos"])

@app.get("/")
def root():
    """Endpoint raíz"""
    return {"message": "Eventos Mayores Madrid API - Versión Simplificada", "docs": "/docs"}

@app.get("/api/health")
def health_check():
    """Health check básico"""
    return {
        "status": "ok",
        "message": "API funcionando correctamente",
        "app": settings.app_name
    }