# backend/scraping/__init__.py

"""
Módulo de scraping inteligente
"""
from .engine import ScrapingEngine

# Importar extractors solo si existen los archivos
try:
    from .extractors.html_extractor import HTMLExtractor
    from .extractors.pdf_extractor import PDFExtractor
    from .extractors.image_extractor import ImageExtractor
except ImportError:
    # Si no existen, crear clases dummy temporales
    class HTMLExtractor:
        def __init__(self): pass
        async def extract(self, url, schema, config): return []
    
    class PDFExtractor:
        def __init__(self): pass
        async def extract(self, url, schema, config): return []
    
    class ImageExtractor:
        def __init__(self): pass
        async def extract(self, url, schema, config): return []

# Importar pipeline solo si existe
try:
    from .pipelines.langgraph_pipeline import ScrapingPipeline, ScrapingState
except ImportError:
    # Crear pipeline dummy temporal
    class ScrapingPipeline:
        def __init__(self): pass
        async def run(self, **kwargs): return {"eventos": [], "errores": []}
    
    class ScrapingState:
        pass

__all__ = [
    "ScrapingEngine",
    "HTMLExtractor", 
    "PDFExtractor",
    "ImageExtractor",
    "ScrapingPipeline",
    "ScrapingState"
]