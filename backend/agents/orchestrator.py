# backend/agents/orchestrator.py - Versión con debug completo

"""
Scraping Agents Orchestrator - Coordinates complete flow
"""
from datetime import datetime
from typing import Dict, List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from .processing_agent import ProcessingAgent
from .scraping_agent import ScrapingAgent
from .supervisor_agent import SupervisorAgent


class ScrapingState(TypedDict):
    """Shared state between all scraping agents"""

    # Initial input
    url: str
    tipo: str
    schema_extraccion: Dict
    mapeo_campos: Dict
    configuracion_scraping: Dict

    # Scraping state
    scraping_strategy: str
    scraped_data: List[Dict]
    scraping_errors: List[str]
    scraping_metadata: Dict

    # Processing state
    processed_events: List[Dict]
    processing_errors: List[str]
    processing_metadata: Dict

    # Supervision state
    supervision_decision: str  # APPROVED, REJECTED, MANUAL_REVIEW, ERROR
    supervision_reasoning: str
    approved_events: List[Dict]
    rejected_events: List[Dict]

    # VALIDATION RESULTS - CRÍTICO para el fix
    validation_results: Dict

    # General metadata
    execution_start: str
    execution_end: str
    total_duration: float


class ScrapingOrchestrator:
    """
    Orchestrator that coordinates the 3 scraping agents
    """

    def __init__(self, scraping_tools: Optional[List] = None):
        # Validate and initialize tools
        self.scraping_tools = scraping_tools or []

        # Initialize agents
        try:
            self.scraping_agent = ScrapingAgent(tools=self.scraping_tools)
            self.processing_agent = ProcessingAgent()
            self.supervisor_agent = SupervisorAgent()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize agents: {str(e)}")

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build agents graph with error handling"""
        try:
            builder = StateGraph(ScrapingState)

            # Add nodes
            builder.add_node("scraping", self._scraping_node)
            builder.add_node("processing", self._processing_node)
            builder.add_node("supervision", self._supervision_node)
            builder.add_node("error_handler", self._error_handler_node)

            # Define main flow
            builder.add_edge(START, "scraping")

            # Conditional edges based on scraping success
            builder.add_conditional_edges(
                "scraping",
                self._should_continue_to_processing,
                {"continue": "processing", "error": "error_handler"},
            )

            # Conditional edges based on processing success
            builder.add_conditional_edges(
                "processing",
                self._should_continue_to_supervision,
                {"continue": "supervision", "error": "error_handler"},
            )

            # Final edges
            builder.add_edge("supervision", END)
            builder.add_edge("error_handler", END)

            return builder.compile()

        except Exception as e:
            raise RuntimeError(f"Failed to build graph: {str(e)}")

    async def execute_scraping_pipeline(
        self,
        url: str,
        tipo: str,
        schema_extraccion: Dict,
        mapeo_campos: Dict,
        configuracion_scraping: Dict,
    ) -> Dict:
        """
        Execute complete scraping pipeline with validation
        """
        print(f"🚀 [DEBUG] Starting pipeline for URL: {url}")
        
        # Validate required inputs
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL provided")

        if not tipo or tipo not in ["HTML", "PDF", "IMAGE"]:
            raise ValueError("Invalid tipo provided")

        # Initialize state with ALL required fields
        initial_state = ScrapingState(
            url=url,
            tipo=tipo,
            schema_extraccion=schema_extraccion or {},
            mapeo_campos=mapeo_campos or {},
            configuracion_scraping=configuracion_scraping or {},
            # Initialize other fields
            scraping_strategy="",
            scraped_data=[],
            scraping_errors=[],
            scraping_metadata={},
            processed_events=[],
            processing_errors=[],
            processing_metadata={},
            supervision_decision="",
            supervision_reasoning="",
            approved_events=[],
            rejected_events=[],
            # CRÍTICO: Inicializar validation_results SIEMPRE
            validation_results={
                "quality_score": 0.0,
                "total_extracted": 0,
                "total_validated": 0,
                "approval_rate": 0.0
            },
            execution_start=datetime.now().isoformat(),
            execution_end="",
            total_duration=0.0,
        )

        print(f"🔧 [DEBUG] Initial state validation_results: {initial_state['validation_results']}")

        try:
            # Execute graph
            start_time = datetime.now()
            print(f"🎯 [DEBUG] About to invoke graph...")
            
            final_state = await self.graph.ainvoke(initial_state)
            
            print(f"✅ [DEBUG] Graph execution completed. Final state keys: {list(final_state.keys())}")
            print(f"🔍 [DEBUG] Final state validation_results: {final_state.get('validation_results', 'MISSING!')}")
            
            end_time = datetime.now()

            # Update timing
            final_state["execution_end"] = end_time.isoformat()
            final_state["total_duration"] = (end_time - start_time).total_seconds()

            # ENSURE validation_results exists before returning
            if "validation_results" not in final_state:
                print(f"❌ [DEBUG] validation_results MISSING in final_state! Adding default...")
                final_state["validation_results"] = {
                    "quality_score": 0.0,
                    "total_extracted": 0,
                    "total_validated": 0,
                    "approval_rate": 0.0
                }

            return final_state

        except Exception as e:
            print(f"💥 [DEBUG] Pipeline execution failed: {str(e)}")
            # Handle catastrophic failures
            error_state = initial_state.copy()
            error_state.update(
                {
                    "supervision_decision": "ERROR",
                    "supervision_reasoning": f"Pipeline execution failed: {str(e)}",
                    "scraping_errors": [str(e)],
                    "execution_end": datetime.now().isoformat(),
                    "total_duration": (datetime.now() - start_time).total_seconds(),
                    # ASEGURAR que validation_results existe incluso en errores
                    "validation_results": {
                        "quality_score": 0.0,
                        "total_extracted": 0,
                        "total_validated": 0,
                        "approval_rate": 0.0
                    }
                }
            )
            print(f"🩹 [DEBUG] Error state validation_results: {error_state['validation_results']}")
            return error_state

    async def _scraping_node(self, state: ScrapingState) -> ScrapingState:
        """Scraping node with error handling"""
        try:
            print(f"🔍 [DEBUG] Scraping node - input state validation_results: {state.get('validation_results', 'MISSING!')}")
            result = await self.scraping_agent.analyze_and_scrape(state)
            print(f"🔍 [DEBUG] Scraping node - output state validation_results: {result.get('validation_results', 'MISSING!')}")
            return result
        except Exception as e:
            print(f"💥 [DEBUG] Scraping node error: {str(e)}")
            state["scraping_errors"].append(f"Scraping node error: {str(e)}")
            # ENSURE validation_results exists
            if "validation_results" not in state:
                state["validation_results"] = {
                    "quality_score": 0.0,
                    "total_extracted": 0,
                    "total_validated": 0,
                    "approval_rate": 0.0
                }
            return state

    async def _processing_node(self, state: ScrapingState) -> ScrapingState:
        """Processing node with error handling"""
        try:
            print(f"⚙️ [DEBUG] Processing node - input state validation_results: {state.get('validation_results', 'MISSING!')}")
            result = await self.processing_agent.process_data(state)
            
            # ACTUALIZAR validation_results desde processing metadata
            if "processing_metadata" in result:
                metadata = result["processing_metadata"]
                result["validation_results"] = {
                    "quality_score": 1.0 - metadata.get("rejection_rate", 0.0),
                    "total_extracted": metadata.get("total_raw", 0),
                    "total_validated": metadata.get("validated", 0),
                    "approval_rate": 1.0 - metadata.get("rejection_rate", 0.0)
                }
                print(f"⚙️ [DEBUG] Processing node - updated validation_results: {result['validation_results']}")
            else:
                # Ensure validation_results exists even if no metadata
                if "validation_results" not in result:
                    result["validation_results"] = state.get("validation_results", {
                        "quality_score": 0.0,
                        "total_extracted": 0,
                        "total_validated": 0,
                        "approval_rate": 0.0
                    })
                print(f"⚙️ [DEBUG] Processing node - fallback validation_results: {result['validation_results']}")
            
            return result
        except Exception as e:
            print(f"💥 [DEBUG] Processing node error: {str(e)}")
            state["processing_errors"].append(f"Processing node error: {str(e)}")
            # ENSURE validation_results exists in errors
            if "validation_results" not in state:
                state["validation_results"] = {
                    "quality_score": 0.0,
                    "total_extracted": 0,
                    "total_validated": 0,
                    "approval_rate": 0.0
                }
            return state

    async def _supervision_node(self, state: ScrapingState) -> ScrapingState:
        """Supervision node with error handling"""
        try:
            print(f"👨‍💼 [DEBUG] Supervision node - input state validation_results: {state.get('validation_results', 'MISSING!')}")
            result = await self.supervisor_agent.supervise_quality(state)
            print(f"👨‍💼 [DEBUG] Supervision node - output state validation_results: {result.get('validation_results', 'MISSING!')}")
            return result
        except Exception as e:
            print(f"💥 [DEBUG] Supervision node error: {str(e)}")
            state["supervision_decision"] = "ERROR"
            state["supervision_reasoning"] = f"Supervision node error: {str(e)}"
            # ENSURE validation_results exists
            if "validation_results" not in state:
                state["validation_results"] = {
                    "quality_score": 0.0,
                    "total_extracted": 0,
                    "total_validated": 0,
                    "approval_rate": 0.0
                }
            return state

    async def _error_handler_node(self, state: ScrapingState) -> ScrapingState:
        """Handle pipeline errors gracefully"""
        print(f"🚨 [DEBUG] Error handler node - input state validation_results: {state.get('validation_results', 'MISSING!')}")
        
        all_errors = state.get("scraping_errors", []) + state.get(
            "processing_errors", []
        )

        state["supervision_decision"] = "ERROR"
        state["supervision_reasoning"] = (
            f"Pipeline failed with {len(all_errors)} errors"
        )
        state["approved_events"] = []
        
        # ENSURE validation_results exists in error handler
        if "validation_results" not in state:
            state["validation_results"] = {
                "quality_score": 0.0,
                "total_extracted": 0,
                "total_validated": 0,
                "approval_rate": 0.0
            }
        
        print(f"🚨 [DEBUG] Error handler node - final validation_results: {state['validation_results']}")
        return state

    def _should_continue_to_processing(self, state: ScrapingState) -> str:
        """Determine if scraping was successful enough to continue"""
        scraping_errors = state.get("scraping_errors", [])
        scraped_data = state.get("scraped_data", [])

        # Continue if we have data and no critical errors
        if scraped_data and len(scraping_errors) == 0:
            return "continue"

        # Continue if we have some data despite minor errors
        if scraped_data and len(scraping_errors) <= 2:
            return "continue"

        return "error"

    def _should_continue_to_supervision(self, state: ScrapingState) -> str:
        """Determine if processing was successful enough to continue"""
        processing_errors = state.get("processing_errors", [])
        processed_events = state.get("processed_events", [])

        # Continue if we have processed events
        if processed_events:
            return "continue"

        # Go to error handler if no events processed
        return "error"

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return [tool.name for tool in self.scraping_tools]

    def validate_configuration(self) -> Dict[str, bool]:
        """Validate orchestrator configuration"""
        return {
            "scraping_agent_ready": self.scraping_agent is not None,
            "processing_agent_ready": self.processing_agent is not None,
            "supervisor_agent_ready": self.supervisor_agent is not None,
            "tools_available": len(self.scraping_tools) > 0,
            "graph_compiled": self.graph is not None,
        }