#!/usr/bin/env python3
# scripts/seed_sources.py

"""
Script para insertar fuentes web de ejemplo en el sistema
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import SessionLocal
from backend.services.source_manager import SourceManager

def seed_default_sources():
    """
    Insertar fuentes web de ejemplo para Madrid
    """
    print("🌱 Insertando fuentes de ejemplo...")
    
    db = SessionLocal()
    try:
        source_manager = SourceManager(db)
        
        # Fuentes de ejemplo para eventos en Madrid
        fuentes_ejemplo = [
            {
                "nombre": "Ayuntamiento de Madrid - Actividades Mayores",
                "url": "https://www.madrid.es/portales/munimadrid/es/Inicio/Servicios-sociales-y-salud/Personas-mayores/",
                "tipo": "HTML",
                "schema_extraccion": {
                    "campos": {
                        "titulo": {
                            "selector": ".actividad-titulo, h3, .title",
                            "tipo": "text",
                            "requerido": True
                        },
                        "fecha": {
                            "selector": ".fecha, .date, .actividad-fecha",
                            "tipo": "date",
                            "formato": "%d/%m/%Y",
                            "requerido": True
                        },
                        "precio": {
                            "selector": ".precio, .price",
                            "tipo": "text",
                            "default": "Gratis"
                        },
                        "ubicacion": {
                            "selector": ".lugar, .location, .ubicacion",
                            "tipo": "text"
                        },
                        "descripcion": {
                            "selector": ".descripcion, .description",
                            "tipo": "text"
                        }
                    },
                    "filtros": {
                        "precio_maximo": 15,
                        "palabras_clave": ["mayores", "senior", "tercera edad", "adultos"],
                        "excluir_palabras": ["niños", "infantil", "bebé", "jóvenes"]
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
                    "wait_for_selector": ".content-main, .actividades",
                    "scroll_to_bottom": False,
                    "timeout": 30000,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (compatible; EventosBot/1.0)"
                    }
                },
                "frecuencia_actualizacion": "0 9 * * 1",  # Lunes 9:00
                "activa": False  # Inicialmente desactivada para testing
            },
            
            {
                "nombre": "Comunidad de Madrid - Centros Culturales",
                "url": "https://www.comunidad.madrid/servicios/cultura-turismo-deporte/centros-culturales",
                "tipo": "HTML",
                "schema_extraccion": {
                    "campos": {
                        "titulo": {
                            "selector": ".evento-nombre, h2, h3",
                            "tipo": "text",
                            "requerido": True
                        },
                        "fecha": {
                            "selector": ".evento-fecha, .fecha-evento",
                            "tipo": "date",
                            "formato": "%d/%m/%Y",
                            "requerido": True
                        },
                        "precio": {
                            "selector": ".precio-evento, .precio",
                            "tipo": "text",
                            "default": "Gratis"
                        },
                        "ubicacion": {
                            "selector": ".centro-cultural, .ubicacion",
                            "tipo": "text"
                        }
                    },
                    "filtros": {
                        "precio_maximo": 10,
                        "palabras_clave": ["cultura", "teatro", "música", "exposición"],
                        "excluir_palabras": ["infantil", "niños"]
                    }
                },
                "mapeo_campos": {
                    "titulo": "titulo",
                    "fecha": "fecha_inicio",
                    "precio": "precio",
                    "ubicacion": "ubicacion"
                },
                "configuracion_scraping": {
                    "wait_for_selector": ".eventos-lista, .centros-culturales",
                    "scroll_to_bottom": False,
                    "timeout": 30000
                },
                "frecuencia_actualizacion": "0 10 * * 2",  # Martes 10:00
                "activa": False
            },
            
            {
                "nombre": "IMSERSO - Actividades",
                "url": "https://www.imserso.es/imserso_01/el_imserso/actividades/",
                "tipo": "HTML",
                "schema_extraccion": {
                    "campos": {
                        "titulo": {
                            "selector": ".actividad-titulo, h3",
                            "tipo": "text",
                            "requerido": True
                        },
                        "fecha": {
                            "selector": ".fecha-actividad",
                            "tipo": "date",
                            "requerido": True
                        },
                        "descripcion": {
                            "selector": ".actividad-descripcion",
                            "tipo": "text"
                        }
                    },
                    "filtros": {
                        "palabras_clave": ["mayores", "tercera edad", "senior"],
                        "precio_maximo": 5
                    }
                },
                "mapeo_campos": {
                    "titulo": "titulo",
                    "fecha": "fecha_inicio",
                    "descripcion": "descripcion"
                },
                "configuracion_scraping": {
                    "timeout": 30000
                },
                "frecuencia_actualizacion": "0 11 * * 3",  # Miércoles 11:00
                "activa": False
            },
            
            {
                "nombre": "Bibliotecas Municipales Madrid",
                "url": "https://www.madrid.es/portales/munimadrid/es/Inicio/Cultura-y-ocio/Bibliotecas/",
                "tipo": "HTML",
                "schema_extraccion": {
                    "campos": {
                        "titulo": {
                            "selector": ".evento-biblioteca, .actividad-titulo",
                            "tipo": "text",
                            "requerido": True
                        },
                        "fecha": {
                            "selector": ".fecha-evento",
                            "tipo": "date",
                            "requerido": True
                        },
                        "ubicacion": {
                            "selector": ".biblioteca-nombre",
                            "tipo": "text"
                        },
                        "descripcion": {
                            "selector": ".evento-descripcion",
                            "tipo": "text"
                        }
                    },
                    "filtros": {
                        "palabras_clave": ["lectura", "club", "tertulia", "charla", "taller"],
                        "precio_maximo": 0  # Solo eventos gratuitos
                    }
                },
                "mapeo_campos": {
                    "titulo": "titulo",
                    "fecha": "fecha_inicio",
                    "ubicacion": "ubicacion",
                    "descripcion": "descripcion"
                },
                "configuracion_scraping": {
                    "wait_for_selector": ".eventos-biblioteca",
                    "timeout": 30000
                },
                "frecuencia_actualizacion": "0 14 * * 4",  # Jueves 14:00
                "activa": False
            }
        ]
        
        # Insertar fuentes
        sources_created = 0
        for fuente_data in fuentes_ejemplo:
            try:
                source_manager.create_source(fuente_data, "sistema")
                sources_created += 1
                print(f"✅ Fuente creada: {fuente_data['nombre']}")
            except ValueError as e:
                if "Ya existe una fuente" in str(e):
                    print(f"⚠️  Ya existe: {fuente_data['nombre']}")
                else:
                    print(f"❌ Error creando {fuente_data['nombre']}: {e}")
            except Exception as e:
                print(f"❌ Error inesperado creando {fuente_data['nombre']}: {e}")
        
        print(f"\n🎉 Proceso completado! {sources_created} fuentes nuevas creadas")
        print("\n📋 NOTA: Todas las fuentes están DESACTIVADAS por defecto.")
        print("   Usa el panel de administración para activarlas y configurarlas.")
        
    except Exception as e:
        print(f"❌ Error general insertando fuentes: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_sources()