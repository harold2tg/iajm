from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.parroquial.models import ActividadParroquial


def crear_actividad(db: Session, **kwargs) -> ActividadParroquial:
    actividad = ActividadParroquial(**kwargs)
    db.add(actividad)
    db.commit()
    db.refresh(actividad)
    return actividad


def get_actividad(db: Session, id: uuid.UUID) -> Optional[ActividadParroquial]:
    return db.get(ActividadParroquial, id)


def listar_actividades(db: Session, skip: int = 0, limit: int = 100) -> list[ActividadParroquial]:
    stmt = select(ActividadParroquial).order_by(ActividadParroquial.fecha.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def marcar_entregado(
    db: Session,
    actividad: ActividadParroquial,
    monto: float,
    fecha: date,
) -> ActividadParroquial:
    actividad.dinero_recolectado = monto
    actividad.fecha_entrega = fecha
    actividad.entregado = True
    db.commit()
    db.refresh(actividad)
    return actividad
