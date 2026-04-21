from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.asesores.models import Asesor, AsesorGrupo, CuotaAsesor, TipoAsesorEnum


def get_by_id(db: Session, asesor_id: uuid.UUID) -> Asesor | None:
    return db.execute(select(Asesor).where(Asesor.id == asesor_id)).scalar_one_or_none()


def get_by_usuario_id(db: Session, usuario_id: uuid.UUID) -> Asesor | None:
    return db.execute(select(Asesor).where(Asesor.usuario_id == usuario_id)).scalar_one_or_none()


def get_all(db: Session, solo_activos: bool = False) -> list[Asesor]:
    stmt = select(Asesor)
    if solo_activos:
        stmt = stmt.where(Asesor.activo == True)  # noqa: E712
    return list(db.execute(stmt).scalars().all())


def create(db: Session, **kwargs) -> Asesor:
    asesor = Asesor(**kwargs)
    db.add(asesor)
    db.commit()
    db.refresh(asesor)
    return asesor


def update(db: Session, asesor: Asesor, **kwargs) -> Asesor:
    for key, value in kwargs.items():
        setattr(asesor, key, value)
    db.commit()
    db.refresh(asesor)
    return asesor


def get_grupos_de_asesor(db: Session, asesor_id: uuid.UUID) -> list[AsesorGrupo]:
    stmt = select(AsesorGrupo).where(AsesorGrupo.asesor_id == asesor_id)
    return list(db.execute(stmt).scalars().all())


def add_grupo(db: Session, asesor_id: uuid.UUID, grupo_id: uuid.UUID) -> AsesorGrupo:
    ag = AsesorGrupo(asesor_id=asesor_id, grupo_id=grupo_id)
    db.add(ag)
    db.commit()
    db.refresh(ag)
    return ag


def remove_grupo(db: Session, asesor_id: uuid.UUID, grupo_id: uuid.UUID) -> bool:
    stmt = select(AsesorGrupo).where(
        AsesorGrupo.asesor_id == asesor_id,
        AsesorGrupo.grupo_id == grupo_id,
    )
    ag = db.execute(stmt).scalar_one_or_none()
    if ag is None:
        return False
    db.delete(ag)
    db.commit()
    return True


def count_asesores_base_en_grupo(db: Session, grupo_id: uuid.UUID) -> int:
    stmt = (
        select(func.count(Asesor.id))
        .join(AsesorGrupo, AsesorGrupo.asesor_id == Asesor.id)
        .where(
            AsesorGrupo.grupo_id == grupo_id,
            Asesor.tipo == TipoAsesorEnum.base,
            Asesor.activo == True,  # noqa: E712
        )
    )
    return db.execute(stmt).scalar_one()


def get_cuotas_asesor(
    db: Session,
    asesor_id: uuid.UUID,
    mes: int | None = None,
    anio: int | None = None,
) -> list[CuotaAsesor]:
    stmt = select(CuotaAsesor).where(CuotaAsesor.asesor_id == asesor_id)
    if mes is not None:
        stmt = stmt.where(CuotaAsesor.mes == mes)
    if anio is not None:
        stmt = stmt.where(CuotaAsesor.anio == anio)
    return list(db.execute(stmt).scalars().all())


def get_cuota_by_id(db: Session, cuota_id: uuid.UUID) -> CuotaAsesor | None:
    return db.execute(select(CuotaAsesor).where(CuotaAsesor.id == cuota_id)).scalar_one_or_none()


def create_cuota(db: Session, **kwargs) -> CuotaAsesor:
    cuota = CuotaAsesor(**kwargs)
    db.add(cuota)
    db.commit()
    db.refresh(cuota)
    return cuota


def update_cuota(db: Session, cuota: CuotaAsesor, **kwargs) -> CuotaAsesor:
    for key, value in kwargs.items():
        setattr(cuota, key, value)
    db.commit()
    db.refresh(cuota)
    return cuota


def existe_cuota(db: Session, asesor_id: uuid.UUID, mes: int, anio: int) -> bool:
    stmt = select(CuotaAsesor).where(
        CuotaAsesor.asesor_id == asesor_id,
        CuotaAsesor.mes == mes,
        CuotaAsesor.anio == anio,
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def get_all_cuotas(
    db: Session,
    asesor_id: uuid.UUID | None = None,
    mes: int | None = None,
    anio: int | None = None,
) -> list[CuotaAsesor]:
    stmt = select(CuotaAsesor)
    if asesor_id is not None:
        stmt = stmt.where(CuotaAsesor.asesor_id == asesor_id)
    if mes is not None:
        stmt = stmt.where(CuotaAsesor.mes == mes)
    if anio is not None:
        stmt = stmt.where(CuotaAsesor.anio == anio)
    return list(db.execute(stmt).scalars().all())
