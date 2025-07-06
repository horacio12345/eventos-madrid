# api/routes/admin.py

"""
Endpoints simplificados para fuentes específicas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from core import get_db
from core.models import FuenteWeb, Evento, LogScraping
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents.ssreyes_agent import SSReyesAgent
from fastapi import UploadFile, File, Form


router = APIRouter()

@router.post("/ssreyes/extract")
async def extract_ssreyes_events(request: dict):
    """
    Extract events specifically from SSReyes PDF
    """
    try:
        pdf_relative_path = request.get("pdf_url")
        if not pdf_relative_path:
            raise HTTPException(status_code=400, detail="pdf_url is required")

        # Construir la ruta absoluta para asegurar que el fichero se encuentre.
        # La ruta relativa viene de `data/uploads/...`
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_absolute_path = os.path.join(backend_dir, pdf_relative_path)

        if not os.path.exists(pdf_absolute_path):
            raise HTTPException(status_code=404, detail=f"El fichero no se encontró en la ruta: {pdf_absolute_path}")

        print(f"🚀 [ADMIN] Starting SSReyes extraction for: {pdf_absolute_path}")
        
        # Use specific SSReyes agent
        agent = SSReyesAgent()
        result = await agent.extract_events_from_pdf(pdf_absolute_path)
        
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


    # ============= UPLOAD =============

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    agent_type: str = Form(...)
):
    """
    Subir archivo para procesamiento por agente específico
    """
    try:
        # Validar tipo de archivo
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        # Usar el directorio data/uploads para persistencia
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(backend_dir, "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Crear un nombre de archivo único con timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{agent_type}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Devolver la ruta relativa para que el frontend la use
        relative_path = os.path.join("data", "uploads", unique_filename)

        return {
            "message": "Archivo subido exitosamente",
            "file_path": relative_path,
            "agent_type": agent_type,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/fuentes/{fuente_id}")
def delete_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """Eliminar una fuente por ID"""
    try:
        fuente = db.query(FuenteWeb).filter(FuenteWeb.id == fuente_id).first()
        if not fuente:
            raise HTTPException(status_code=404, detail="Fuente no encontrada")
        
        db.delete(fuente)
        db.commit()
        
        return {"message": "Fuente eliminada exitosamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ============= GESTIÓN DE ARCHIVOS SUBIDOS =============

@router.get("/uploads/{agent_name}")
def get_uploaded_files(agent_name: str):
    """Listar archivos subidos para un agente específico."""
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(backend_dir, "data", "uploads")
        
        if not os.path.exists(upload_dir):
            return []

        # Filtrar archivos que pertenecen al agente
        files = [
            f for f in os.listdir(upload_dir) 
            if f.startswith(f"_{agent_name}_") or f.split('_', 1)[1].startswith(f"{agent_name}_")
        ]
        
        return sorted(files, reverse=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando archivos: {str(e)}")


@router.delete("/upload/{filename}")
def delete_uploaded_file(filename: str, db: Session = Depends(get_db)):
    """
    Eliminar un archivo subido y todos los eventos asociados a él.
    """
    try:
        # Construir la ruta absoluta al archivo
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(backend_dir, "data", "uploads", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="El archivo no fue encontrado en el servidor.")

        # 1. Borrar eventos de la DB asociados a este archivo
        # La `url_original` se guardó como una ruta absoluta, necesitamos la parte final.
        # O mejor, construimos la ruta relativa que se guardó.
        relative_path = os.path.join("data", "uploads", filename)
        
        # Buscamos eventos que contengan esta ruta relativa.
        eventos_a_borrar = db.query(Evento).filter(Evento.url_original.contains(relative_path)).all()
        
        count = len(eventos_a_borrar)
        if count > 0:
            db.query(Evento).filter(Evento.url_original.contains(relative_path)).delete(synchronize_session=False)
        
        # 2. Borrar el archivo físico del disco
        os.remove(file_path)
        
        db.commit()
        
        return {"message": f"Archivo '{filename}' y {count} eventos asociados eliminados exitosamente."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminando el archivo: {str(e)}")

# ============= LOGS =============

@router.get("/logs")
def get_logs(fuente_id: int = None, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener los logs de scraping, con filtro opcional por fuente."""
    try:
        query = db.query(LogsScraping).order_by(LogsScraping.fecha_inicio.desc())
        
        if fuente_id:
            query = query.filter(LogsScraping.fuente_id == fuente_id)
            
        logs = query.limit(limit).all()
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs: {str(e)}")




# Añadir estos endpoints al final de backend/api/routes/admin.py

@router.post("/ssreyes/cleanup-duplicates")
async def cleanup_ssreyes_duplicates():
    """
    Limpiar duplicados existentes del agente SSReyes
    """
    try:
        print("🧹 [ADMIN] Starting SSReyes duplicates cleanup...")
        
        agent = SSReyesAgent()
        result = agent.cleanup_duplicates()
        
        print(f"✅ [ADMIN] Cleanup completed: {result}")
        
        return {
            "estado": "success",
            "duplicates_removed": result['duplicates_removed'],
            "total_events_processed": result['total_events_processed'],
            "message": f"Se eliminaron {result['duplicates_removed']} eventos duplicados"
        }
        
    except Exception as e:
        print(f"💥 [ADMIN] Cleanup failed: {str(e)}")
        return {
            "estado": "error",
            "error": str(e),
            "duplicates_removed": 0
        }

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas del sistema para debugging
    """
    try:
        from sqlalchemy import func, distinct
        
        # Estadísticas generales
        total_eventos = db.query(func.count(Evento.id)).scalar()
        eventos_activos = db.query(func.count(Evento.id)).filter(Evento.activo == True).scalar()
        
        # Estadísticas por fuente
        eventos_por_fuente = db.query(
            Evento.fuente_nombre,
            func.count(Evento.id).label('total')
        ).group_by(Evento.fuente_nombre).all()
        
        # Detectar posibles duplicados
        duplicados_potenciales = db.query(
            Evento.titulo,
            Evento.fecha_inicio,
            func.count(Evento.id).label('count')
        ).group_by(
            Evento.titulo, 
            Evento.fecha_inicio
        ).having(func.count(Evento.id) > 1).all()
        
        # Eventos sin hash
        eventos_sin_hash = db.query(func.count(Evento.id)).filter(
            Evento.hash_contenido.is_(None)
        ).scalar()
        
        return {
            "total_eventos": total_eventos,
            "eventos_activos": eventos_activos,
            "eventos_por_fuente": [
                {"fuente": fuente, "total": total} 
                for fuente, total in eventos_por_fuente
            ],
            "duplicados_potenciales": len(duplicados_potenciales),
            "eventos_sin_hash": eventos_sin_hash,
            "duplicados_detalle": [
                {
                    "titulo": titulo,
                    "fecha": str(fecha),
                    "count": count
                }
                for titulo, fecha, count in duplicados_potenciales[:10]  # Solo primeros 10
            ] if duplicados_potenciales else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fix-hashes")
def fix_missing_hashes(db: Session = Depends(get_db)):
    """
    Generar hashes faltantes para eventos existentes
    """
    try:
        from services.event_normalizer import EventNormalizer
        import hashlib
        
        normalizer = EventNormalizer()
        
        # Buscar eventos sin hash
        eventos_sin_hash = db.query(Evento).filter(
            Evento.hash_contenido.is_(None)
        ).all()
        
        updated_count = 0
        
        for evento in eventos_sin_hash:
            # Generar hash
            key_content = f"{evento.titulo}{evento.fecha_inicio}{evento.ubicacion or ''}"
            hash_contenido = hashlib.sha256(key_content.encode("utf-8")).hexdigest()
            
            evento.hash_contenido = hash_contenido
            updated_count += 1
        
        db.commit()
        
        return {
            "estado": "success",
            "eventos_actualizados": updated_count,
            "message": f"Se generaron hashes para {updated_count} eventos"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))