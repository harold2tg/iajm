from __future__ import annotations

import uuid

from sqlalchemy.orm import Session, joinedload

from app.domains.miembros.models import Miembro, HistorialGrupo
from app.domains.encuentros.models import AsistenciaEncuentro, EstadoAsistenciaEnum


def get_by_id(db: Session, miembro_id: uuid.UUID) -> Miembro | None:
    return (
        db.query(Miembro)
        .options(joinedload(Miembro.grupo))
        .filter(Miembro.id == miembro_id)
        .first()
    )


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Miembro]:
    return (
        db.query(Miembro)
        .options(joinedload(Miembro.grupo))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_by_grupo(db: Session, grupo_id: uuid.UUID, solo_activos: bool = True) -> list[Miembro]:
    q = (
        db.query(Miembro)
        .options(joinedload(Miembro.grupo))
        .filter(Miembro.grupo_id == grupo_id)
    )
    if solo_activos:
        q = q.filter(Miembro.activo == True)
    return q.all()


def get_by_grupos(db: Session, grupo_ids: list[uuid.UUID], solo_activos: bool = True) -> list[Miembro]:
    q = (
        db.query(Miembro)
        .options(joinedload(Miembro.grupo))
        .filter(Miembro.grupo_id.in_(grupo_ids))
    )
    if solo_activos:
        q = q.filter(Miembro.activo == True)
    return q.all()


def create(db: Session, miembro: Miembro) -> Miembro:
    db.add(miembro)
    db.flush()
    db.refresh(miembro)
    return miembro


def update(db: Session, miembro: Miembro) -> Miembro:
    db.flush()
    db.refresh(miembro)
    return miembro


def get_activos_todos(db: Session) -> list[Miembro]:
    return db.query(Miembro).filter(Miembro.activo == True).all()


def get_historial_grupo(db: Session, miembro_id: uuid.UUID) -> list[HistorialGrupo]:
    return (
        db.query(HistorialGrupo)
        .filter(HistorialGrupo.miembro_id == miembro_id)
        .order_by(HistorialGrupo.cambiado_en.desc())
        .all()
    )


def crear_asistencia_encuentro(
    db: Session,
    encuentro_id: uuid.UUID,
    miembro_id: uuid.UUID,
    registrado_por_id: uuid.UUID,
) -> None:
    asistencia = AsistenciaEncuentro(
        encuentro_id=encuentro_id,
        miembro_id=miembro_id,
        estado=EstadoAsistenciaEnum.asistio,
        registrado_por=registrado_por_id,
    )
    db.add(asistencia)
    db.flush()
