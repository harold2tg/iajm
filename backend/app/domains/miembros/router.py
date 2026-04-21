from __future__ import annotations

import uuid

from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_user_grupos
from app.domains.usuarios.models import Usuario
from app.domains.miembros.schemas import (
    MiembroCreate,
    MiembroUpdate,
    MiembroResponse,
    HistorialGrupoResponse,
)
from app.domains.miembros import service

router = APIRouter(tags=["miembros"])


@router.get("/", response_model=list[MiembroResponse])
def listar(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
    grupo_id: Optional[uuid.UUID] = None,
) -> list[MiembroResponse]:
    return service.listar_miembros(db, current_user, grupos_actor, grupo_id=grupo_id)


@router.post("/", response_model=MiembroResponse, status_code=status.HTTP_201_CREATED)
def crear(
    data: MiembroCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> MiembroResponse:
    return service.crear_miembro(db, data, current_user)


@router.get("/{miembro_id}", response_model=MiembroResponse)
def obtener(
    miembro_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
) -> MiembroResponse:
    return service.obtener_miembro(db, miembro_id, current_user, grupos_actor)


@router.patch("/{miembro_id}", response_model=MiembroResponse)
def actualizar(
    miembro_id: uuid.UUID,
    data: MiembroUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
) -> MiembroResponse:
    return service.actualizar_miembro(db, miembro_id, data, current_user)


@router.delete("/{miembro_id}", response_model=MiembroResponse)
def desactivar(
    miembro_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> MiembroResponse:
    return service.desactivar_miembro(db, miembro_id, current_user)


@router.get("/{miembro_id}/historial-grupo", response_model=list[HistorialGrupoResponse])
def historial_grupo(
    miembro_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
) -> list[HistorialGrupoResponse]:
    return service.listar_historial_grupo(db, miembro_id, current_user, grupos_actor)
