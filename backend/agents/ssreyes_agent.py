# agents/ssreyes_agent.py

"""
Agente específico para San Sebastián de los Reyes - Versión mejorada sin duplicados
"""
import os
import sys
import yaml
from datetime import datetime, date
from typing import Dict, List
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from docling.document_converter import DocumentConverter
from sqlalchemy.orm import Session
from sqlalchemy import and_

from core import get_settings
from core.database import SessionLocal
from core.models import Evento, FuenteWeb


# IMPORTAR EL NORMALIZADOR
from services.event_normalizer import EventNormalizer

settings = get_settings()


class SSReyesAgent:
    """
    Agente específico para extraer eventos de San Sebastián de los Reyes
    VERSIÓN MEJORADA - Sin duplicados
    """

    def __init__(self, fuente_id: int = None, fuente_nombre: str = None):
        # DINÁMICO: Obtener datos de la fuente
        self.fuente_id = fuente_id
        self.fuente_nombre = fuente_nombre
        
        # Si no se proporcionan, obtener de la DB
        if not self.fuente_id or not self.fuente_nombre:
            self._load_fuente_info()

        # Initialize LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model, temperature=0)
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(model=settings.anthropic_model, temperature=0)
        else:
            raise ValueError("Required OPENAI_API_KEY or ANTHROPIC_API_KEY")

        # Load SSReyes specific config
        self.config = self._load_ssreyes_config()
        
        # JSON output parser
        self.json_parser = JsonOutputParser()
        
        # INICIALIZAR NORMALIZADOR
        self.normalizer = EventNormalizer()
        
        # Create prompt template
        self.extraction_prompt = PromptTemplate(
            input_variables=["texto"],
            template=self.config["prompts"]["extraction_prompt"],
        )
    

    def _load_fuente_info(self):
        """Cargar información de la fuente desde la base de datos"""
        db = SessionLocal()
        try:
            # Buscar fuente de tipo SSReyes
            fuente = db.query(FuenteWeb).filter(
                FuenteWeb.nombre.ilike('%reyes%')
            ).first()
            
            if fuente:
                self.fuente_id = fuente.id
                self.fuente_nombre = fuente.nombre
            else:
                # Valores por defecto
                self.fuente_id = 1
                self.fuente_nombre = "San Sebastián de los Reyes"
        finally:
            db.close()


    def _load_ssreyes_config(self) -> Dict:
        """Load SSReyes specific configuration from YAML"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), "prompts", "ssreyes.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("ssreyes.yaml configuration file not found")

    async def extract_events_from_pdf(self, pdf_url: str) -> Dict:
        """
        Extract events from SSReyes PDF using specific instructions
        VERSIÓN MEJORADA - Con detección de duplicados + DEBUG LOGGING
        """
        try:            
            # Step 1: Convert relative path to absolute
            if not os.path.isabs(pdf_url):
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                pdf_absolute_path = os.path.join(backend_dir, pdf_url)
            else:
                pdf_absolute_path = pdf_url
            
            # Step 2: Extract PDF content
            converter = DocumentConverter()
            result = converter.convert(pdf_absolute_path)
            texto = result.document.export_to_markdown()
        
            
            # Step 2: Extract events using LLM with SSReyes specific prompt
            chain = self.extraction_prompt | self.llm | self.json_parser
            response = await chain.ainvoke({"texto": texto})

            
            # Step 3: Process and validate response
            if isinstance(response, dict) and "eventos" in response:
                eventos_raw = response["eventos"]
                
                # Step 4: NORMALIZAR EVENTOS (incluye detección de duplicados)
                mapeo_campos = {
                    "titulo": "titulo",
                    "fecha_inicio": "fecha_inicio",
                    "categoria": "categoria",
                    "precio": "precio",
                    "ubicacion": "ubicacion",
                    "descripcion": "descripcion"
                }
                
                eventos_normalizados = self.normalizer.batch_normalize(eventos_raw, mapeo_campos)
    
                
                # Step 5: Save events to database WITH DEDUPLICATION
                save_result = self.save_eventos_to_db_deduped(eventos_normalizados, pdf_url)

                
                # Add metadata to each event
                for evento in eventos_normalizados:
                    evento["fuente_nombre"] = "San Sebastián de los Reyes"
                    evento["url_original"] = pdf_url
                    evento["fecha_extraccion"] = datetime.now().isoformat()
                    
                    # Ensure enlace_ubicacion is properly formatted
                    if not evento.get("enlace_ubicacion"):
                        ubicacion = evento.get("ubicacion", "Centro Municipal de Personas Mayores Gloria Fuertes San Sebastián de los Reyes")
                        ubicacion_encoded = ubicacion.replace(" ", "+")
                        evento["enlace_ubicacion"] = f"https://www.google.com/maps/search/{ubicacion_encoded}"
                
                
                return {
                    "estado": "success",
                    "eventos_encontrados": len(eventos_raw),
                    "eventos_normalizados": len(eventos_normalizados),
                    "eventos_guardados": save_result['guardados'],
                    "eventos_duplicados": save_result['duplicados'],
                    "eventos": eventos_normalizados,
                    "fuente": "SSReyes",
                    "pdf_url": pdf_url,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"❌ [SSReyes] Invalid response format: {response}")
                return {
                    "estado": "error",
                    "error": "Invalid response format from LLM",
                    "eventos": [],
                    "raw_response": str(response)
                }
                
        except Exception as e:
            print(f"💥 [SSReyes] Error during extraction: {str(e)}")
            return {
                "estado": "error",
                "error": str(e),
                "eventos": [],
                "pdf_url": pdf_url
            }

    def save_eventos_to_db_deduped(self, eventos: List[Dict], pdf_url: str) -> Dict:
        """
        Save events to database WITH DUPLICATE DETECTION
        """
        saved_count = 0
        duplicate_count = 0
        db = SessionLocal()
        
        try:
            for evento_data in eventos:
                # Verificar si ya existe un evento con el mismo hash
                hash_contenido = evento_data.get('hash_contenido')
                
                if hash_contenido:
                    existing_evento = db.query(Evento).filter(
                        Evento.hash_contenido == hash_contenido
                    ).first()
                    
                    if existing_evento:
                        print(f"⚠️ [SSReyes] Duplicate detected: {evento_data['titulo']}")
                        duplicate_count += 1
                        continue
                
                # También verificar por título + fecha + ubicación como backup
                existing_by_content = db.query(Evento).filter(
                    and_(
                        Evento.titulo == evento_data["titulo"],
                        Evento.fecha_inicio == datetime.combine(evento_data["fecha_inicio"], datetime.min.time()),
                        Evento.ubicacion == evento_data.get("ubicacion", "")
                    )
                ).first()
                
                if existing_by_content:
                    print(f"⚠️ [SSReyes] Content duplicate detected: {evento_data['titulo']}")
                    duplicate_count += 1
                    continue
                
                # Crear objeto Evento
                evento = Evento(
                    titulo=evento_data["titulo"],
                    fecha_inicio=datetime.combine(evento_data["fecha_inicio"], datetime.min.time()),
                    categoria=evento_data["categoria"],
                    precio=evento_data["precio"],
                    ubicacion=evento_data.get("ubicacion"),
                    descripcion=evento_data.get("descripcion"),
                    hash_contenido=hash_contenido,
                    fuente_id=self.fuente_id,
                    fuente_nombre=self.fuente_nombre,
                    url_original=pdf_url,
                    datos_extra=evento_data.get("datos_extra"),
                    activo=True
                )
                db.add(evento)
                saved_count += 1
                print(f"✅ [SSReyes] Added new event: {evento_data['titulo']}")
            
            db.commit()
            print(f"✅ [SSReyes] Successfully saved {saved_count} events, skipped {duplicate_count} duplicates")
            return {
                "guardados": saved_count,
                "duplicados": duplicate_count
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ [SSReyes] Error saving to database: {str(e)}")
            raise e
        finally:
            db.close()

    def save_eventos_to_db(self, eventos: List[Dict], pdf_url: str) -> Dict:
        """
        MÉTODO LEGACY - Usar save_eventos_to_db_deduped en su lugar
        Mantenerlo para compatibilidad hacia atrás
        """
        print("⚠️ [SSReyes] Using legacy save method, consider upgrading to deduped version")
        return self.save_eventos_to_db_deduped(eventos, pdf_url)

    def get_config_info(self) -> Dict:
        """Get configuration info for debugging"""
        return {
            "source_name": self.config["source_info"]["name"],
            "domain": self.config["source_info"]["domain"],
            "type": self.config["source_info"]["type"],
            "default_location": self.config["extraction_config"]["default_location"],
            "default_price": self.config["extraction_config"]["default_price"],
            "normalizer_enabled": True,  # Nueva información
            "deduplication_enabled": True
        }
    
    def cleanup_duplicates(self) -> Dict:
        """
        Método de utilidad para limpiar duplicados existentes
        """
        db = SessionLocal()
        try:
            # Buscar eventos con el mismo título, fecha y ubicación
            eventos = db.query(Evento).filter(Evento.fuente_nombre == "San Sebastián de los Reyes").all()
            
            seen_hashes = set()
            duplicates_removed = 0
            
            for evento in eventos:
                # Generar hash si no lo tiene
                if not evento.hash_contenido:
                    key_content = f"{evento.titulo}{evento.fecha_inicio}{evento.ubicacion or ''}"
                    evento.hash_contenido = self.normalizer._generate_hash({"titulo": evento.titulo, "fecha_inicio": str(evento.fecha_inicio), "ubicacion": evento.ubicacion})
                    
                # Si ya vimos este hash, eliminar el duplicado
                if evento.hash_contenido in seen_hashes:
                    db.delete(evento)
                    duplicates_removed += 1
                    print(f"🗑️ [SSReyes] Removed duplicate: {evento.titulo}")
                else:
                    seen_hashes.add(evento.hash_contenido)
            
            db.commit()
            print(f"🧹 [SSReyes] Cleanup completed: removed {duplicates_removed} duplicates")
            
            return {
                "duplicates_removed": duplicates_removed,
                "total_events_processed": len(eventos)
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ [SSReyes] Error during cleanup: {str(e)}")
            raise e
        finally:
            db.close()