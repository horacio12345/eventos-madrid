# backend/agents/orchestrator.py

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
        # Validate required inputs
        if not url or not url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL provided")

        if not tipo or tipo not in ["HTML", "PDF", "IMAGE"]:
            raise ValueError("Invalid tipo provided")

        # Initialize state
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
            execution_start=datetime.now().isoformat(),
            execution_end="",
            total_duration=0.0,
        )

        try:
            # Execute graph
            start_time = datetime.now()
            final_state = await self.graph.ainvoke(initial_state)
            end_time = datetime.now()

            # Update timing
            final_state["execution_end"] = end_time.isoformat()
            final_state["total_duration"] = (end_time - start_time).total_seconds()

            return final_state

        except Exception as e:
            # Handle catastrophic failures
            error_state = initial_state.copy()
            error_state.update(
                {
                    "supervision_decision": "ERROR",
                    "supervision_reasoning": f"Pipeline execution failed: {str(e)}",
                    "scraping_errors": [str(e)],
                    "execution_end": datetime.now().isoformat(),
                    "total_duration": (datetime.now() - start_time).total_seconds(),
                }
            )
            return error_state

    async def _scraping_node(self, state: ScrapingState) -> ScrapingState:
        """Scraping node with error handling"""
        try:
            return await self.scraping_agent.analyze_and_scrape(state)
        except Exception as e:
            state["scraping_errors"].append(f"Scraping node error: {str(e)}")
            return state

    async def _processing_node(self, state: ScrapingState) -> ScrapingState:
        """Processing node with error handling"""
        try:
            return await self.processing_agent.process_data(state)
        except Exception as e:
            state["processing_errors"].append(f"Processing node error: {str(e)}")
            return state

    async def _supervision_node(self, state: ScrapingState) -> ScrapingState:
        """Supervision node with error handling"""
        try:
            return await self.supervisor_agent.supervise_quality(state)
        except Exception as e:
            state["supervision_decision"] = "ERROR"
            state["supervision_reasoning"] = f"Supervision node error: {str(e)}"
            return state

    async def _error_handler_node(self, state: ScrapingState) -> ScrapingState:
        """Handle pipeline errors gracefully"""
        all_errors = state.get("scraping_errors", []) + state.get(
            "processing_errors", []
        )

        state["supervision_decision"] = "ERROR"
        state["supervision_reasoning"] = (
            f"Pipeline failed with {len(all_errors)} errors"
        )
        state["approved_events"] = []

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
