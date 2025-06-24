#!/usr/bin/env python3
# scripts/init_db.py

"""
Script para inicializar la base de datos SQLite con las tablas necesarias
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.core import create_tables, get_settings, Configuracion
from backend.core.database import SessionLocal

def init_database():
    """
    Inicializar base de datos y configuración inicial
    """
    print("🗄️  Inicializando base de datos...")
    
    try:
        # Crear todas las tablas
        create_tables()
        print("✅ Tablas creadas correctamente")
        
        # Insertar configuración inicial
        init_default_config()
        print("✅ Configuración inicial insertada")
        
        print("🎉 Base de datos inicializada correctamente!")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        sys.exit(1)

def init_default_config():
    """
    Insertar configuración inicial del sistema
    """
    db = SessionLocal()
    try:
        # Configuraciones por defecto
        default_configs = [
            {
                "clave": "sistema_version",
                "valor": "1.0.0",
                "descripcion": "Versión del sistema de eventos"
            },
            {
                "clave": "ultima_inicializacion",
                "valor": "2025-01-01",
                "descripcion": "Fecha de última inicialización del sistema"
            },
            {
                "clave": "precio_maximo_defecto",
                "valor": "15",
                "descripcion": "Precio máximo por defecto para eventos (€)"
            },
            {
                "clave": "frecuencia_scraping_defecto",
                "valor": "0 9 * * 1",
                "descripcion": "Frecuencia por defecto de scraping (lunes 9:00)"
            },
            {
                "clave": "timeout_scraping_defecto",
                "valor": "30",
                "descripcion": "Timeout por defecto para scraping (segundos)"
            },
            {
                "clave": "eventos_activos_dias",
                "valor": "365",
                "descripcion": "Días que los eventos permanecen activos"
            }
        ]
        
        for config_data in default_configs:
            # Verificar si ya existe
            existing = db.query(Configuracion).filter(
                Configuracion.clave == config_data["clave"]
            ).first()
            
            if not existing:
                config = Configuracion(**config_data)
                db.add(config)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_database()