# backend/scraping/engine.py

"""
Motor principal de scraping - Orquestador de extracción
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.core import get_db, get_settings
from backend.core.models import FuenteWeb, LogScraping, Evento
from .pipelines.langgraph_pipeline import ScrapingPipeline
from .extractors.html_extractor import HTMLExtractor
from .extractors.pdf_extractor import PDFExtractor
from .extractors.image_extractor import ImageExtractor

settings = get_settings()


class ScrapingEngine:
    """
    Motor principal de scraping que coordina la extracción de todas las fuentes
    """
    
    def __init__(self):
        self.pipeline = ScrapingPipeline()
        self.extractors = {
            "HTML": HTMLExtractor(),
            "PDF": PDFExtractor(),
            "IMAGE": ImageExtractor()
        }
    
    async def execute_scraping(self, fuente_id: Optional[int] = None) -> Dict:
        """
        Ejecutar scraping para una fuente específica o todas las activas
        """
        results = {"total_ejecutadas": 0, "exitosas": 0, "errores": 0, "detalles": []}
        
        # Obtener fuentes a procesar
        db = next(get_db())
        try:
            if fuente_id:
                fuentes = db.query(FuenteWeb).filter(
                    FuenteWeb.id == fuente_id,
                    FuenteWeb.activa == True
                ).all()
            else:
                fuentes = db.query(FuenteWeb).filter(FuenteWeb.activa == True).all()
        finally:
            db.close()
        
        # Procesar cada fuente
        for fuente in fuentes:
            resultado = await self._procesar_fuente(fuente)
            results["total_ejecutadas"] += 1
            if resultado["estado"] == "success":
                results["exitosas"] += 1
            else:
                results["errores"] += 1
            results["detalles"].append(resultado)
        
        return results
    
    async def _procesar_fuente(self, fuente: FuenteWeb) -> Dict:
        """
        Procesar una fuente individual
        """
        inicio_tiempo = datetime.now()
        
        # Crear log de inicio
        db = next(get_db())
        try:
            log = LogScraping(
                fuente_id=fuente.id,
                fuente_nombre=fuente.nombre,
                fecha_inicio=inicio_tiempo,
                estado="running"
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            log_id = log.id
        finally:
            db.close()
        
        try:
            # Ejecutar pipeline de extracción
            resultado = await self.pipeline.run(
                url=fuente.url,
                tipo=fuente.tipo,
                schema_extraccion=fuente.schema_extraccion,
                mapeo_campos=fuente.mapeo_campos,
                configuracion_scraping=fuente.configuracion_scraping
            )
            
            # Procesar eventos extraídos
            eventos_procesados = await self._procesar_eventos(
                resultado["eventos"],
                fuente,
                db
            )
            
            # Actualizar fuente
            fuente.ultima_ejecucion = datetime.now()
            fuente.ultimo_estado = "success"
            fuente.eventos_encontrados_ultima_ejecucion = len(eventos_procesados["nuevos"]) + len(eventos_procesados["actualizados"])
            
            # Finalizar log exitoso
            tiempo_transcurrido = (datetime.now() - inicio_tiempo).total_seconds()
            self._finalizar_log(
                log_id, "success", eventos_procesados, tiempo_transcurrido, db
            )
            
            return {
                "fuente_id": fuente.id,
                "fuente_nombre": fuente.nombre,
                "estado": "success",
                "eventos_nuevos": len(eventos_procesados["nuevos"]),
                "eventos_actualizados": len(eventos_procesados["actualizados"]),
                "tiempo_segundos": tiempo_transcurrido
            }
            
        except Exception as e:
            # Manejar error
            tiempo_transcurrido = (datetime.now() - inicio_tiempo).total_seconds()
            error_msg = str(e)
            
            # Actualizar fuente con error
            db = next(get_db())
            try:
                fuente.ultima_ejecucion = datetime.now()
                fuente.ultimo_estado = "error"
                fuente.ultimo_error = error_msg
                
                # Finalizar log con error
                self._finalizar_log(
                    log_id, "error", {"nuevos": [], "actualizados": []}, 
                    tiempo_transcurrido, db, error_msg
                )
                db.commit()
            finally:
                db.close()
            
            return {
                "fuente_id": fuente.id,
                "fuente_nombre": fuente.nombre,
                "estado": "error",
                "error": error_msg,
                "tiempo_segundos": tiempo_transcurrido
            }
    
    async def _procesar_eventos(self, eventos_raw: List[Dict], fuente: FuenteWeb, db: Session) -> Dict:
        """
        Procesar eventos extraídos y guardar en base de datos
        """
        eventos_nuevos = []
        eventos_actualizados = []
        
        for evento_data in eventos_raw:
            # Generar hash para detectar duplicados
            contenido_hash = self._generar_hash_evento(evento_data)
            
            # Buscar evento existente
            evento_existente = db.query(Evento).filter(
                Evento.hash_contenido == contenido_hash,
                Evento.fuente_id == fuente.id
            ).first()
            
            if evento_existente:
                # Actualizar evento existente
                self._actualizar_evento(evento_existente, evento_data)
                eventos_actualizados.append(evento_existente)
            else:
                # Crear nuevo evento
                nuevo_evento = self._crear_evento(evento_data, fuente, contenido_hash)
                db.add(nuevo_evento)
                eventos_nuevos.append(nuevo_evento)
        
        db.commit()
        
        return {
            "nuevos": eventos_nuevos,
            "actualizados": eventos_actualizados
        }
    
    def _generar_hash_evento(self, evento_data: Dict) -> str:
        """
        Generar hash único para un evento basado en contenido clave
        """
        import hashlib
        
        # Usar campos clave para generar hash
        contenido_clave = f"{evento_data.get('titulo', '')}{evento_data.get('fecha_inicio', '')}{evento_data.get('ubicacion', '')}"
        return hashlib.sha256(contenido_clave.encode()).hexdigest()
    
    def _crear_evento(self, evento_data: Dict, fuente: FuenteWeb, hash_contenido: str) -> Evento:
        """
        Crear nuevo evento desde datos extraídos
        """
        return Evento(
            titulo=evento_data.get("titulo"),
            fecha_inicio=evento_data.get("fecha_inicio"),
            fecha_fin=evento_data.get("fecha_fin"),
            categoria=evento_data.get("categoria", "Ocio y Social"),
            precio=evento_data.get("precio", "Gratis"),
            ubicacion=evento_data.get("ubicacion"),
            descripcion=evento_data.get("descripcion"),
            fuente_id=fuente.id,
            fuente_nombre=fuente.nombre,
            url_original=evento_data.get("url_original"),
            hash_contenido=hash_contenido,
            datos_extra=evento_data.get("datos_extra", {}),
            datos_raw=evento_data
        )
    
    def _actualizar_evento(self, evento: Evento, evento_data: Dict) -> None:
        """
        Actualizar evento existente con nuevos datos
        """
        evento.titulo = evento_data.get("titulo", evento.titulo)
        evento.precio = evento_data.get("precio", evento.precio)
        evento.ubicacion = evento_data.get("ubicacion", evento.ubicacion)
        evento.descripcion = evento_data.get("descripcion", evento.descripcion)
        evento.datos_extra = evento_data.get("datos_extra", evento.datos_extra)
        evento.datos_raw = evento_data
        evento.ultima_actualizacion = datetime.now()
    
    def _finalizar_log(self, log_id: int, estado: str, eventos: Dict, 
                      tiempo_segundos: float, db: Session, error: str = None) -> None:
        """
        Finalizar log de scraping
        """
        log = db.query(LogScraping).filter(LogScraping.id == log_id).first()
        if log:
            log.fecha_fin = datetime.now()
            log.estado = estado
            log.eventos_extraidos = len(eventos["nuevos"]) + len(eventos["actualizados"])
            log.eventos_nuevos = len(eventos["nuevos"])
            log.eventos_actualizados = len(eventos["actualizados"])
            log.tiempo_ejecucion_segundos = int(tiempo_segundos)
            if error:
                log.detalles_error = error
            db.commit()
    
    async def test_fuente(self, configuracion_test: Dict) -> Dict:
        """
        Testear una configuración de fuente sin guardar datos
        """
        try:
            resultado = await self.pipeline.run(
                url=configuracion_test["url"],
                tipo=configuracion_test["tipo"],
                schema_extraccion=configuracion_test.get("schema_extraccion", {}),
                mapeo_campos=configuracion_test.get("mapeo_campos", {}),
                configuracion_scraping=configuracion_test.get("configuracion_scraping", {})
            )
            
            return {
                "estado": "success",
                "eventos_encontrados": len(resultado["eventos"]),
                "preview_eventos": resultado["eventos"][:3],  # Solo primeros 3
                "tiempo_ejecucion": resultado.get("tiempo_ejecucion", 0),
                "errores": []
            }
            
        except Exception as e:
            return {
                "estado": "error",
                "error": str(e),
                "eventos_encontrados": 0,
                "preview_eventos": [],
                "errores": [str(e)]
            }