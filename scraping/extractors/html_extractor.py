# backend/scraping/extractors/html_extractor.py

"""
Extractor HTML usando Playwright
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page

from backend.core import get_settings

settings = get_settings()


class HTMLExtractor:
    """
    Extractor para contenido HTML usando Playwright
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
    
    async def extract(self, url: str, schema: Dict, config: Dict) -> List[Dict]:
        """
        Extraer eventos de una página HTML
        
        Args:
            url: URL a procesar
            schema: Schema de extracción con campos y selectores
            config: Configuración específica de scraping
        
        Returns:
            Lista de eventos extraídos
        """
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=settings.playwright_headless
            )
            
            try:
                page = await browser.new_page()
                
                # Configurar headers si se especifican
                if config.get("headers"):
                    await page.set_extra_http_headers(config["headers"])
                
                # Ir a la página
                await page.goto(url, timeout=settings.playwright_timeout)
                
                # Esperar selector si se especifica
                if config.get("wait_for_selector"):
                    await page.wait_for_selector(
                        config["wait_for_selector"],
                        timeout=settings.playwright_timeout
                    )
                
                # Scroll si se especifica
                if config.get("scroll_to_bottom"):
                    await self._scroll_to_bottom(page)
                
                # Extraer eventos usando el schema
                eventos = await self._extract_events_from_page(page, schema)
                
                return eventos
                
            finally:
                await browser.close()
    
    async def _scroll_to_bottom(self, page: Page) -> None:
        """
        Hacer scroll hasta abajo para cargar contenido dinámico
        """
        await page.evaluate("""
            () => {
                return new Promise((resolve) => {
                    var totalHeight = 0;
                    var distance = 100;
                    var timer = setInterval(() => {
                        var scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;

                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 100);
                });
            }
        """)
    
    async def _extract_events_from_page(self, page: Page, schema: Dict) -> List[Dict]:
        """
        Extraer eventos de la página usando el schema definido
        """
        eventos = []
        campos = schema.get("campos", {})
        filtros = schema.get("filtros", {})
        
        # Buscar contenedores de eventos
        containers_selector = self._get_container_selector(campos)
        
        # Si tenemos un selector de contenedor específico, úsalo
        if "contenedor_eventos" in schema:
            containers = await page.query_selector_all(schema["contenedor_eventos"])
        else:
            # Intentar detectar contenedores automáticamente
            containers = await self._detect_event_containers(page, campos)
        
        for container in containers:
            try:
                evento = await self._extract_single_event(container, campos, page)
                
                # Aplicar filtros
                if self._passes_filters(evento, filtros):
                    eventos.append(evento)
                    
            except Exception as e:
                # Log error pero continúa con otros eventos
                print(f"Error extrayendo evento: {e}")
                continue
        
        return eventos
    
    def _get_container_selector(self, campos: Dict) -> str:
        """
        Generar selector de contenedor basado en los campos
        """
        # Buscar elementos que contengan múltiples campos de evento
        common_selectors = [
            ".evento", ".event", ".card", ".item",
            "[class*='evento']", "[class*='event']",
            "article", ".post", ".entry"
        ]
        return ", ".join(common_selectors)
    
    async def _detect_event_containers(self, page: Page, campos: Dict) -> List:
        """
        Detectar automáticamente contenedores de eventos
        """
        # Buscar elementos que contengan campos clave
        titulo_selector = campos.get("titulo", {}).get("selector", "")
        fecha_selector = campos.get("fecha", {}).get("selector", "")
        
        if titulo_selector and fecha_selector:
            # Buscar elementos padre que contengan tanto título como fecha
            containers = await page.query_selector_all(f"""
                *:has({titulo_selector}):has({fecha_selector})
            """)
            
            if containers:
                return containers
        
        # Fallback: buscar usando selectores comunes
        container_selector = self._get_container_selector(campos)
        return await page.query_selector_all(container_selector)
    
    async def _extract_single_event(self, container, campos: Dict, page: Page) -> Dict:
        """
        Extraer un evento individual de su contenedor
        """
        evento = {}
        
        for campo_nombre, campo_config in campos.items():
            try:
                valor = await self._extract_field_value(
                    container, campo_config, page
                )
                
                if valor:
                    evento[campo_nombre] = valor
                elif campo_config.get("default"):
                    evento[campo_nombre] = campo_config["default"]
                    
            except Exception as e:
                if campo_config.get("requerido", False):
                    raise Exception(f"Campo requerido '{campo_nombre}' no encontrado: {e}")
                elif campo_config.get("default"):
                    evento[campo_nombre] = campo_config["default"]
        
        # Añadir metadatos
        evento["url_original"] = page.url
        evento["fecha_extraccion"] = datetime.now().isoformat()
        
        return evento
    
    async def _extract_field_value(self, container, campo_config: Dict, page: Page) -> Optional[str]:
        """
        Extraer valor de un campo específico
        """
        selector = campo_config.get("selector")
        tipo = campo_config.get("tipo", "text")
        
        if not selector:
            return None
        
        try:
            element = await container.query_selector(selector)
            if not element:
                return None
            
            # Extraer valor según el tipo
            if tipo == "text":
                valor = await element.inner_text()
            elif tipo == "html":
                valor = await element.inner_html()
            elif tipo == "attribute":
                attr_name = campo_config.get("attribute", "href")
                valor = await element.get_attribute(attr_name)
            else:
                valor = await element.inner_text()
            
            # Limpiar y procesar valor
            if valor:
                valor = self._clean_text(valor)
                
                # Procesar según tipo
                if tipo == "date":
                    valor = self._parse_date(valor, campo_config.get("formato"))
                elif tipo == "price":
                    valor = self._parse_price(valor)
            
            return valor
            
        except Exception:
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Limpiar texto extraído
        """
        if not text:
            return ""
        
        # Limpiar espacios y caracteres especiales
        text = " ".join(text.split())
        text = text.strip()
        
        return text
    
    def _parse_date(self, date_str: str, formato: Optional[str] = None) -> Optional[str]:
        """
        Parsear fecha desde string
        """
        try:
            # Implementar parsing de fechas común en español
            # Por ahora retorna tal como viene
            return date_str
        except Exception:
            return None
    
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
        
        # Extraer números y símbolo de euro
        import re
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return f"{numbers[0]}€"
        
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
        
        import re
        numbers = re.findall(r'(\d+(?:\.\d+)?)', precio_str)
        if numbers:
            return float(numbers[0])
        
        return None