# scraping/pipelines/__init__.py

"""
Pipelines de procesamiento con LangGraph
"""
from .langgraph_pipeline import ScrapingPipeline, ScrapingState

__all__ = ["ScrapingPipeline", "ScrapingState"]