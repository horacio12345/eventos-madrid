# scraping/pipelines/langgraph_pipeline.py

"""
Pipeline principal de scraping usando LangGraph
"""
from typing import Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from backend.core import get_settings
from ..extractors import HTMLExtractor, PDFExtractor, ImageExtractor

settings = get_settings()


class ScrapingState(TypedDict):
    """Estado del pipeline de scraping"""
    url: str
    tipo: str  # HTML, PDF, IMAGE
    schema_extraccion: Dict
    mapeo_campos: Dict
    configuracion_scraping: Dict
    contenido_raw: Optional[str]
    eventos_extraidos: List[Dict]
    eventos_normalizados: List[Dict]
    errores: List[str]
    metadatos: Dict


class ScrapingPipeline:
    """
    Pipeline de scraping inteligente usando LangGraph
    """
    
    def __init__(self):
        # Inicializar LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0
            )
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                model=settings.anthropic_model,
                temperature=0
            )
        else:
            raise ValueError("Se requiere configurar OPENAI_API_KEY o ANTHROPIC_API_KEY")
        
        # Inicializar extractors
        self.extractors = {
            "HTML": HTMLExtractor(),
            "PDF": PDFExtractor(),
            "IMAGE": ImageExtractor()
        }
        
        # Construir grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Construir el grafo de procesamiento
        """
        builder = StateGraph(ScrapingState)
        
        # Añadir nodos
        builder.add_node("fetch", self._fetch_node)
        builder.add_node("extract", self._extract_node)
        builder.add_node("enhance", self._enhance_node)
        builder.add_node("normalize", self._normalize_node)
        builder.add_node("validate", self._validate_node)
        
        # Definir flujo
        builder.add_edge(START, "fetch")
        builder.add_edge("fetch", "extract")
        builder.add_edge("extract", "enhance")
        builder.add_edge("enhance", "normalize")
        builder.add_edge("normalize", "validate")
        builder.add_edge("validate", END)
        
        return builder.compile()
    
    async def run(self, url: str, tipo: str, schema_extraccion: Dict, 
                 mapeo_campos: Dict, configuracion_scraping: Dict) -> Dict:
        """
        Ejecutar pipeline completo de scraping
        """
        initial_state = ScrapingState(
            url=url,
            tipo=tipo,
            schema_extraccion=schema_extraccion,
            mapeo_campos=mapeo_campos,
            configuracion_scraping=configuracion_scraping,
            contenido_raw=None,
            eventos_extraidos=[],
            eventos_normalizados=[],
            errores=[],
            metadatos={}
        )
        
        # Ejecutar grafo
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "eventos": result["eventos_normalizados"],
            "errores": result["errores"],
            "metadatos": result["metadatos"]
        }
    
    async def _fetch_node(self, state: ScrapingState) -> ScrapingState:
        """
        Nodo para obtener contenido de la fuente
        """
        try:
            # Por ahora, solo registramos que se va a hacer fetch
            # El fetch real se hace en el extractor
            state["metadatos"]["fetch_iniciado"] = True
            
        except Exception as e:
            state["errores"].append(f"Error en fetch: {str(e)}")
        
        return state
    
    async def _extract_node(self, state: ScrapingState) -> ScrapingState:
        """
        Nodo para extraer contenido usando el extractor apropiado
        """
        try:
            extractor = self.extractors.get(state["tipo"])
            if not extractor:
                raise ValueError(f"Extractor no disponible para tipo: {state['tipo']}")
            
            # Extraer eventos
            eventos = await extractor.extract(
                url=state["url"],
                schema=state["schema_extraccion"],
                config=state["configuracion_scraping"]
            )
            
            state["eventos_extraidos"] = eventos
            state["metadatos"]["eventos_encontrados"] = len(eventos)
            
        except Exception as e:
            state["errores"].append(f"Error en extracción: {str(e)}")
            state["eventos_extraidos"] = []
        
        return state
    
    async def _enhance_node(self, state: ScrapingState) -> ScrapingState:
        """
        Nodo para mejorar eventos usando IA
        """
        try:
            if not state["eventos_extraidos"]:
                return state
            
            enhanced_events = []
            
            for evento in state["eventos_extraidos"]:
                # Mejorar evento con IA si tiene campos incompletos
                enhanced = await self._enhance_event_with_ai(evento)
                enhanced_events.append(enhanced)
            
            state["eventos_extraidos"] = enhanced_events
            state["metadatos"]["eventos_mejorados"] = len(enhanced_events)
            
        except Exception as e:
            state["errores"].append(f"Error en mejora: {str(e)}")
        
        return state
    
    async def _normalize_node(self, state: ScrapingState) -> ScrapingState:
        """
        Nodo para normalizar eventos al formato estándar
        """
        try:
            normalized_events = []
            
            for evento in state["eventos_extraidos"]:
                normalized = self._normalize_event(evento, state["mapeo_campos"])
                if normalized:
                    normalized_events.append(normalized)
            
            state["eventos_normalizados"] = normalized_events
            state["metadatos"]["eventos_normalizados"] = len(normalized_events)
            
        except Exception as e:
            state["errores"].append(f"Error en normalización: {str(e)}")
            state["eventos_normalizados"] = []
        
        return state
    
    async def _validate_node(self, state: ScrapingState) -> ScrapingState:
        """
        Nodo para validar eventos normalizados
        """
        try:
            valid_events = []
            
            for evento in state["eventos_normalizados"]:
                if self._validate_event(evento):
                    valid_events.append(evento)
                else:
                    state["errores"].append(f"Evento inválido: {evento.get('titulo', 'Sin título')}")
            
            state["eventos_normalizados"] = valid_events
            state["metadatos"]["eventos_validos"] = len(valid_events)
            
        except Exception as e:
            state["errores"].append(f"Error en validación: {str(e)}")
        
        return state
    
    async def _enhance_event_with_ai(self, evento: Dict) -> Dict:
        """
        Mejorar evento usando IA para completar campos faltantes
        """
        try:
            # Solo mejorar si faltan campos importantes
            if not evento.get("categoria") or not evento.get("descripcion"):
                
                prompt = f"""
                Analiza este evento y completa la información faltante:
                
                Título: {evento.get('titulo', 'N/A')}
                Descripción: {evento.get('descripcion', 'N/A')}
                Ubicación: {evento.get('ubicacion', 'N/A')}
                
                Tareas:
                1. Si falta categoría, asigna una de: Cultura, Deporte y Salud, Formación, Cine, Paseos y Excursiones, Ocio y Social
                2. Si la descripción está vacía o es muy corta, genera una descripción apropiada basada en el título
                3. Mantén el resto de campos tal como están
                
                Responde en formato JSON con los campos: titulo, descripcion, categoria, ubicacion
                """
                
                response = await self.llm.ainvoke(prompt)
                
                # Parsear respuesta e integrar con evento original
                try:
                    import json
                    enhanced_data = json.loads(response.content)
                    
                    # Actualizar solo campos que estaban vacíos o faltantes
                    if not evento.get("categoria") and enhanced_data.get("categoria"):
                        evento["categoria"] = enhanced_data["categoria"]
                    
                    if not evento.get("descripcion") and enhanced_data.get("descripcion"):
                        evento["descripcion"] = enhanced_data["descripcion"]
                        
                except (json.JSONDecodeError, KeyError):
                    # Si falla el parsing, continuar con evento original
                    pass
            
            return evento
            
        except Exception:
            # Si falla la mejora con IA, devolver evento original
            return evento
    
    def _normalize_event(self, evento: Dict, mapeo_campos: Dict) -> Optional[Dict]:
        """
        Normalizar evento usando el mapeo de campos definido
        """
        try:
            normalized = {}
            
            # Aplicar mapeo de campos
            for campo_origen, campo_destino in mapeo_campos.items():
                valor = evento.get(campo_origen)
                
                if valor:
                    # Manejar campos anidados como "datos_extra.telefono"
                    if "." in campo_destino:
                        parts = campo_destino.split(".")
                        if parts[0] == "datos_extra":
                            if "datos_extra" not in normalized:
                                normalized["datos_extra"] = {}
                            normalized["datos_extra"][parts[1]] = valor
                    else:
                        normalized[campo_destino] = valor
            
            # Añadir campos requeridos por defecto si no existen
            if not normalized.get("categoria"):
                normalized["categoria"] = "Ocio y Social"
            
            if not normalized.get("precio"):
                normalized["precio"] = "Gratis"
            
            # Copiar metadatos originales
            normalized["url_original"] = evento.get("url_original")
            normalized["fecha_extraccion"] = evento.get("fecha_extraccion")
            
            return normalized
            
        except Exception:
            return None
    
    def _validate_event(self, evento: Dict) -> bool:
        """
        Validar que un evento tiene los campos mínimos requeridos
        """
        # Campos obligatorios
        required_fields = ["titulo", "fecha_inicio", "categoria"]
        
        for field in required_fields:
            if not evento.get(field):
                return False
        
        # Validaciones adicionales
        if len(evento.get("titulo", "")) < 3:
            return False
        
        # La categoría debe ser una de las válidas
        valid_categories = [
            "Cultura", "Deporte y Salud", "Formación", 
            "Cine", "Paseos y Excursiones", "Ocio y Social"
        ]
        if evento.get("categoria") not in valid_categories:
            return False
        
        return True