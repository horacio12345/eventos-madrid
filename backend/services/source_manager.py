# backend/services/source_manager.py

"""
Servicio para gestionar fuentes web de scraping
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from backend.core import FuenteWeb, get_settings

settings = get_settings()


class SourceManager:
    """
    Servicio para gestionar fuentes web y su configuración
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_source(self, source_data: Dict, created_by: str = "admin") -> FuenteWeb:
        """
        Crear nueva fuente web
        """
        # Validar datos de entrada
        self._validate_source_data(source_data)
        
        # Verificar que no existe una fuente con el mismo nombre
        existing = self.db.query(FuenteWeb).filter(
            FuenteWeb.nombre == source_data["nombre"]
        ).first()
        
        if existing:
            raise ValueError(f"Ya existe una fuente con el nombre '{source_data['nombre']}'")
        
        # Crear nueva fuente
        fuente = FuenteWeb(
            nombre=source_data["nombre"],
            url=source_data["url"],
            tipo=source_data["tipo"],
            schema_extraccion=source_data.get("schema_extraccion", {}),
            mapeo_campos=source_data.get("mapeo_campos", {}),
            configuracion_scraping=source_data.get("configuracion_scraping", {}),
            frecuencia_actualizacion=source_data.get("frecuencia_actualizacion", settings.default_update_frequency),
            activa=source_data.get("activa", True),
            creado_por=created_by
        )
        
        self.db.add(fuente)
        self.db.commit()
        self.db.refresh(fuente)
        
        return fuente
    
    def update_source(self, source_id: int, update_data: Dict) -> FuenteWeb:
        """
        Actualizar fuente existente
        """
        fuente = self.db.query(FuenteWeb).filter(FuenteWeb.id == source_id).first()
        
        if not fuente:
            raise ValueError(f"Fuente con ID {source_id} no encontrada")
        
        # Validar datos de actualización
        if "nombre" in update_data or "url" in update_data or "tipo" in update_data:
            self._validate_source_data(update_data, partial=True)
        
        # Actualizar campos
        for key, value in update_data.items():
            if hasattr(fuente, key):
                setattr(fuente, key, value)
        
        self.db.commit()
        return fuente
    
    def delete_source(self, source_id: int) -> bool:
        """
        Eliminar fuente
        """
        fuente = self.db.query(FuenteWeb).filter(FuenteWeb.id == source_id).first()
        
        if not fuente:
            raise ValueError(f"Fuente con ID {source_id} no encontrada")
        
        self.db.delete(fuente)
        self.db.commit()
        return True
    
    def get_source(self, source_id: int) -> Optional[FuenteWeb]:
        """
        Obtener fuente por ID
        """
        return self.db.query(FuenteWeb).filter(FuenteWeb.id == source_id).first()
    
    def get_active_sources(self) -> List[FuenteWeb]:
        """
        Obtener todas las fuentes activas
        """
        return self.db.query(FuenteWeb).filter(FuenteWeb.activa == True).all()
    
    def get_all_sources(self) -> List[FuenteWeb]:
        """
        Obtener todas las fuentes
        """
        return self.db.query(FuenteWeb).all()
    
    def toggle_source_status(self, source_id: int) -> FuenteWeb:
        """
        Cambiar estado activo/inactivo de una fuente
        """
        fuente = self.get_source(source_id)
        
        if not fuente:
            raise ValueError(f"Fuente con ID {source_id} no encontrada")
        
        fuente.activa = not fuente.activa
        self.db.commit()
        
        return fuente
    
    def update_source_status(self, source_id: int, estado: str, error: str = None) -> FuenteWeb:
        """
        Actualizar estado de ejecución de una fuente
        """
        fuente = self.get_source(source_id)
        
        if not fuente:
            raise ValueError(f"Fuente con ID {source_id} no encontrada")
        
        fuente.ultima_ejecucion = datetime.now()
        fuente.ultimo_estado = estado
        
        if error:
            fuente.ultimo_error = error
        else:
            fuente.ultimo_error = None
        
        self.db.commit()
        return fuente
    
    def get_sources_for_execution(self) -> List[FuenteWeb]:
        """
        Obtener fuentes que están listas para ejecutar
        (activas y que cumplan criterios de programación)
        """
        # Por simplicidad, devolver todas las activas
        # En el futuro se puede añadir lógica de cron más compleja
        return self.get_active_sources()
    
    def create_default_source_template(self, tipo: str) -> Dict:
        """
        Crear plantilla por defecto para nuevo tipo de fuente
        """
        templates = {
            "HTML": {
                "schema_extraccion": {
                    "campos": {
                        "titulo": {
                            "selector": ".evento-titulo, .title, h2, h3",
                            "tipo": "text",
                            "requerido": True
                        },
                        "fecha": {
                            "selector": ".evento-fecha, .fecha, .date",
                            "tipo": "date",
                            "formato": "%d/%m/%Y",
                            "requerido": True
                        },
                        "precio": {
                            "selector": ".evento-precio, .precio, .price",
                            "tipo": "text",
                            "default": "Gratis"
                        },
                        "ubicacion": {
                            "selector": ".evento-lugar, .ubicacion, .location",
                            "tipo": "text"
                        },
                        "descripcion": {
                            "selector": ".evento-descripcion, .descripcion, .description",
                            "tipo": "text"
                        }
                    },
                    "filtros": {
                        "precio_maximo": 15,
                        "palabras_clave": ["mayores", "senior", "tercera edad"],
                        "excluir_palabras": ["niños", "infantil", "bebé"]
                    }
                },
                "mapeo_campos": {
                    "titulo": "titulo",
                    "fecha": "fecha_inicio",
                    "precio": "precio",
                    "ubicacion": "ubicacion",
                    "descripcion": "descripcion"
                },
                "configuracion_scraping": {
                    "wait_for_selector": ".eventos-container, .events, .lista-eventos",
                    "scroll_to_bottom": False,
                    "timeout": 30000,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (compatible; EventBot/1.0)"
                    }
                }
            },
            
            "PDF": {
                "schema_extraccion": {
                    "campos": {
                        "titulo": {
                            "pattern": "(?i)^(.+?)(?=\\s*-\\s*\\d|\\s*\\.|$)",
                            "tipo": "text",
                            "requerido": True
                        },
                        "fecha": {
                            "pattern": "\\d{1,2}[/-]\\d{1,2}[/-]\\d{4}",
                            "tipo": "date",
                            "formato": "%d/%m/%Y",
                            "requerido": True
                        },
                        "precio": {
                            "pattern": "(?:gratis|gratuito|\\d+[€\\s]*euros?)",
                            "tipo": "text",
                            "default": "Gratis"
                        }
                    },
                    "filtros": {
                        "precio_maximo": 15,
                        "palabras_clave": ["mayores", "senior"]
                    }
                },
                "mapeo_campos": {
                    "titulo": "titulo",
                    "fecha": "fecha_inicio",
                    "precio": "precio"
                },
                "configuracion_scraping": {
                    "ocr_enabled": True,
                    "language": "spa",
                    "dpi": 300
                }
            }
        }
        
        return templates.get(tipo, {})
    
    def _validate_source_data(self, source_data: Dict, partial: bool = False) -> None:
        """
        Validar datos de fuente
        """
        required_fields = ["nombre", "url", "tipo"]
        
        if not partial:
            for field in required_fields:
                if field not in source_data or not source_data[field]:
                    raise ValueError(f"Campo requerido '{field}' faltante o vacío")
        
        # Validar tipo
        if "tipo" in source_data:
            valid_types = ["HTML", "PDF", "IMAGE"]
            if source_data["tipo"] not in valid_types:
                raise ValueError(f"Tipo '{source_data['tipo']}' no válido. Debe ser uno de: {valid_types}")
        
        # Validar URL
        if "url" in source_data:
            url = source_data["url"]
            if not url.startswith(("http://", "https://")):
                raise ValueError("URL debe comenzar con http:// o https://")
        
        # Validar nombre
        if "nombre" in source_data:
            nombre = source_data["nombre"]
            if len(nombre) < 3 or len(nombre) > 100:
                raise ValueError("Nombre debe tener entre 3 y 100 caracteres")
    
    def export_source_config(self, source_id: int) -> Dict:
        """
        Exportar configuración de fuente para backup/compartir
        """
        fuente = self.get_source(source_id)
        
        if not fuente:
            raise ValueError(f"Fuente con ID {source_id} no encontrada")
        
        return {
            "nombre": fuente.nombre,
            "url": fuente.url,
            "tipo": fuente.tipo,
            "schema_extraccion": fuente.schema_extraccion,
            "mapeo_campos": fuente.mapeo_campos,
            "configuracion_scraping": fuente.configuracion_scraping,
            "frecuencia_actualizacion": fuente.frecuencia_actualizacion,
            "exported_at": datetime.now().isoformat()
        }
    
    def import_source_config(self, config_data: Dict, created_by: str = "admin") -> FuenteWeb:
        """
        Importar configuración de fuente desde backup
        """
        # Limpiar datos de exportación
        config_clean = {k: v for k, v in config_data.items() if k != "exported_at"}
        
        return self.create_source(config_clean, created_by)