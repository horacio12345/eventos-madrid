# api/routes/admin.py

"""
Endpoints simplificados para fuentes específicas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, Depends, HTTPException
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

# Mantener endpoints existentes si los hay...
@router.post("/login")
def login_placeholder():
    """Placeholder - mantener compatibilidad"""
    return {"message": "Login functionality needed"}

@router.get("/fuentes")
def get_fuentes_placeholder():
    """Placeholder - mantener compatibilidad"""
    return []