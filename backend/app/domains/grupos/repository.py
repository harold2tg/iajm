from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.grupos.models import Grupo


def get_by_id(db: Session, grupo_id: uuid.UUID) -> Grupo | None:
    stmt = select(Grupo).where(Grupo.id == grupo_id)
    return db.execute(stmt).scalar_one_or_none()


def get_by_nombre(db: Session, nombre: str) -> Grupo | None:
    stmt = select(Grupo).where(Grupo.nombre == nombre)
    return db.execute(stmt).scalar_one_or_none()


def get_all(db: Session) -> list[Grupo]:
    stmt = select(Grupo).order_by(Grupo.edad_minima)
    return list(db.execute(stmt).scalars().all())


def update(db: Session, grupo: Grupo, **kwargs: object) -> Grupo:
    for key, value in kwargs.items():
        setattr(grupo, key, value)
    db.flush()
    db.refresh(grupo)
    return grupo


def get_grupo_para_edad(db: Session, edad: int) -> Grupo | None:
    stmt = select(Grupo).where(
        Grupo.edad_minima <= edad,
        Grupo.edad_maxima >= edad,
    )
    return db.execute(stmt).scalar_one_or_none()
