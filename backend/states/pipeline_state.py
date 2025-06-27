# backend/states/pipeline_state.py

"""
Comprehensive state management for the scraping pipeline
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict


class AgentExecutionState(TypedDict):
    """State for individual agent execution"""

    started_at: str
    completed_at: Optional[str]
    duration_seconds: Optional[float]
    status: Literal["pending", "running", "completed", "failed"]
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class EventValidationState(TypedDict):
    """State for event validation process"""

    total_extracted: int
    total_normalized: int
    total_validated: int
    total_approved: int
    total_rejected: int
    rejection_rate: float
    approval_rate: float
    quality_score: float


class PipelineMetadata(TypedDict):
    """Metadata for the entire pipeline execution"""

    pipeline_version: str
    execution_id: str
    source_type: str
    source_url: str
    execution_environment: str
    total_duration_seconds: float
    memory_usage_mb: Optional[float]
    performance_metrics: Dict[str, Any]


class ScrapingPipelineState(TypedDict):
    """
    Comprehensive state for the entire scraping pipeline.
    Shared between all agents and stages.
    """

    # ============= PIPELINE IDENTIFICATION =============
    execution_id: str
    pipeline_version: str
    created_at: str
    updated_at: str

    # ============= INITIAL INPUT =============
    source_url: str
    source_type: Literal["HTML", "PDF", "IMAGE"]
    schema_extraccion: Dict[str, Any]
    mapeo_campos: Dict[str, str]
    configuracion_scraping: Dict[str, Any]

    # ============= SCRAPING AGENT STATE =============
    scraping_agent: AgentExecutionState
    scraping_strategy: str
    web_analysis_result: Dict[str, Any]
    scraped_data: List[Dict[str, Any]]
    scraping_tools_used: List[str]

    # ============= PROCESSING AGENT STATE =============
    processing_agent: AgentExecutionState
    normalized_events: List[Dict[str, Any]]
    validation_results: EventValidationState
    field_mapping_applied: Dict[str, str]

    # ============= SUPERVISOR AGENT STATE =============
    supervisor_agent: AgentExecutionState
    final_decision: Literal["APPROVED", "REJECTED", "MANUAL_REVIEW", "ERROR"]
    decision_reasoning: str
    quality_assessment: Dict[str, Any]
    approved_events: List[Dict[str, Any]]
    rejected_events: List[Dict[str, Any]]

    # ============= GLOBAL PIPELINE STATE =============
    overall_status: Literal[
        "initializing", "scraping", "processing", "supervising", "completed", "failed"
    ]
    pipeline_errors: List[str]
    pipeline_warnings: List[str]

    # ============= EXECUTION METRICS =============
    execution_start: str
    execution_end: Optional[str]
    total_duration_seconds: Optional[float]

    # ============= METADATA =============
    pipeline_metadata: PipelineMetadata

    # ============= FUTURE EXTENSIONS =============
    # Reserved for conversation agent integration
    conversation_context: Optional[Dict[str, Any]]
    user_interaction_history: Optional[List[Dict[str, Any]]]


@dataclass
class StateBuilder:
    """Builder class for creating and updating pipeline state"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset builder to initial state"""
        self._state_data = {}
        return self

    def with_source_info(
        self, url: str, source_type: str, schema: Dict, mapping: Dict, config: Dict
    ):
        """Set source information"""
        self._state_data.update(
            {
                "source_url": url,
                "source_type": source_type,
                "schema_extraccion": schema,
                "mapeo_campos": mapping,
                "configuracion_scraping": config,
            }
        )
        return self

    def with_execution_id(self, execution_id: str):
        """Set execution ID"""
        self._state_data["execution_id"] = execution_id
        return self

    def build(self) -> ScrapingPipelineState:
        """Build the complete state"""
        now = datetime.now().isoformat()

        return ScrapingPipelineState(
            # Pipeline identification
            execution_id=self._state_data.get(
                "execution_id", f"exec_{int(datetime.now().timestamp())}"
            ),
            pipeline_version="1.0.0",
            created_at=now,
            updated_at=now,
            # Initial input
            source_url=self._state_data.get("source_url", ""),
            source_type=self._state_data.get("source_type", "HTML"),
            schema_extraccion=self._state_data.get("schema_extraccion", {}),
            mapeo_campos=self._state_data.get("mapeo_campos", {}),
            configuracion_scraping=self._state_data.get("configuracion_scraping", {}),
            # Scraping agent state
            scraping_agent=AgentExecutionState(
                started_at="",
                completed_at=None,
                duration_seconds=None,
                status="pending",
                errors=[],
                warnings=[],
                metadata={},
            ),
            scraping_strategy="",
            web_analysis_result={},
            scraped_data=[],
            scraping_tools_used=[],
            # Processing agent state
            processing_agent=AgentExecutionState(
                started_at="",
                completed_at=None,
                duration_seconds=None,
                status="pending",
                errors=[],
                warnings=[],
                metadata={},
            ),
            normalized_events=[],
            validation_results=EventValidationState(
                total_extracted=0,
                total_normalized=0,
                total_validated=0,
                total_approved=0,
                total_rejected=0,
                rejection_rate=0.0,
                approval_rate=0.0,
                quality_score=0.0,
            ),
            field_mapping_applied={},
            # Supervisor agent state
            supervisor_agent=AgentExecutionState(
                started_at="",
                completed_at=None,
                duration_seconds=None,
                status="pending",
                errors=[],
                warnings=[],
                metadata={},
            ),
            final_decision="APPROVED",
            decision_reasoning="",
            quality_assessment={},
            approved_events=[],
            rejected_events=[],
            # Global pipeline state
            overall_status="initializing",
            pipeline_errors=[],
            pipeline_warnings=[],
            # Execution metrics
            execution_start=now,
            execution_end=None,
            total_duration_seconds=None,
            # Metadata
            pipeline_metadata=PipelineMetadata(
                pipeline_version="1.0.0",
                execution_id=self._state_data.get(
                    "execution_id", f"exec_{int(datetime.now().timestamp())}"
                ),
                source_type=self._state_data.get("source_type", "HTML"),
                source_url=self._state_data.get("source_url", ""),
                execution_environment="production",
                total_duration_seconds=0.0,
                memory_usage_mb=None,
                performance_metrics={},
            ),
            # Future extensions
            conversation_context=None,
            user_interaction_history=None,
        )


def create_initial_state(
    url: str,
    source_type: str,
    schema_extraccion: Dict[str, Any],
    mapeo_campos: Dict[str, str],
    configuracion_scraping: Dict[str, Any],
    execution_id: Optional[str] = None,
) -> ScrapingPipelineState:
    """
    Create initial pipeline state with provided parameters.

    Args:
        url: Source URL to scrape
        source_type: Type of source (HTML, PDF, IMAGE)
        schema_extraccion: Extraction schema configuration
        mapeo_campos: Field mapping configuration
        configuracion_scraping: Scraping configuration
        execution_id: Optional execution ID

    Returns:
        Initial pipeline state
    """
    builder = StateBuilder()

    if execution_id:
        builder.with_execution_id(execution_id)

    return builder.with_source_info(
        url, source_type, schema_extraccion, mapeo_campos, configuracion_scraping
    ).build()


def update_state_with_agent_result(
    state: ScrapingPipelineState,
    agent_name: Literal["scraping_agent", "processing_agent", "supervisor_agent"],
    result: Dict[str, Any],
    status: Literal["completed", "failed"] = "completed",
) -> ScrapingPipelineState:
    """
    Update pipeline state with agent execution result.

    Args:
        state: Current pipeline state
        agent_name: Name of the agent that executed
        result: Agent execution result
        status: Execution status

    Returns:
        Updated pipeline state
    """
    now = datetime.now().isoformat()
    state["updated_at"] = now

    # Update agent-specific state
    agent_state = state[agent_name]

    if not agent_state["started_at"]:
        agent_state["started_at"] = now

    agent_state["completed_at"] = now
    agent_state["status"] = status

    # Calculate duration if start time exists
    if agent_state["started_at"]:
        try:
            start_time = datetime.fromisoformat(agent_state["started_at"])
            end_time = datetime.fromisoformat(now)
            agent_state["duration_seconds"] = (end_time - start_time).total_seconds()
        except ValueError:
            agent_state["duration_seconds"] = None

    # Update agent-specific data based on agent type
    if agent_name == "scraping_agent":
        state["scraped_data"] = result.get("data", [])
        state["scraping_strategy"] = result.get("metadata", {}).get("strategy", "")
        state["scraping_tools_used"] = result.get("metadata", {}).get("tools_used", [])
        state["web_analysis_result"] = result.get("metadata", {}).get("analysis", {})

        if status == "completed" and state["scraped_data"]:
            state["overall_status"] = "processing"
        elif status == "failed":
            state["overall_status"] = "failed"

    elif agent_name == "processing_agent":
        state["normalized_events"] = result.get("data", [])
        processing_metadata = result.get("metadata", {})

        state["validation_results"]["total_extracted"] = processing_metadata.get(
            "total_raw", 0
        )
        state["validation_results"]["total_normalized"] = processing_metadata.get(
            "normalized", 0
        )
        state["validation_results"]["total_validated"] = processing_metadata.get(
            "validated", 0
        )

        if state["validation_results"]["total_extracted"] > 0:
            state["validation_results"]["approval_rate"] = (
                state["validation_results"]["total_validated"]
                / state["validation_results"]["total_extracted"]
            )

        if status == "completed" and state["normalized_events"]:
            state["overall_status"] = "supervising"
        elif status == "failed":
            state["overall_status"] = "failed"

    elif agent_name == "supervisor_agent":
        state["approved_events"] = result.get("approved_events", [])
        state["rejected_events"] = result.get("rejected_events", [])
        state["final_decision"] = result.get("decision", "ERROR")
        state["decision_reasoning"] = result.get("reasoning", "")
        state["quality_assessment"] = result.get("metadata", {})

        state["validation_results"]["total_approved"] = len(state["approved_events"])
        state["validation_results"]["total_rejected"] = len(state["rejected_events"])

        if status == "completed":
            state["overall_status"] = "completed"
        elif status == "failed":
            state["overall_status"] = "failed"

    # Add errors and warnings
    agent_state["errors"].extend(result.get("errors", []))
    agent_state["warnings"].extend(result.get("warnings", []))
    agent_state["metadata"].update(result.get("metadata", {}))

    # Update global errors if any
    if result.get("errors"):
        state["pipeline_errors"].extend(result["errors"])

    return state


def finalize_pipeline_state(state: ScrapingPipelineState) -> ScrapingPipelineState:
    """
    Finalize pipeline state with execution metrics.

    Args:
        state: Pipeline state to finalize

    Returns:
        Finalized pipeline state
    """
    now = datetime.now().isoformat()

    state["execution_end"] = now
    state["updated_at"] = now

    # Calculate total duration
    try:
        start_time = datetime.fromisoformat(state["execution_start"])
        end_time = datetime.fromisoformat(now)
        state["total_duration_seconds"] = (end_time - start_time).total_seconds()
        state["pipeline_metadata"]["total_duration_seconds"] = state[
            "total_duration_seconds"
        ]
    except ValueError:
        state["total_duration_seconds"] = None

    # Calculate final quality score
    validation = state["validation_results"]
    if validation["total_extracted"] > 0:
        validation["quality_score"] = (
            validation["total_approved"] / validation["total_extracted"]
        ) * 0.7 + (max(0, 1 - len(state["pipeline_errors"]) / 10)) * 0.3

    return state


def get_state_summary(state: ScrapingPipelineState) -> Dict[str, Any]:
    """
    Get a summary of the pipeline state for logging/monitoring.

    Args:
        state: Pipeline state

    Returns:
        State summary
    """
    return {
        "execution_id": state["execution_id"],
        "overall_status": state["overall_status"],
        "source_url": state["source_url"],
        "source_type": state["source_type"],
        "total_duration": state["total_duration_seconds"],
        "events_approved": len(state["approved_events"]),
        "events_rejected": len(state["rejected_events"]),
        "final_decision": state["final_decision"],
        "quality_score": state["validation_results"]["quality_score"],
        "pipeline_errors": len(state["pipeline_errors"]),
        "agent_statuses": {
            "scraping": state["scraping_agent"]["status"],
            "processing": state["processing_agent"]["status"],
            "supervisor": state["supervisor_agent"]["status"],
        },
    }
