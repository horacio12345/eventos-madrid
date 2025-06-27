# backend/scraping/__init__.py

"""
Intelligent scraping system with AI agents and modular tools
"""

# ============= INTELLIGENT AGENTS =============
from backend.agents import (ProcessingAgent, ScrapingAgent,
                            ScrapingOrchestrator, SupervisorAgent)
# ============= PIPELINE STATE =============
from backend.states import (AgentExecutionState, EventValidationState,
                            ScrapingPipelineState, create_initial_state,
                            update_state_with_agent_result)
# ============= MODULAR TOOLS =============
from backend.tools import (ALL_TOOLS, analyze_web_structure,
                           extract_html_simple, extract_html_with_pdfs,
                           extract_month_from_text, extract_multiple_pdfs,
                           extract_pdf_direct, filter_by_current_month,
                           get_relevant_date_range, validate_event_relevance)

# ============= CORE SCRAPING ENGINE =============
from .engine import ScrapingEngine

# ============= LEGACY COMPATIBILITY =============
# Keep legacy extractors for backward compatibility if needed
try:
    from .extractors.html_extractor import HTMLExtractor
    from .extractors.image_extractor import ImageExtractor
    from .extractors.pdf_extractor import PDFExtractor

    LEGACY_EXTRACTORS_AVAILABLE = True
except ImportError:
    LEGACY_EXTRACTORS_AVAILABLE = False

    # Create dummy classes for backward compatibility
    class HTMLExtractor:
        def __init__(self):
            pass

        async def extract(self, url, schema, config):
            return []

    class PDFExtractor:
        def __init__(self):
            pass

        async def extract(self, url, schema, config):
            return []

    class ImageExtractor:
        def __init__(self):
            pass

        async def extract(self, url, schema, config):
            return []


# Legacy pipeline (deprecated - use ScrapingOrchestrator instead)
try:
    from .pipelines.langgraph_pipeline import ScrapingPipeline, ScrapingState

    LEGACY_PIPELINE_AVAILABLE = True
except ImportError:
    LEGACY_PIPELINE_AVAILABLE = False

    # Create dummy classes for backward compatibility
    class ScrapingPipeline:
        def __init__(self):
            pass

        async def run(self, **kwargs):
            raise DeprecationWarning(
                "Legacy ScrapingPipeline deprecated. Use ScrapingOrchestrator instead."
            )

    class ScrapingState:
        pass


# ============= PUBLIC API =============
__all__ = [
    # Core engine
    "ScrapingEngine",
    # AI Agents (recommended)
    "ScrapingAgent",
    "ProcessingAgent",
    "SupervisorAgent",
    "ScrapingOrchestrator",
    # Modular tools
    "ALL_TOOLS",
    "extract_html_simple",
    "extract_html_with_pdfs",
    "analyze_web_structure",
    "extract_pdf_direct",
    "extract_multiple_pdfs",
    "filter_by_current_month",
    "validate_event_relevance",
    "extract_month_from_text",
    "get_relevant_date_range",
    # Pipeline state
    "ScrapingPipelineState",
    "AgentExecutionState",
    "EventValidationState",
    "create_initial_state",
    "update_state_with_agent_result",
    # Legacy compatibility (deprecated)
    "HTMLExtractor",
    "PDFExtractor",
    "ImageExtractor",
    "ScrapingPipeline",
    "ScrapingState",
]

# ============= VERSION INFO =============
__version__ = "1.0.0"
__description__ = "Intelligent web scraping with AI agents"


# ============= SYSTEM STATUS =============
def get_system_status():
    """Get current system configuration status"""
    return {
        "version": __version__,
        "agents_available": True,
        "tools_count": len(ALL_TOOLS),
        "legacy_extractors": LEGACY_EXTRACTORS_AVAILABLE,
        "legacy_pipeline": LEGACY_PIPELINE_AVAILABLE,
        "recommended_components": [
            "ScrapingEngine (integrated with agents)",
            "ScrapingOrchestrator (agent coordinator)",
            "Modular tools (ALL_TOOLS)",
            "ScrapingPipelineState (typed state)",
        ],
    }
