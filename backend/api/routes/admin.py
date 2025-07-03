# api/routes/admin.py

"""
Endpoints simplificados para fuentes específicas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core import get_db
from core.models import FuenteWeb
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents.ssreyes_agent import SSReyesAgent

router = APIRouter()

@router.post("/ssreyes/extract")
async def extract_ssreyes_events(request: dict):
    """
    Extract events specifically from SSReyes PDF
    """
    try:
        pdf_url = request.get("pdf_url")
        if not pdf_url:
            raise HTTPException(status_code=400, detail="pdf_url is required")
        
        print(f"🚀 [ADMIN] Starting SSReyes extraction for: {pdf_url}")
        
        # Use specific SSReyes agent
        agent = SSReyesAgent()
        result = await agent.extract_events_from_pdf(pdf_url)
        
        print(f"✅ [ADMIN] SSReyes extraction completed: {result['estado']}")
        
        return result
        
    except Exception as e:
        print(f"💥 [ADMIN] SSReyes extraction failed: {str(e)}")
        return {
            "estado": "error",
            "error": str(e),
            "eventos": []
        }

@router.get("/ssreyes/config")
async def get_ssreyes_config():
    """
    Get SSReyes agent configuration for debugging
    """
    try:
        agent = SSReyesAgent()
        return agent.get_config_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= FUENTES CRUD =============

@router.get("/fuentes")
def get_fuentes(db: Session = Depends(get_db)):
    """Obtener todas las fuentes configuradas"""
    fuentes = db.query(FuenteWeb).all()
    return [
        {
            "id": f.id,
            "nombre": f.nombre,
            "url": f.url,
            "tipo": f.tipo,
            "activa": f.activa,
            "frecuencia_actualizacion": f.frecuencia_actualizacion,
            "ultima_ejecucion": f.ultima_ejecucion,
            "ultimo_estado": f.ultimo_estado,
            "eventos_encontrados_ultima_ejecucion": f.eventos_encontrados_ultima_ejecucion or 0
        }
        for f in fuentes
    ]

@router.post("/fuentes")
def create_fuente(request: dict, db: Session = Depends(get_db)):
    """Crear nueva fuente"""
    try:
        fuente = FuenteWeb(
            nombre=request["nombre"],
            url=request["url"],
            tipo=request["tipo"],
            activa=request.get("activa", False),
            frecuencia_actualizacion=request.get("frecuencia_actualizacion", "0 9 * * 1"),
            ultimo_estado="pending"
        )
        db.add(fuente)
        db.commit()
        db.refresh(fuente)
        
        return {"id": fuente.id, "message": "Fuente creada exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============= AUTH =============

@router.post("/login")
def login_placeholder():
    """Placeholder - mantener compatibilidad"""
    return {"message": "Login functionality needed"}