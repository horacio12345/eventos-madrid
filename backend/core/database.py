# backend/core/database.py

"""
Configuración de base de datos SQLite con SQLAlchemy 2.0
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

settings = get_settings()

# ============= ENGINE SQLite =============
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Mostrar SQL en desarrollo
    pool_pre_ping=True,  # Verificar conexión antes de usar
)

# ============= SESSION FACTORY =============
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============= BASE PARA MODELOS =============
Base = declarative_base()


# ============= DEPENDENCIA PARA FASTAPI =============
def get_db() -> Session:
    """
    Dependencia de FastAPI para obtener sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============= FUNCIONES DE INICIALIZACIÓN =============
def create_tables() -> None:
    """
    Crear todas las tablas en la base de datos
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Eliminar todas las tablas (útil para testing)
    """
    Base.metadata.drop_all(bind=engine)
