# backend/scraping/__init__.py

"""
Intelligent scraping system with AI agents and modular tools
"""

# Core components
from .engine import ScrapingEngine

# Version info
__version__ = "1.0.0"
__description__ = "Intelligent web scraping with AI agents"

# Public API
__all__ = [
    # Core engine
    "ScrapingEngine",
    # Version info
    "__version__",
    "__description__"
]
