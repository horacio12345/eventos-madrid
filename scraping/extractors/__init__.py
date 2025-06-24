# scraping/extractors/__init__.py

"""
Extractors para diferentes tipos de contenido
"""
from .html_extractor import HTMLExtractor
from .pdf_extractor import PDFExtractor
from .image_extractor import ImageExtractor

__all__ = ["HTMLExtractor", "PDFExtractor", "ImageExtractor"]