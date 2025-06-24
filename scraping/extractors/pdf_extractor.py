# backend/scraping/extractors/pdf_extractor.py

"""
Extractor PDF usando Docling
"""
import re
from typing import Dict, List, Optional
from datetime import datetime
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption

from backend.core import get_settings

settings = get_settings()


class PDFExtractor:
    """
    Extractor para contenido PDF usando Docling
    """
    
    def __init__(self):
        # Configurar pipeline de PDF con OCR si es necesario
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,  # Activar OCR para PDFs escaneados
            do_table_structure=True  # Extraer estructura de tablas
        )
        
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
    
    async def extract(self, url: str, schema: Dict, config: Dict) -> List[Dict]:
        """
        Extraer eventos de un documento PDF
        
        Args:
            url: URL del PDF a procesar
            schema: Schema de extracción con campos y patrones
            config: Configuración específica de scraping
        
        Returns:
            Lista de eventos extraídos
        """
        try:
            # Convertir PDF usando Docling
            result = self.converter.convert(url)
            
            # Exportar a markdown para facilitar el parsing
            content = result.document.export_to_markdown()
            
            # Extraer eventos usando el schema
            eventos = self._extract_events_from_content(content, schema)
            
            # Añadir metadatos
            for evento in eventos:
                evento["url_original"] = url
                evento["fecha_extraccion"] = datetime.now().isoformat()
            
            return eventos
            
        except Exception as e:
            raise Exception(f"Error procesando PDF {url}: {str(e)}")
    
    def _extract_events_from_content(self, content: str, schema: Dict) -> List[Dict]:
        """
        Extraer eventos del contenido del PDF usando patrones regex
        """
        eventos = []
        campos = schema.get("campos", {})
        filtros = schema.get("filtros", {})
        
        # Dividir contenido en secciones potenciales de eventos
        secciones = self._split_content_into_sections(content)
        
        for seccion in secciones:
            try:
                evento = self._extract_single_event_from_section(seccion, campos)
                
                # Aplicar filtros
                if evento and self._passes_filters(evento, filtros):
                    eventos.append(evento)
                    
            except Exception as e:
                # Log error pero continúa con otras secciones
                print(f"Error extrayendo evento de sección: {e}")
                continue
        
        return eventos
    
    def _split_content_into_sections(self, content: str) -> List[str]:
        """
        Dividir contenido en secciones que pueden contener eventos
        """
        # Patrones comunes para separar eventos en PDFs
        separators = [
            r'\n(?=\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',  # Fechas al inicio de línea
            r'\n(?=[A-ZÁÉÍÓÚ][A-Za-záéíóúñü\s]{10,})',        # Títulos en mayúscula
            r'\n\s*[-•]\s*',                                   # Listas con guiones o bullets
            r'\n\s*\d+[\.\)]\s*',                             # Listas numeradas
            r'\n\s*\*\s*',                                    # Listas con asteriscos
        ]
        
        # Intentar dividir por diferentes patrones
        for pattern in separators:
            secciones = re.split(pattern, content)
            if len(secciones) > 1:
                return [s.strip() for s in secciones if s.strip()]
        
        # Si no se puede dividir, devolver párrafos
        paragrafos = content.split('\n\n')
        return [p.strip() for p in paragrafos if len(p.strip()) > 50]
    
    def _extract_single_event_from_section(self, seccion: str, campos: Dict) -> Optional[Dict]:
        """
        Extraer un evento individual de una sección de texto
        """
        evento = {}
        
        for campo_nombre, campo_config in campos.items():
            try:
                valor = self._extract_field_with_pattern(seccion, campo_config)
                
                if valor:
                    evento[campo_nombre] = valor
                elif campo_config.get("default"):
                    evento[campo_nombre] = campo_config["default"]
                    
            except Exception as e:
                if campo_config.get("requerido", False):
                    return None  # Si un campo requerido falla, descartar evento
                elif campo_config.get("default"):
                    evento[campo_nombre] = campo_config["default"]
        
        # Verificar que el evento tiene campos mínimos
        if not evento.get("titulo") and not evento.get("fecha"):
            return None
        
        return evento
    
    def _extract_field_with_pattern(self, texto: str, campo_config: Dict) -> Optional[str]:
        """
        Extraer valor de un campo usando patrones regex
        """
        pattern = campo_config.get("pattern")
        tipo = campo_config.get("tipo", "text")
        
        if not pattern:
            return None
        
        try:
            # Buscar patrón en el texto
            match = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
            
            if match:
                # Tomar el primer grupo si existe, sino toda la coincidencia
                valor = match.group(1) if match.groups() else match.group(0)
                
                # Limpiar y procesar valor
                valor = self._clean_text(valor)
                
                # Procesar según tipo
                if tipo == "date":
                    valor = self._parse_date(valor, campo_config.get("formato"))
                elif tipo == "price":
                    valor = self._parse_price(valor)
                
                return valor
                
        except Exception:
            return None
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """
        Limpiar texto extraído
        """
        if not text:
            return ""
        
        # Limpiar espacios múltiples y caracteres especiales
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text
    
    def _parse_date(self, date_str: str, formato: Optional[str] = None) -> Optional[str]:
        """
        Parsear fecha desde string usando patrones comunes españoles
        """
        if not date_str:
            return None
        
        # Patrones comunes de fecha en español
        date_patterns = [
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})',     # dd/mm/yyyy
            r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2})',     # dd/mm/yy
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',        # dd de mes de yyyy
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return date_str
    
    def _parse_price(self, price_str: str) -> str:
        """
        Parsear precio desde string
        """
        if not price_str:
            return "Gratis"
        
        price_lower = price_str.lower()
        
        # Detectar palabras que indican gratuito
        free_words = ["gratis", "gratuito", "libre", "sin coste", "entrada libre"]
        if any(word in price_lower for word in free_words):
            return "Gratis"
        
        # Buscar números con euro
        euro_pattern = r'(\d+(?:[,\.]\d{2})?)\s*€?'
        match = re.search(euro_pattern, price_str)
        if match:
            price = match.group(1).replace(',', '.')
            return f"{price}€"
        
        return price_str
    
    def _passes_filters(self, evento: Dict, filtros: Dict) -> bool:
        """
        Verificar si un evento pasa los filtros definidos
        """
        # Filtro precio máximo
        precio_max = filtros.get("precio_maximo")
        if precio_max and evento.get("precio"):
            precio_evento = self._extract_price_number(evento["precio"])
            if precio_evento and precio_evento > precio_max:
                return False
        
        # Filtro palabras clave
        palabras_clave = filtros.get("palabras_clave", [])
        if palabras_clave:
            texto_evento = f"{evento.get('titulo', '')} {evento.get('descripcion', '')}".lower()
            if not any(palabra.lower() in texto_evento for palabra in palabras_clave):
                return False
        
        # Filtro palabras excluidas
        excluir_palabras = filtros.get("excluir_palabras", [])
        if excluir_palabras:
            texto_evento = f"{evento.get('titulo', '')} {evento.get('descripcion', '')}".lower()
            if any(palabra.lower() in texto_evento for palabra in excluir_palabras):
                return False
        
        return True
    
    def _extract_price_number(self, precio_str: str) -> Optional[float]:
        """
        Extraer número de precio
        """
        if not precio_str or precio_str.lower() == "gratis":
            return 0.0
        
        # Buscar números en el string
        numbers = re.findall(r'(\d+(?:[,\.]\d+)?)', precio_str)
        if numbers:
            price_str = numbers[0].replace(',', '.')
            return float(price_str)
        
        return None