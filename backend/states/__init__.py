# backend/states/__init__.py

"""
Shared state definitions for the scraping pipeline
"""
from .pipeline_state import (AgentExecutionState, EventValidationState,
                             PipelineMetadata, ScrapingPipelineState,
                             create_initial_state,
                             update_state_with_agent_result)

__all__ = [
    "ScrapingPipelineState",
    "AgentExecutionState",
    "EventValidationState",
    "PipelineMetadata",
    "create_initial_state",
    "update_state_with_agent_result",
]
