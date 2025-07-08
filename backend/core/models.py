# backend/core/models.py

"""
Modelos SQLAlchemy para el proyecto - VERSIÓN LIMPIA
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Evento(Base):
    """
    Modelo para eventos extraídos - Flexible con JSON para campos dinámicos
    """

    __tablename__ = "eventos"

    # ============= CAMPOS BASE OBLIGATORIOS =============
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False, index=True)
    fecha_inicio = Column(DateTime, nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)  # Cultura, Deporte, etc.
    fuente_id = Column(Integer, nullable=False, index=True)
    fuente_nombre = Column(String(100), nullable=False)

    # ============= CAMPOS COMUNES OPCIONALES =============
    precio = Column(String(50))  # "Gratis", "5€", etc.
    ubicacion = Column(String(255))
    descripcion = Column(Text)
    fecha_fin = Column(DateTime)

    # ============= DATOS DINÁMICOS POR FUENTE =============
    datos_extra = Column(JSON)  # Campos específicos de cada fuente
    datos_raw = Column(JSON)  # Datos originales sin procesar (debug)

    # ============= METADATOS DEL SISTEMA =============
    hash_contenido = Column(String(64), index=True)  # Para detectar duplicados
    url_original = Column(String(500))  # URL donde se encontró
    ultima_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    activo = Column(Boolean, default=True, index=True)

    def __repr__(self) -> str:
        return f"<Evento(id={self.id}, titulo='{self.titulo}', fuente='{self.fuente_nombre}')>"


class FuenteWeb(Base):
    """
    Modelo para agentes de procesamiento - Sistema dinámico de extracción
    """

    __tablename__ = "fuentes_web"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    tipo = Column(String(20), nullable=False)  # AGENTE, PDF, etc.

    # ============= CONFIGURACIÓN DE EXTRACCIÓN =============
    schema_extraccion = Column(JSON)  # Define QUÉ campos extraer y CÓMO
    mapeo_campos = Column(JSON)  # Mapeo de campos extraídos -> modelo base
    configuracion_scraping = Column(JSON)  # Config específica (obsoleto)

    # ============= CONFIGURACIÓN DE EJECUCIÓN =============
    frecuencia_actualizacion = Column(String(50), default="0 9 * * 1")  # cron (obsoleto)
    activa = Column(Boolean, default=True, index=True)

    # ============= METADATOS DE EJECUCIÓN =============
    ultima_ejecucion = Column(DateTime)
    ultimo_estado = Column(String(20), default="pending")  # success, error, pending
    ultimo_error = Column(Text)
    eventos_encontrados_ultima_ejecucion = Column(Integer, default=0)

    # ============= METADATOS DEL SISTEMA =============
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    creado_por = Column(String(50), default="admin")

    def __repr__(self) -> str:
        return f"<FuenteWeb(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}')>"


class Configuracion(Base):
    """
    Modelo para configuración general del sistema
    """

    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(50), nullable=False, unique=True, index=True)
    valor = Column(String(255))
    descripcion = Column(String(255))
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Configuracion(clave='{self.clave}', valor='{self.valor}')>"