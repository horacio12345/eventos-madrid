# backend/scraping/engine.py

"""
Intelligent scraping engine - Orchestrates extraction using AI agents
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.agents import ScrapingOrchestrator
from backend.core import get_db, get_settings
from backend.core.models import Evento, FuenteWeb, LogScraping
from backend.states import (create_initial_state, finalize_pipeline_state,
                            update_state_with_agent_result)
from backend.tools import ALL_TOOLS

settings = get_settings()


class ScrapingEngine:
    """
    Intelligent scraping engine that coordinates extraction using AI agents and modular tools
    """

    def __init__(self):
        # Initialize orchestrator with all available tools
        self.orchestrator = ScrapingOrchestrator(scraping_tools=ALL_TOOLS)

        # Validate orchestrator configuration
        config_status = self.orchestrator.validate_configuration()
        if not all(config_status.values()):
            raise RuntimeError(f"Orchestrator configuration invalid: {config_status}")

    async def execute_scraping(self, fuente_id: Optional[int] = None) -> Dict:
        """
        Execute scraping for specific source or all active sources
        """
        results = {"total_ejecutadas": 0, "exitosas": 0, "errores": 0, "detalles": []}

        # Get sources to process
        db = next(get_db())
        try:
            if fuente_id:
                fuentes = (
                    db.query(FuenteWeb)
                    .filter(FuenteWeb.id == fuente_id, FuenteWeb.activa == True)
                    .all()
                )
            else:
                fuentes = db.query(FuenteWeb).filter(FuenteWeb.activa == True).all()
        finally:
            db.close()

        # Process each source
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
        Process individual source using intelligent agent pipeline
        """
        inicio_tiempo = datetime.now()

        # Create execution log
        db = next(get_db())
        try:
            log = LogScraping(
                fuente_id=fuente.id,
                fuente_nombre=fuente.nombre,
                fecha_inicio=inicio_tiempo,
                estado="running",
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            log_id = log.id
        finally:
            db.close()

        try:
            # Create initial pipeline state
            execution_id = f"exec_{fuente.id}_{int(inicio_tiempo.timestamp())}"

            # Execute intelligent agent pipeline
            final_state = await self.orchestrator.execute_scraping_pipeline(
                url=fuente.url,
                tipo=fuente.tipo,
                schema_extraccion=fuente.schema_extraccion or {},
                mapeo_campos=fuente.mapeo_campos or {},
                configuracion_scraping=fuente.configuracion_scraping or {},
            )

            # Process extracted events if approved
            if final_state["supervision_decision"] == "APPROVED":
                eventos_procesados = await self._procesar_eventos(
                    final_state["approved_events"], fuente
                )
            else:
                eventos_procesados = {"nuevos": [], "actualizados": []}

            # Update source status
            db = next(get_db())
            try:
                fuente_db = (
                    db.query(FuenteWeb).filter(FuenteWeb.id == fuente.id).first()
                )
                if fuente_db:
                    fuente_db.ultima_ejecucion = datetime.now()
                    fuente_db.ultimo_estado = "success"
                    fuente_db.eventos_encontrados_ultima_ejecucion = len(
                        eventos_procesados["nuevos"]
                    ) + len(eventos_procesados["actualizados"])
                    db.commit()
            finally:
                db.close()

            # Finalize log
            tiempo_transcurrido = (datetime.now() - inicio_tiempo).total_seconds()
            self._finalizar_log(
                log_id, "success", eventos_procesados, tiempo_transcurrido, final_state
            )

            # CORRECCIÓN: Manejo seguro de validation_results
            validation_results = final_state.get("validation_results", {})
            quality_score = validation_results.get("quality_score", 0.0)

            return {
                "fuente_id": fuente.id,
                "fuente_nombre": fuente.nombre,
                "estado": "success",
                "eventos_nuevos": len(eventos_procesados["nuevos"]),
                "eventos_actualizados": len(eventos_procesados["actualizados"]),
                "tiempo_segundos": tiempo_transcurrido,
                "pipeline_decision": final_state["supervision_decision"],
                "quality_score": quality_score,
                "agent_strategy": final_state["scraping_strategy"],
            }

        except Exception as e:
            # Handle errors
            tiempo_transcurrido = (datetime.now() - inicio_tiempo).total_seconds()
            error_msg = str(e)

            # Update source with error
            db = next(get_db())
            try:
                fuente_db = (
                    db.query(FuenteWeb).filter(FuenteWeb.id == fuente.id).first()
                )
                if fuente_db:
                    fuente_db.ultima_ejecucion = datetime.now()
                    fuente_db.ultimo_estado = "error"
                    fuente_db.ultimo_error = error_msg
                    db.commit()

                # Finalize log with error
                self._finalizar_log(
                    log_id,
                    "error",
                    {"nuevos": [], "actualizados": []},
                    tiempo_transcurrido,
                    None,
                    error_msg,
                )
            finally:
                db.close()

            return {
                "fuente_id": fuente.id,
                "fuente_nombre": fuente.nombre,
                "estado": "error",
                "error": error_msg,
                "tiempo_segundos": tiempo_transcurrido,
            }

    async def _procesar_eventos(
        self, eventos_raw: List[Dict], fuente: FuenteWeb
    ) -> Dict:
        """
        Process extracted events and save to database
        """
        eventos_nuevos = []
        eventos_actualizados = []

        db = next(get_db())
        try:
            for evento_data in eventos_raw:
                # Generate hash for duplicate detection
                contenido_hash = self._generar_hash_evento(evento_data)

                # Find existing event
                evento_existente = (
                    db.query(Evento)
                    .filter(
                        Evento.hash_contenido == contenido_hash,
                        Evento.fuente_id == fuente.id,
                    )
                    .first()
                )

                if evento_existente:
                    # Update existing event
                    self._actualizar_evento(evento_existente, evento_data)
                    eventos_actualizados.append(evento_existente)
                else:
                    # Create new event
                    nuevo_evento = self._crear_evento(
                        evento_data, fuente, contenido_hash
                    )
                    db.add(nuevo_evento)
                    eventos_nuevos.append(nuevo_evento)

            db.commit()
        finally:
            db.close()

        return {"nuevos": eventos_nuevos, "actualizados": eventos_actualizados}

    def _generar_hash_evento(self, evento_data: Dict) -> str:
        """
        Generate unique hash for event based on key content
        """
        import hashlib

        # Use key fields to generate hash
        contenido_clave = f"{evento_data.get('titulo', '')}{evento_data.get('fecha_inicio', '')}{evento_data.get('ubicacion', '')}"
        return hashlib.sha256(contenido_clave.encode()).hexdigest()

    def _crear_evento(
        self, evento_data: Dict, fuente: FuenteWeb, hash_contenido: str
    ) -> Evento:
        """
        Create new event from extracted data
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
            datos_raw=evento_data,
        )

    def _actualizar_evento(self, evento: Evento, evento_data: Dict) -> None:
        """
        Update existing event with new data
        """
        evento.titulo = evento_data.get("titulo", evento.titulo)
        evento.precio = evento_data.get("precio", evento.precio)
        evento.ubicacion = evento_data.get("ubicacion", evento.ubicacion)
        evento.descripcion = evento_data.get("descripcion", evento.descripcion)
        evento.datos_extra = evento_data.get("datos_extra", evento.datos_extra)
        evento.datos_raw = evento_data
        evento.ultima_actualizacion = datetime.now()

    def _finalizar_log(
        self,
        log_id: int,
        estado: str,
        eventos: Dict,
        tiempo_segundos: float,
        pipeline_state: Optional[Dict] = None,
        error: str = None,
    ) -> None:
        """
        Finalize scraping log with results
        """
        db = next(get_db())
        try:
            log = db.query(LogScraping).filter(LogScraping.id == log_id).first()
            if log:
                log.fecha_fin = datetime.now()
                log.estado = estado
                log.eventos_extraidos = len(eventos["nuevos"]) + len(
                    eventos["actualizados"]
                )
                log.eventos_nuevos = len(eventos["nuevos"])
                log.eventos_actualizados = len(eventos["actualizados"])
                log.tiempo_ejecucion_segundos = int(tiempo_segundos)

                if error:
                    log.detalles_error = error
                elif pipeline_state:
                    # CORRECCIÓN: Acceso seguro a validation_results
                    validation_results = pipeline_state.get("validation_results", {})
                    quality_score = validation_results.get("quality_score", 0.0)
                    
                    # Add pipeline insights to log message
                    log.mensaje = (
                        f"Decision: {pipeline_state.get('supervision_decision', 'N/A')}, "
                        f"Strategy: {pipeline_state.get('scraping_strategy', 'N/A')}, "
                        f"Quality: {quality_score:.2f}"
                    )

                db.commit()
        finally:
            db.close()

    async def test_fuente(self, configuracion_test: Dict) -> Dict:
        """
        Test source configuration without saving data
        """
        print("--- DENTRO DE SCRAPING ENGINE: test_fuente ---")
        print(f"Configuración de test recibida:\n{configuracion_test}")
        
        try:
            # Execute intelligent agent pipeline for testing
            print("🚀 Ejecutando el pipeline del orquestador...")
            final_state = await self.orchestrator.execute_scraping_pipeline(
                url=configuracion_test["url"],
                tipo=configuracion_test["tipo"],
                schema_extraccion=configuracion_test.get("schema_extraccion", {}),
                mapeo_campos=configuracion_test.get("mapeo_campos", {}),
                configuracion_scraping=configuracion_test.get(
                    "configuracion_scraping", {}
                ),
            )
            
            print("\n✅ Pipeline del orquestador finalizado. Estado final completo:")
            print(final_state)
            print("-" * 20)

            # CORRECCIÓN: Acceso seguro a validation_results
            validation_results = final_state.get("validation_results", {})

            # Prepare response in expected format
            if final_state["supervision_decision"] == "APPROVED":
                eventos_preview = final_state["approved_events"][:3]
                estado = "success"
                errores = []
            elif final_state["supervision_decision"] == "ERROR":
                eventos_preview = []
                estado = "error"
                errores = final_state.get("pipeline_errors", ["Error no especificado en pipeline_errors"])
            else: # REJECTED, etc.
                eventos_preview = final_state.get("approved_events", [])[:3]
                estado = "warning"
                errores = [
                    f"Decisión: {final_state['supervision_decision']} - {final_state.get('supervision_reasoning', 'Sin razonamiento.')}"
                ]

            response = {
                "estado": estado,
                "eventos_encontrados": len(final_state.get("approved_events", [])),
                "preview_eventos": eventos_preview,
                "tiempo_ejecucion": final_state.get("total_duration", 0),
                "errores": errores,
                "pipeline_decision": final_state["supervision_decision"],
                "decision_reasoning": final_state.get("supervision_reasoning", ""),
                "quality_score": validation_results.get("quality_score", 0.0),
                "scraping_strategy": final_state.get("scraping_strategy", "unknown"),
                "agent_metadata": {
                    "tools_used": final_state.get("scraping_tools_used", []),
                    "analysis_result": final_state.get("web_analysis_result", {}),
                    "validation_metrics": validation_results,
                },
            }
            print("\n📦 Respuesta preparada para enviar al frontend:")
            print(response)
            print("--- FIN DE test_fuente ---")
            return response

        except Exception as e:
            import traceback
            print("\n💥 ERROR INESPERADO DENTRO DE test_fuente:")
            traceback.print_exc()
            
            response = {
                "estado": "error",
                "error": f"Excepción en ScrapingEngine: {str(e)}",
                "eventos_encontrados": 0,
                "preview_eventos": [],
                "errores": [str(e), traceback.format_exc()],
                "pipeline_decision": "CRITICAL_ERROR",
                "decision_reasoning": f"Pipeline execution failed with exception: {str(e)}",
                "quality_score": 0.0,
                "scraping_strategy": "failed",
                "agent_metadata": {},
            }
            print("\n📦 Respuesta de error preparada para enviar al frontend:")
            print(response)
            print("--- FIN DE test_fuente (con error) ---")
            return response

    def get_orchestrator_status(self) -> Dict:
        """
        Get orchestrator configuration and status
        """
        return {
            "configuration_valid": self.orchestrator.validate_configuration(),
            "available_tools": self.orchestrator.get_available_tools(),
            "agents_ready": {
                "scraping_agent": self.orchestrator.scraping_agent is not None,
                "processing_agent": self.orchestrator.processing_agent is not None,
                "supervisor_agent": self.orchestrator.supervisor_agent is not None,
            },
            "total_tools": len(ALL_TOOLS),
        }