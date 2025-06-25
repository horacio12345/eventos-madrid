# backend/tools/__init__.py

"""
Modular tools for intelligent scraping agents
"""
from .base_tool import BaseTool
from .html_tools import (
    extract_html_simple,
    extract_html_with_pdfs,
    analyze_web_structure
)
from .pdf_tools import (
    extract_pdf_direct,
    extract_multiple_pdfs
)
from .analysis_tools import (
    filter_by_current_month,
    validate_event_relevance
)
from .date_tools import (
    extract_month_from_text,
    get_relevant_date_range
)

# All available tools for agents
ALL_TOOLS = [
    extract_html_simple,
    extract_html_with_pdfs,
    analyze_web_structure,
    extract_pdf_direct,
    extract_multiple_pdfs,
    filter_by_current_month,
    validate_event_relevance,
    extract_month_from_text,
    get_relevant_date_range
]

__all__ = [
    "BaseTool",
    "ALL_TOOLS",
    "extract_html_simple",
    "extract_html_with_pdfs", 
    "analyze_web_structure",
    "extract_pdf_direct",
    "extract_multiple_pdfs",
    "filter_by_current_month",
    "validate_event_relevance",
    "extract_month_from_text",
    "get_relevant_date_range"
]