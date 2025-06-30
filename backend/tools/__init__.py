# backend/tools/__init__.py

"""
A professional, modular toolkit for intelligent scraping agents.
"""
from .base_tool import BaseTool
from .html_tools import get_page_links
from .pdf_tools import read_pdf_content

# The final, clean set of tools for the agent.
# Each tool is simple, robust, and performs a single, well-defined task.
ALL_TOOLS = [
    get_page_links,
    read_pdf_content,
]

__all__ = [
    "BaseTool",
    "get_page_links",
    "read_pdf_content",
    "ALL_TOOLS",
]