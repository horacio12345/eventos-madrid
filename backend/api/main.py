# backend/api/main.py

"""
Aplicación principal FastAPI
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Cargar variables de entorno desde .env en la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import admin, eventos, health
from backend.core import create_tables, get_settings
from backend.services.scheduler import start_scheduler, stop_scheduler
from backend.scraping.engine import ScrapingEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    create_tables()
    scraping_engine = ScrapingEngine()
    start_scheduler(scraping_engine=scraping_engine)
    yield
    # Shutdown
    stop_scheduler()


# Configuración
settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para agregación de eventos para mayores en Madrid",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(eventos.router, prefix="/api", tags=["eventos"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
def root():
    """Endpoint raíz"""
    return {"message": "API Eventos Mayores Madrid", "docs": "/docs"}
