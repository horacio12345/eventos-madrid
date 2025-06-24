# backend/scraping/pipelines/__init__.py

"""
Pipelines de procesamiento con LangGraph
"""

try:
    from .langgraph_pipeline import ScrapingPipeline, ScrapingState
except ImportError:
    # Pipeline dummy temporal
    class ScrapingPipeline:
        def __init__(self): pass
        async def run(self, **kwargs): return {"eventos": [], "errores": []}
    
    # State dummy temporal  
    class ScrapingState:
        pass

__all__ = ["ScrapingPipeline", "ScrapingState"]