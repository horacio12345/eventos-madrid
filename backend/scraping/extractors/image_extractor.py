# scraping/extractors/image_extractor.py

"""
Extractor de imágenes usando OCR con Tesseract
"""
import re
import requests
from typing import Dict, List, Optional
from datetime import datetime
from PIL import Image
import pytesseract
import io

from backend.core import get_settings

settings = get_settings()


class ImageExtractor:
    """
    Extractor para contenido de imágenes usando OCR
    """
    
    def __init__(self):
        # Configurar Tesseract si hay path específico
        if hasattr(settings, 'tesseract_path') and settings.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path
    
    async def extract(self, url: str, schema: Dict, config: Dict) -> List[Dict]:
        """
        Extraer eventos de una imagen usando OCR
        
        Args:
            url: URL de la imagen a procesar
            schema: Schema de extracción con campos y patrones
            config: Configuración específica de OCR
        
        Returns:
            Lista de eventos extraídos
        """
        try:
            # Descargar y cargar imagen
            image = await self._load_image_from_url(url)
            
            # Extraer texto usando OCR
            texto = self._extract_text_from_image(image, config)
            
            # Extraer eventos usando el schema
            eventos = self._extract_events_from_text(texto, schema)
            
            # Añadir metadatos
            for evento in eventos:
                evento["url_original"] = url
                evento["fecha_extraccion"] = datetime.now().isoformat()
                evento["metodo_extraccion"] = "OCR"
            
            return eventos
            
        except Exception as e:
            raise Exception(f"Error procesando imagen {url}: {str(e)}")
    
    async def _load_image_from_url(self, url: str) -> Image.Image:
        """
        Cargar imagen desde URL
        """
        try:
            response = requests.get(url, timeout=settings.request_timeout)
            response.raise_for_status()
            
            # Cargar imagen desde bytes
            image = Image.open(io.BytesIO(response.content))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            raise Exception(f"Error cargando imagen: {str(e)}")
    
    def _extract_text_from_image(self, image: Image.Image, config: Dict) -> str:
        """
        Extraer texto de imagen usando OCR
        """
        try:
            # Configurar OCR
            ocr_config = self._build_ocr_config(config)
            
            # Preprocesar imagen si es necesario
            processed_image = self._preprocess_image(image, config)
            
            # Extraer texto
            texto = pytesseract.image_to_string(
                processed_image, 
                lang=config.get("language", "spa"),
                config=ocr_config
            )
            
            return texto
            
        except Exception as e:
            raise Exception(f"Error en OCR: {str(e)}")
    
    def _build_ocr_config(self, config: Dict) -> str:
        """
        Construir configuración de Tesseract
        """
        ocr_options = []
        
        # DPI
        dpi = config.get("dpi", 300)
        ocr_options.append(f"--dpi {dpi}")
        
        # PSM (Page Segmentation Mode)
        psm = config.get("psm", 6)  # 6 = single uniform block of text
        ocr_options.append(f"--psm {psm}")
        
        # OEM (OCR Engine Mode)
        oem = config.get("oem", 3)  # 3 = default (LSTM + legacy)
        ocr_options.append(f"--oem {oem}")
        
        return " ".join(ocr_options)
    
    def _preprocess_image(self, image: Image.Image, config: Dict) -> Image.Image:
        """
        Preprocesar imagen para mejorar OCR
        """
        processed = image.copy()
        
        # Redimensionar si es muy pequeña
        width, height = processed.size
        if width < 800 or height < 600:
            scale_factor = max(800/width, 600/height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            processed = processed.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Aplicar filtros adicionales si se especifican
        if config.get("enhance_contrast", False):
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(1.5)
        
        if config.get("enhance_sharpness", False):
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(processed)
            processed = enhancer.enhance(2.0)
        
        return processed
    
    def _extract_events_from_text(self, texto: str, schema: Dict) -> List[Dict]:
        """
        Extraer eventos del texto OCR usando patrones regex
        """
        eventos = []
        campos = schema.get("campos", {})
        filtros = schema.get("filtros", {})
        
        # Dividir texto en líneas/secciones
        secciones = self._split_text_into_sections(texto)
        
        for seccion in secciones:
            try:
                evento = self._extract_single_event_from_text(seccion, campos)
                
                # Aplicar filtros
                if evento and self._passes_filters(evento, filtros):
                    eventos.append(evento)
                    
            except Exception as e:
                # Log error pero continúa con otras secciones
                print(f"Error extrayendo evento de texto OCR: {e}")
                continue
        
        return eventos
    
    def _split_text_into_sections(self, texto: str) -> List[str]:
        """
        Dividir texto OCR en secciones potenciales de eventos
        """
        # Limpiar texto OCR
        texto = self._clean_ocr_text(texto)
        
        # Dividir por patrones comunes de eventos
        separators = [
            r'\n(?=\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',  # Fechas
            r'\n(?=[A-ZÁÉÍÓÚ][A-Za-záéíóúñü\s]{10,})',        # Títulos
            r'\n\s*[-•]\s*',                                   # Listas
            r'\n\s*\d+[\.\)]\s*',                             # Numeradas
        ]
        
        for pattern in separators:
            secciones = re.split(pattern, texto)
            if len(secciones) > 1:
                return [s.strip() for s in secciones if len(s.strip()) > 20]
        
        # Dividir por líneas si no hay patrones
        lineas = texto.split('\n')
        return [linea.strip() for linea in lineas if len(linea.strip()) > 20]
    
    def _clean_ocr_text(self, texto: str) -> str:
        """
        Limpiar texto obtenido por OCR
        """
        if not texto:
            return ""
        
        # Corregir errores comunes de OCR
        texto = re.sub(r'[|!1]', 'l', texto)  # Correcciones de caracteres confundidos
        texto = re.sub(r'0(?=[a-zA-Z])', 'o', texto)  # 0 → o antes de letras
        texto = re.sub(r'5(?=[a-zA-Z])', 's', texto)  # 5 → s antes de letras
        
        # Limpiar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        # Eliminar caracteres extraños
        texto = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]€\$\%\+\=\@\#]', ' ', texto)
        
        return texto.strip()
    
    def _extract_single_event_from_text(self, texto: str, campos: Dict) -> Optional[Dict]:
        """
        Extraer un evento individual del texto OCR
        """
        evento = {}
        
        for campo_nombre, campo_config in campos.items():
            try:
                valor = self._extract_field_with_pattern(texto, campo_config)
                
                if valor:
                    evento[campo_nombre] = valor
                elif campo_config.get("default"):
                    evento[campo_nombre] = campo_config["default"]
                    
            except Exception as e:
                if campo_config.get("requerido", False):
                    return None
                elif campo_config.get("default"):
                    evento[campo_nombre] = campo_config["default"]
        
        # Verificar que el evento tiene campos mínimos
        if not evento.get("titulo") and not evento.get("fecha"):
            return None
        
        return evento
    
    def _extract_field_with_pattern(self, texto: str, campo_config: Dict) -> Optional[str]:
        """
        Extraer valor de un campo usando patrones regex adaptados para OCR
        """
        pattern = campo_config.get("pattern")
        tipo = campo_config.get("tipo", "text")
        
        if not pattern:
            return None
        
        try:
            # Buscar patrón en el texto (case insensitive para OCR)
            match = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
            
            if match:
                valor = match.group(1) if match.groups() else match.group(0)
                valor = self._clean_extracted_value(valor)
                
                # Procesar según tipo
                if tipo == "date":
                    valor = self._parse_date_from_ocr(valor, campo_config.get("formato"))
                elif tipo == "price":
                    valor = self._parse_price_from_ocr(valor)
                
                return valor
                
        except Exception:
            return None
        
        return None
    
    def _clean_extracted_value(self, valor: str) -> str:
        """
        Limpiar valor extraído específicamente para texto OCR
        """
        if not valor:
            return ""
        
        # Limpiar espacios
        valor = " ".join(valor.split())
        
        # Corregir algunos errores comunes de OCR
        valor = re.sub(r'\bl\b', 'I', valor)  # l solitaria → I
        valor = re.sub(r'\b0\b', 'O', valor)  # 0 solitario → O
        
        return valor.strip()
    
    def _parse_date_from_ocr(self, date_str: str, formato: Optional[str] = None) -> Optional[str]:
        """
        Parsear fecha desde texto OCR (más tolerante a errores)
        """
        if not date_str:
            return None
        
        # Patrones tolerantes para errores de OCR
        date_patterns = [
            r'(\d{1,2})[\/\-\.\s](\d{1,2})[\/\-\.\s](\d{4})',
            r'(\d{1,2})[\/\-\.\s](\d{1,2})[\/\-\.\s](\d{2})',
            r'(\d{1,2})\s*de\s*(\w+)\s*de\s*(\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return date_str
    
    def _parse_price_from_ocr(self, price_str: str) -> str:
        """
        Parsear precio desde texto OCR
        """
        if not price_str:
            return "Gratis"
        
        price_lower = price_str.lower()
        
        # Detectar gratuito (tolerante a errores OCR)
        free_patterns = [
            r'grat[iu]s?',
            r'gratuit[oa]?',
            r'libre?',
            r'sin\s*cost[eo]',
            r'entrada\s*libre'
        ]
        
        for pattern in free_patterns:
            if re.search(pattern, price_lower):
                return "Gratis"
        
        # Buscar números (tolerante a errores OCR)
        euro_pattern = r'(\d+(?:[,\.]\d{1,2})?)\s*[€e]?'
        match = re.search(euro_pattern, price_str)
        if match:
            price = match.group(1).replace(',', '.')
            return f"{price}€"
        
        return price_str
    
    def _passes_filters(self, evento: Dict, filtros: Dict) -> bool:
        """
        Verificar filtros (mismo que otros extractors)
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
        
        numbers = re.findall(r'(\d+(?:[,\.]\d+)?)', precio_str)
        if numbers:
            price_str = numbers[0].replace(',', '.')
            return float(price_str)
        
        return None