# backend/api/routes/admin.py

"""
Endpoints de administración con autenticación
"""

import hashlib
import traceback  # <--- AÑADIR IMPORT
from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.core import get_db, get_settings
from backend.core.models import FuenteWeb, LogScraping
from backend.scraping.engine import ScrapingEngine

router = APIRouter()
settings = get_settings()

# Configuración de seguridad
security = HTTPBearer()


def verify_password(plain_password: str, stored_password: str) -> bool:
    """Verificar contraseña simple"""
    return plain_password == stored_password


def create_access_token(data: dict) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verificar token JWT"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
            )
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )


@router.post("/login")
def login(username: str, password: str):
    """
    Login de administrador
    """
    if username != settings.admin_username or password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas"
        )

    access_token = create_access_token(data={"sub": username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.get("/fuentes")
def get_fuentes(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    """
    Obtener lista de fuentes configuradas
    """
    fuentes = db.query(FuenteWeb).all()

    return [
        {
            "id": fuente.id,
            "nombre": fuente.nombre,
            "url": fuente.url,
            "tipo": fuente.tipo,
            "activa": fuente.activa,
            "ultima_ejecucion": (
                fuente.ultima_ejecucion.isoformat() if fuente.ultima_ejecucion else None
            ),
            "ultimo_estado": fuente.ultimo_estado,
            "eventos_encontrados_ultima_ejecucion": fuente.eventos_encontrados_ultima_ejecucion,
            "frecuencia_actualizacion": fuente.frecuencia_actualizacion,
            "fecha_creacion": fuente.fecha_creacion.isoformat(),
        }
        for fuente in fuentes
    ]


@router.post("/fuentes")
def create_fuente(
    fuente_data: dict,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Crear nueva fuente web
    """
    # Validar que no existe una fuente con el mismo nombre
    existing = (
        db.query(FuenteWeb).filter(FuenteWeb.nombre == fuente_data["nombre"]).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una fuente con ese nombre",
        )

    fuente = FuenteWeb(
        nombre=fuente_data["nombre"],
        url=fuente_data["url"],
        tipo=fuente_data["tipo"],
        schema_extraccion=fuente_data.get("schema_extraccion", {}),
        mapeo_campos=fuente_data.get("mapeo_campos", {}),
        configuracion_scraping=fuente_data.get("configuracion_scraping", {}),
        frecuencia_actualizacion=fuente_data.get(
            "frecuencia_actualizacion", settings.default_update_frequency
        ),
        activa=fuente_data.get("activa", True),
        creado_por=current_user,
    )

    db.add(fuente)
    db.commit()
    db.refresh(fuente)

    return {"id": fuente.id, "message": "Fuente creada correctamente"}


@router.put("/fuentes/{fuente_id}")
def update_fuente(
    fuente_id: int,
    fuente_data: dict,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Actualizar fuente existente
    """
    fuente = db.query(FuenteWeb).filter(FuenteWeb.id == fuente_id).first()
    if not fuente:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    # Actualizar campos
    for key, value in fuente_data.items():
        if hasattr(fuente, key):
            setattr(fuente, key, value)

    db.commit()
    return {"message": "Fuente actualizada correctamente"}


@router.delete("/fuentes/{fuente_id}")
def delete_fuente(
    fuente_id: int,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Eliminar fuente
    """
    fuente = db.query(FuenteWeb).filter(FuenteWeb.id == fuente_id).first()
    if not fuente:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    db.delete(fuente)
    db.commit()
    return {"message": "Fuente eliminada correctamente"}


@router.post("/execute-scraping")
async def execute_real_scraping(
    test_data: dict, 
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    EJECUTAR SCRAPING REAL CON PIPELINE COMPLETO DE AGENTES
    """
    print("="*50)
    print(f"🚀 [ADMIN] INICIANDO TEST DE SCRAPING. Datos recibidos:")
    print(test_data)
    print("="*50)
    
    try:
        # Obtener URL y configuración
        url = test_data.get("url", "")
        tipo = test_data.get("tipo", "HTML")
        
        if not url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL es requerida para el test",
            )
        
        # INICIALIZAR EL SCRAPING ENGINE REAL
        print(f"🔧 [ADMIN] Initializing ScrapingEngine...")
        scraping_engine = ScrapingEngine()
        
        # EJECUTAR EL TEST REAL CON AGENTES
        print(f"🎯 [ADMIN] Executing real agent pipeline for URL: {url}")
        
        configuracion_test = {
            "url": url,
            "tipo": tipo,
            "schema_extraccion": test_data.get("schema_extraccion", {}),
            "mapeo_campos": test_data.get("mapeo_campos", {}),
            "configuracion_scraping": test_data.get("configuracion_scraping", {})
        }
        
        # ESTO EJECUTA EL PIPELINE COMPLETO
        result = await scraping_engine.test_fuente(configuracion_test)
        
        print(f"✅ [ADMIN] Test de scraping completado. Resultado:")
        print(result)
        print("="*50)
        
        return result
        
    except Exception as e:
        print(f"💥 [ADMIN] ERROR CATASTRÓFICO EN /execute-scraping:")
        traceback.print_exc()  # Imprimir el traceback completo
        print("="*50)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ejecutando pipeline: {str(e)}"
        )


@router.post("/trigger-update")
async def trigger_update(
    request_data: dict = {},
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    EJECUTAR SCRAPING REAL PARA UNA FUENTE O TODAS
    """
    fuente_id = request_data.get("fuente_id") if request_data else None
    print(f"🚀 [ADMIN] Triggering real scraping update. Fuente ID: {fuente_id}")
    
    try:
        # INICIALIZAR EL SCRAPING ENGINE REAL
        scraping_engine = ScrapingEngine()
        
        # EJECUTAR SCRAPING REAL
        if fuente_id:
            print(f"🎯 [ADMIN] Executing scraping for specific source: {fuente_id}")
            resultado = await scraping_engine.execute_scraping(fuente_id)
        else:
            print(f"🎯 [ADMIN] Executing scraping for ALL active sources")
            resultado = await scraping_engine.execute_scraping()
        
        print(f"✅ [ADMIN] Scraping execution completed: {resultado}")
        
        return {
            "message": "Scraping ejecutado correctamente",
            "resultado": resultado
        }
        
    except Exception as e:
        error_msg = f"Error en trigger update: {str(e)}"
        print(f"💥 [ADMIN] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/logs")
def get_logs(
    fuente_id: Optional[int] = None,
    limite: int = 50,
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    Obtener logs de scraping
    """
    query = db.query(LogScraping)

    if fuente_id:
        query = query.filter(LogScraping.fuente_id == fuente_id)

    logs = query.order_by(LogScraping.fecha_inicio.desc()).limit(limite).all()

    return [
        {
            "id": log.id,
            "fuente_id": log.fuente_id,
            "fuente_nombre": log.fuente_nombre,
            "fecha_inicio": log.fecha_inicio.isoformat(),
            "fecha_fin": log.fecha_fin.isoformat() if log.fecha_fin else None,
            "estado": log.estado,
            "eventos_extraidos": log.eventos_extraidos,
            "eventos_nuevos": log.eventos_nuevos,
            "eventos_actualizados": log.eventos_actualizados,
            "tiempo_ejecucion_segundos": log.tiempo_ejecucion_segundos,
            "mensaje": log.mensaje,
            "detalles_error": log.detalles_error,
        }
        for log in logs
    ]
