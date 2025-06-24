# scraping/__init__.py

"""
Módulo de scraping inteligente
"""
from .engine import ScrapingEngine
from .extractors import HTMLExtractor, PDFExtractor, ImageExtractor
from .pipelines import ScrapingPipeline, ScrapingState

__all__ = [
    "ScrapingEngine",
    "HTMLExtractor", 
    "PDFExtractor",
    "ImageExtractor",
    "ScrapingPipeline",
    "ScrapingState"
]