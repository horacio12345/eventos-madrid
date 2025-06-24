# backend/scraping/extractors/__init__.py

"""
Extractors para diferentes tipos de contenido
"""

try:
    from .html_extractor import HTMLExtractor
except ImportError:
    class HTMLExtractor:
        def __init__(self): pass
        async def extract(self, url, schema, config): return []

try:
    from .pdf_extractor import PDFExtractor
except ImportError:
    class PDFExtractor:
        def __init__(self): pass
        async def extract(self, url, schema, config): return []

try:
    from .image_extractor import ImageExtractor
except ImportError:
    class ImageExtractor:
        def __init__(self): pass
        async def extract(self, url, schema, config): return []

__all__ = ["HTMLExtractor", "PDFExtractor", "ImageExtractor"]