# api/routes/eventos.py

"""
Endpoints públicos para eventos - CON DEDUPLICACIÓN EN BACKEND
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, distinct
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core import get_db
from core.models import Evento

router = APIRouter()


@router.get("/eventos")
def get_eventos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    limite: int = Query(100, le=1000, description="Límite de eventos"),
    db: Session = Depends(get_db),
):
    """
    Obtener lista de eventos activos ordenados por fecha - CON DEDUPLICACIÓN
    """
    # Subquery para deduplicar por título + fecha_inicio (tomar el primer ID de cada grupo)
    subquery = (
        db.query(
            func.min(Evento.id).label("id")
        )
        .filter(
            and_(Evento.activo == True, Evento.fecha_inicio >= datetime.now().date())
        )
        .group_by(Evento.titulo, Evento.fecha_inicio)
        .subquery()
    )
    
    # Query principal usando los IDs únicos
    query = db.query(Evento).filter(
        Evento.id.in_(db.query(subquery.c.id))
    )

    if categoria:
        query = query.filter(Evento.categoria == categoria)

    eventos = query.order_by(Evento.fecha_inicio).limit(limite).all()

    return [
        {
            "id": evento.id,
            "titulo": evento.titulo,
            "categoria": evento.categoria,
            "precio": evento.precio,
            "fecha_inicio": (
                evento.fecha_inicio.isoformat() if evento.fecha_inicio else None
            ),
            "fecha_fin": evento.fecha_fin.isoformat() if evento.fecha_fin else None,
            "ubicacion": evento.ubicacion,
            "descripcion": evento.descripcion,
            "fuente_nombre": evento.fuente_nombre,
            "datos_extra": evento.datos_extra or {},
        }
        for evento in eventos
    ]


@router.get("/eventos/{evento_id}")
def get_evento_detail(evento_id: int, db: Session = Depends(get_db)):
    """
    Obtener detalle completo de un evento específico
    """
    evento = (
        db.query(Evento)
        .filter(and_(Evento.id == evento_id, Evento.activo == True))
        .first()
    )

    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "categoria": evento.categoria,
        "precio": evento.precio,
        "fecha_inicio": (
            evento.fecha_inicio.isoformat() if evento.fecha_inicio else None
        ),
        "fecha_fin": evento.fecha_fin.isoformat() if evento.fecha_fin else None,
        "ubicacion": evento.ubicacion,
        "descripcion": evento.descripcion,
        "fuente_nombre": evento.fuente_nombre,
        "url_original": evento.url_original,
        "ultima_actualizacion": evento.ultima_actualizacion.isoformat(),
        "datos_extra": evento.datos_extra or {},
    }


@router.get("/categorias")
def get_categorias(db: Session = Depends(get_db)):
    """
    Obtener lista de categorías disponibles con conteo de eventos - CON DEDUPLICACIÓN
    """
    # Subquery para obtener eventos únicos (misma lógica que /eventos)
    subquery = (
        db.query(
            func.min(Evento.id).label("id")
        )
        .filter(
            and_(Evento.activo == True, Evento.fecha_inicio >= datetime.now().date())
        )
        .group_by(Evento.titulo, Evento.fecha_inicio)
        .subquery()
    )
    
    # Contar categorías usando solo eventos únicos
    result = (
        db.query(Evento.categoria, func.count(Evento.id).label("total"))
        .filter(Evento.id.in_(db.query(subquery.c.id)))
        .group_by(Evento.categoria)
        .all()
    )

    return [{"categoria": cat, "total_eventos": total} for cat, total in result]