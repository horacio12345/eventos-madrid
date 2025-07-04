# agents/ssreyes_agent.py

"""
Agente específico para San Sebastián de los Reyes - Versión simplificada
"""
import json
import os
import sys
import yaml
from datetime import datetime
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from docling.document_converter import DocumentConverter

from core import get_settings

settings = get_settings()


class SSReyesAgent:
    """
    Agente específico para extraer eventos de San Sebastián de los Reyes
    """

    def __init__(self):
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
        
        # Create prompt template
        self.extraction_prompt = PromptTemplate(
            input_variables=["texto"],
            template=self.config["prompts"]["extraction_prompt"],
        )

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
        """
        try:
            print(f"🔍 [SSReyes] Starting extraction from: {pdf_url}")
            
            # Step 1: Extract PDF content
            converter = DocumentConverter()
            result = converter.convert(pdf_url)
            texto = result.document.export_to_markdown()
            
            print(f"📄 [SSReyes] PDF content extracted, length: {len(texto)}")
            
            # Step 2: Extract events using LLM with SSReyes specific prompt
            chain = self.extraction_prompt | self.llm | self.json_parser
            
            response = await chain.ainvoke({"texto": texto})
            
            # Step 3: Process and validate response
            if isinstance(response, dict) and "eventos" in response:
                eventos = response["eventos"]
                print(f"✅ [SSReyes] Extracted {len(eventos)} events")
                
                # Step 4: Save events to database
                save_result = self.save_eventos_to_db(eventos, pdf_url)
                print(f"💾 [SSReyes] Saved {save_result['guardados']} events to database")
                
                # Add metadata to each event
                for evento in eventos:
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
                    "eventos_encontrados": len(eventos),
                    "eventos_guardados": save_result['guardados'],
                    "eventos": eventos,
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

    def save_eventos_to_db(self, eventos: List[Dict], pdf_url: str) -> Dict:
        """Save events to database"""
        from core.database import SessionLocal
        from core.models import Evento
        
        saved_count = 0
        db = SessionLocal()
        
        try:
            for evento_data in eventos:
                # Crear objeto Evento
                evento = Evento(
                    titulo=evento_data["titulo"],
                    fecha_inicio=datetime.strptime(evento_data["fecha_inicio"], "%Y-%m-%d").date(),
                    categoria=evento_data["categoria"],
                    precio=evento_data["precio"],
                    ubicacion=evento_data["ubicacion"],
                    descripcion=evento_data["descripcion"],
                    fuente_id=1,  # SSReyes
                    fuente_nombre="San Sebastián de los Reyes",
                    url_original=pdf_url
                )
                db.add(evento)
                saved_count += 1
            
            db.commit()
            print(f"✅ [SSReyes] Successfully saved {saved_count} events to database")
            return {"guardados": saved_count}
            
        except Exception as e:
            db.rollback()
            print(f"❌ [SSReyes] Error saving to database: {str(e)}")
            raise e
        finally:
            db.close()

    def get_config_info(self) -> Dict:
        """Get configuration info for debugging"""
        return {
            "source_name": self.config["source_info"]["name"],
            "domain": self.config["source_info"]["domain"],
            "type": self.config["source_info"]["type"],
            "default_location": self.config["extraction_config"]["default_location"],
            "default_price": self.config["extraction_config"]["default_price"]
        }