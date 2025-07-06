# backend/services/event_normalizer.py

"""
Servicio para normalizar y validar eventos extraídos
"""
import hashlib
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from core import get_settings

settings = get_settings()


class EventNormalizer:
    """
    Servicio para normalizar eventos desde diferentes fuentes a formato estándar
    """

    # Categorías válidas del sistema
    CATEGORIAS_VALIDAS = [
        "Cultura",
        "Deporte y Salud",
        "Formación",
        "Cine",
        "Paseos y Excursiones",
        "Ocio y Social",
    ]

    # Mapeo de palabras clave a categorías
    CATEGORIA_KEYWORDS = {
        "Cultura": [
            "teatro",
            "música",
            "concierto",
            "museo",
            "exposición",
            "cultura",
            "arte",
            "ópera",
        ],
        "Deporte y Salud": [
            "deporte",
            "gimnasia",
            "caminar",
            "salud",
            "ejercicio",
            "físico",
            "yoga",
            "pilates",
        ],
        "Formación": [
            "taller",
            "curso",
            "charla",
            "conferencia",
            "formación",
            "aprender",
            "educación",
        ],
        "Cine": [
            "cine",
            "película",
            "film",
            "documental",
            "proyección",
            "cortometraje",
        ],
        "Paseos y Excursiones": [
            "paseo",
            "excursión",
            "visita",
            "ruta",
            "senderismo",
            "parque",
            "jardín",
        ],
        "Ocio y Social": [
            "fiesta",
            "encuentro",
            "social",
            "baile",
            "juegos",
            "tertulia",
            "actividad",
        ],
    }

    def normalize_event(self, evento_raw: Dict, mapeo_campos: Dict) -> Optional[Dict]:
        """
        Normalizar un evento individual desde datos raw
        """
        try:
            # Aplicar mapeo básico de campos
            evento_normalizado = self._apply_field_mapping(evento_raw, mapeo_campos)

            # Normalizar campos específicos
            evento_normalizado = self._normalize_fields(evento_normalizado)

            # Validar evento normalizado
            if not self._validate_event(evento_normalizado):
                return None

            # Generar hash único
            evento_normalizado["hash_contenido"] = self._generate_hash(
                evento_normalizado
            )

            return evento_normalizado

        except Exception as e:
            print(f"Error normalizando evento: {e}")
            return None

    def _apply_field_mapping(self, evento_raw: Dict, mapeo_campos: Dict) -> Dict:
        """
        Aplicar mapeo de campos desde configuración de fuente
        """
        evento_mapeado = {}

        # Aplicar mapeo definido
        for campo_origen, campo_destino in mapeo_campos.items():
            valor = evento_raw.get(campo_origen)

            if valor:
                if "." in campo_destino:
                    # Manejar campos anidados como "datos_extra.telefono"
                    parts = campo_destino.split(".")
                    if parts[0] == "datos_extra":
                        if "datos_extra" not in evento_mapeado:
                            evento_mapeado["datos_extra"] = {}
                        evento_mapeado["datos_extra"][parts[1]] = valor
                else:
                    evento_mapeado[campo_destino] = valor

        # Conservar campos que no están mapeados en datos_extra
        datos_extra = evento_mapeado.get("datos_extra", {})
        for key, value in evento_raw.items():
            if key not in mapeo_campos and value:
                datos_extra[key] = value

        if datos_extra:
            evento_mapeado["datos_extra"] = datos_extra

        return evento_mapeado

    def _normalize_fields(self, evento: Dict) -> Dict:
        """
        Normalizar campos específicos del evento
        """
        # Normalizar título
        if evento.get("titulo"):
            evento["titulo"] = self._normalize_title(evento["titulo"])

        # Normalizar precio
        evento["precio"] = self._normalize_price(evento.get("precio", ""))

        # Normalizar categoría
        evento["categoria"] = self._normalize_category(evento)

        # Normalizar fechas
        if evento.get("fecha_inicio"):
            evento["fecha_inicio"] = self._normalize_date(evento["fecha_inicio"])

        if evento.get("fecha_fin"):
            evento["fecha_fin"] = self._normalize_date(evento["fecha_fin"])

        # Normalizar ubicación
        if evento.get("ubicacion"):
            evento["ubicacion"] = self._normalize_location(evento["ubicacion"])

        # Normalizar descripción
        if evento.get("descripcion"):
            evento["descripcion"] = self._normalize_description(evento["descripcion"])

        return evento

    def _normalize_title(self, titulo: str) -> str:
        """
        Normalizar título del evento
        """
        if not titulo:
            return ""

        # Limpiar espacios múltiples
        titulo = re.sub(r"\s+", " ", titulo.strip())

        # Capitalizar primera letra de cada palabra importante
        titulo = titulo.title()

        # Limitar longitud
        if len(titulo) > 200:
            titulo = titulo[:197] + "..."

        return titulo

    def _normalize_price(self, precio: str) -> str:
        """
        Normalizar precio del evento
        """
        if not precio:
            return "Gratis"

        precio_lower = precio.lower().strip()

        # Detectar gratuito
        free_words = [
            "gratis",
            "gratuito",
            "libre",
            "sin coste",
            "entrada libre",
            "free",
        ]
        if any(word in precio_lower for word in free_words):
            return "Gratis"

        # Extraer número y euro
        numbers = re.findall(r"(\d+(?:[,\.]\d{1,2})?)", precio)
        if numbers:
            price_num = numbers[0].replace(",", ".")
            return f"{price_num}€"

        return precio if len(precio) < 20 else "Consultar precio"

    def _normalize_category(self, evento: Dict) -> str:
        """
        Normalizar/inferir categoría del evento
        """
        categoria_actual = evento.get("categoria", "")

        # Si ya tiene una categoría válida, mantenerla
        if categoria_actual in self.CATEGORIAS_VALIDAS:
            return categoria_actual

        # Inferir categoría desde título y descripción
        texto_evento = (
            f"{evento.get('titulo', '')} {evento.get('descripcion', '')}".lower()
        )

        # Buscar palabras clave por categoría
        for categoria, keywords in self.CATEGORIA_KEYWORDS.items():
            if any(keyword in texto_evento for keyword in keywords):
                return categoria

        # Categoría por defecto
        return "Ocio y Social"

    def _normalize_date(self, fecha: Any) -> Optional[date]:
        """
        Normalizar fecha a objeto date
        """
        if not fecha:
            return None

        # Si ya es un objeto date/datetime
        if isinstance(fecha, (date, datetime)):
            return fecha.date() if isinstance(fecha, datetime) else fecha

        # Si es string, intentar parsear
        if isinstance(fecha, str):
            return self._parse_date_string(fecha)

        return None

    def _parse_date_string(self, fecha_str: str) -> Optional[date]:
        """
        Parsear fecha desde string con múltiples formatos
        """
        fecha_str = fecha_str.strip()

        # Formatos comunes
        formatos = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%y",
            "%d-%m-%y",
            "%d.%m.%y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d de %B de %Y",
            "%d de %b de %Y",
        ]

        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato).date()
            except ValueError:
                continue

        # Intentar extraer fecha con regex
        date_match = re.search(r"(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})", fecha_str)
        if date_match:
            try:
                day, month, year = date_match.groups()
                return date(int(year), int(month), int(day))
            except ValueError:
                pass

        return None

    def _normalize_location(self, ubicacion: str) -> str:
        """
        Normalizar ubicación del evento
        """
        if not ubicacion:
            return ""

        # Limpiar y capitalizar
        ubicacion = " ".join(ubicacion.split())
        ubicacion = ubicacion.title()

        # Limitar longitud
        if len(ubicacion) > 150:
            ubicacion = ubicacion[:147] + "..."

        return ubicacion

    def _normalize_description(self, descripcion: str) -> str:
        """
        Normalizar descripción del evento
        """
        if not descripcion:
            return ""

        # Limpiar HTML tags si los hay
        descripcion = re.sub(r"<[^>]+>", "", descripcion)

        # Limpiar espacios múltiples
        descripcion = re.sub(r"\s+", " ", descripcion.strip())

        # Limitar longitud
        if len(descripcion) > 1000:
            descripcion = descripcion[:997] + "..."

        return descripcion

    def _validate_event(self, evento: Dict) -> bool:
        """
        Validar que el evento tiene los campos mínimos requeridos
        """
        # Campos obligatorios
        if not evento.get("titulo") or len(evento["titulo"]) < 3:
            return False

        if not evento.get("fecha_inicio"):
            return False

        if evento.get("categoria") not in self.CATEGORIAS_VALIDAS:
            return False

        return True

    def _generate_hash(self, evento: Dict) -> str:
        """
        Generar hash único para detectar duplicados
        """
        # Usar campos clave para hash
        key_content = f"{evento.get('titulo', '')}{evento.get('fecha_inicio', '')}{evento.get('ubicacion', '')}"
        return hashlib.sha256(key_content.encode("utf-8")).hexdigest()

    def batch_normalize(
        self, eventos_raw: List[Dict], mapeo_campos: Dict
    ) -> List[Dict]:
        """
        Normalizar múltiples eventos en lote
        """
        eventos_normalizados = []

        for evento_raw in eventos_raw:
            evento_normalizado = self.normalize_event(evento_raw, mapeo_campos)
            if evento_normalizado:
                eventos_normalizados.append(evento_normalizado)

        return eventos_normalizados
