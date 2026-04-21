from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.parroquial import service
from app.domains.parroquial.schemas import (
    ActividadParroquialCreate,
    ActividadParroquialResponse,
    MarcarEntregaRequest,
)
from app.domains.usuarios.models import Usuario

router = APIRouter()


@router.get("/actividades", response_model=list[ActividadParroquialResponse])
def listar_actividades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.listar_actividades(db, skip=skip, limit=limit, actor=actor)


@router.post("/actividades", response_model=ActividadParroquialResponse, status_code=status.HTTP_201_CREATED)
def crear_actividad(
    data: ActividadParroquialCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.crear_actividad(db, data, actor)


@router.post("/actividades/{actividad_id}/entregar", response_model=ActividadParroquialResponse)
def marcar_entrega(
    actividad_id: uuid.UUID,
    data: MarcarEntregaRequest,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.marcar_entrega(db, actividad_id, data, actor)
