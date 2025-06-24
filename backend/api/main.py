# backend/api/main.py

"""
Aplicación principal FastAPI
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core import get_settings, create_tables
from .routes import eventos, admin, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    create_tables()
    yield
    # Shutdown (si necesario en el futuro)


# Configuración
settings = get_settings()

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para agregación de eventos para mayores en Madrid",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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