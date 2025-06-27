# backend/tools/__init__.py

"""
Modular tools for intelligent scraping agents
"""
from .base_tool import BaseTool
# Content analysis tools
from .content_analysis_tools import (analyze_content_types,
                                     analyze_page_structure)
# Content prioritization tools
from .content_prioritization_tools import (prioritize_content_final,
                                           rank_content_by_strategy,
                                           select_top_content)
# HTML extraction tools
from .html_tools import (analyze_web_structure, extract_html_simple,
                         extract_html_with_pdfs)
# PDF extraction tools
from .pdf_tools import extract_multiple_pdfs, extract_pdf_direct
# Temporal analysis tools
from .temporal_analysis_tools import (detect_temporal_patterns,
                                      extract_dates_from_text,
                                      prioritize_by_temporal_relevance)

# Content validation tools (if exists)
try:
    from .content_validation_tools import validate_event_relevance

    VALIDATION_TOOLS = [validate_event_relevance]
except ImportError:
    VALIDATION_TOOLS = []

# All available tools for agents
ALL_TOOLS = [
    # Content analysis
    analyze_page_structure,
    analyze_content_types,
    # Temporal analysis
    detect_temporal_patterns,
    extract_dates_from_text,
    prioritize_by_temporal_relevance,
    # Content prioritization
    rank_content_by_strategy,
    select_top_content,
    prioritize_content_final,
    # HTML extraction
    extract_html_simple,
    extract_html_with_pdfs,
    analyze_web_structure,
    # PDF extraction
    extract_pdf_direct,
    extract_multiple_pdfs,
    # Content validation (if available)
    *VALIDATION_TOOLS,
]

__all__ = [
    # Base class
    "BaseTool",
    # Content analysis tools
    "analyze_page_structure",
    "analyze_content_types",
    # Temporal analysis tools
    "detect_temporal_patterns",
    "extract_dates_from_text",
    "prioritize_by_temporal_relevance",
    # Content prioritization tools
    "rank_content_by_strategy",
    "select_top_content",
    "prioritize_content_final",
    # HTML extraction tools
    "extract_html_simple",
    "extract_html_with_pdfs",
    "analyze_web_structure",
    # PDF extraction tools
    "extract_pdf_direct",
    "extract_multiple_pdfs",
    # Tool collections
    "ALL_TOOLS",
]

# Add validation tools to __all__ if available
if VALIDATION_TOOLS:
    __all__.append("validate_event_relevance")
