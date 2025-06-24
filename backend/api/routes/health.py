# api/routes/health.py

"""
Endpoints de health check
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import get_db, get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check básico
    """
    try:
        # Test conexión a base de datos
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok" if db_status == "ok" else "error",
        "timestamp": datetime.now().isoformat(),
        "app_name": settings.app_name,
        "database": db_status
    }