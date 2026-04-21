from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.domains.encuentros.models import (
    AsistenciaEncuentro,
    Encuentro,
    EstadoAsistenciaEnum,
    LogReaperturaEncuentro,
)


def get_by_id(db: Session, encuentro_id: uuid.UUID) -> Encuentro | None:
    return db.get(Encuentro, encuentro_id)


def get_by_grupo(
    db: Session, grupo_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Encuentro]:
    stmt = (
        select(Encuentro)
        .where(Encuentro.grupo_id == grupo_id)
        .order_by(Encuentro.fecha.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_by_grupo_y_fecha(
    db: Session, grupo_id: uuid.UUID, fecha: date
) -> Encuentro | None:
    stmt = select(Encuentro).where(
        and_(Encuentro.grupo_id == grupo_id, Encuentro.fecha == fecha)
    )
    return db.scalars(stmt).first()


def create(db: Session, **kwargs) -> Encuentro:
    enc = Encuentro(**kwargs)
    db.add(enc)
    db.commit()
    db.refresh(enc)
    return enc


def update(db: Session, encuentro: Encuentro, **kwargs) -> Encuentro:
    for k, v in kwargs.items():
        setattr(encuentro, k, v)
    db.commit()
    db.refresh(encuentro)
    return encuentro


def get_asistencia(
    db: Session, encuentro_id: uuid.UUID, miembro_id: uuid.UUID
) -> AsistenciaEncuentro | None:
    stmt = select(AsistenciaEncuentro).where(
        and_(
            AsistenciaEncuentro.encuentro_id == encuentro_id,
            AsistenciaEncuentro.miembro_id == miembro_id,
        )
    )
    return db.scalars(stmt).first()


def get_asistencias_encuentro(
    db: Session, encuentro_id: uuid.UUID
) -> list[AsistenciaEncuentro]:
    stmt = select(AsistenciaEncuentro).where(
        AsistenciaEncuentro.encuentro_id == encuentro_id
    )
    return list(db.scalars(stmt).all())


def create_asistencia(db: Session, **kwargs) -> AsistenciaEncuentro:
    a = AsistenciaEncuentro(**kwargs)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def update_asistencia(
    db: Session,
    asistencia: AsistenciaEncuentro,
    estado: EstadoAsistenciaEnum,
    registrado_por: uuid.UUID | None,
) -> AsistenciaEncuentro:
    asistencia.estado = estado
    asistencia.registrado_por = registrado_por
    db.commit()
    db.refresh(asistencia)
    return asistencia


def get_historial_asistencia_miembro(
    db: Session,
    miembro_id: uuid.UUID,
    grupo_id: uuid.UUID | None = None,
    desde: date | None = None,
    hasta: date | None = None,
) -> list[AsistenciaEncuentro]:
    stmt = (
        select(AsistenciaEncuentro)
        .join(Encuentro, AsistenciaEncuentro.encuentro_id == Encuentro.id)
        .where(AsistenciaEncuentro.miembro_id == miembro_id)
    )
    if grupo_id is not None:
        stmt = stmt.where(Encuentro.grupo_id == grupo_id)
    if desde is not None:
        stmt = stmt.where(Encuentro.fecha >= desde)
    if hasta is not None:
        stmt = stmt.where(Encuentro.fecha <= hasta)
    stmt = stmt.order_by(Encuentro.fecha.desc())
    return list(db.scalars(stmt).all())


def count_encuentros_grupo(
    db: Session,
    grupo_id: uuid.UUID,
    desde: date | None = None,
    hasta: date | None = None,
) -> int:
    stmt = select(Encuentro).where(Encuentro.grupo_id == grupo_id)
    if desde is not None:
        stmt = stmt.where(Encuentro.fecha >= desde)
    if hasta is not None:
        stmt = stmt.where(Encuentro.fecha <= hasta)
    return len(list(db.scalars(stmt).all()))


def create_log_reapertura(
    db: Session,
    encuentro_id: uuid.UUID,
    reabierto_por: uuid.UUID,
    motivo: str,
) -> LogReaperturaEncuentro:
    log = LogReaperturaEncuentro(
        encuentro_id=encuentro_id,
        reabierto_por=reabierto_por,
        motivo=motivo,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
