from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.parroquial import repository
from app.domains.parroquial.models import ActividadParroquial
from app.domains.parroquial.schemas import ActividadParroquialCreate, MarcarEntregaRequest
from app.domains.usuarios.models import RolEnum, Usuario


def _es_admin(actor: Usuario) -> bool:
    return any(r.rol == RolEnum.administrador for r in actor.roles)


def crear_actividad(db: Session, data: ActividadParroquialCreate, actor: Usuario) -> ActividadParroquial:
    if not _es_admin(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador",
        )
    return repository.crear_actividad(db, **data.model_dump())


def marcar_entrega(
    db: Session,
    actividad_id,
    data: MarcarEntregaRequest,
    actor: Usuario,
) -> ActividadParroquial:
    actividad = repository.get_actividad(db, actividad_id)
    if actividad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    return repository.marcar_entregado(db, actividad, monto=data.dinero_recolectado, fecha=data.fecha_entrega)


def listar_actividades(
    db: Session,
    skip: int,
    limit: int,
    actor: Usuario,
) -> list[ActividadParroquial]:
    return repository.listar_actividades(db, skip=skip, limit=limit)
