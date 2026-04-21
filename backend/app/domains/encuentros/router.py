from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_user_grupos, require_admin
from app.domains.encuentros import service
from app.domains.encuentros.schemas import (
    AsistenciaBulkUpdate,
    AsistenciaCreate,
    AsistenciaResponse,
    CerrarEncuentroResponse,
    EncuentroCreate,
    EncuentroResponse,
    EncuentroUpdate,
    MetricasMiembro,
    ReaperturaRequest,
)
from app.domains.usuarios.models import Usuario

# Router principal para /api/v1/encuentros
router = APIRouter()

# Router secundario para /api/v1/miembros (métricas de asistencia de un miembro)
miembros_router = APIRouter()


# ── Encuentros ────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[EncuentroResponse])
def listar_encuentros(
    grupo_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    encuentros = service.listar_encuentros(db, grupo_id, actor, grupos_actor, skip, limit)
    return [service._build_encuentro_response(db, e) for e in encuentros]


@router.post("/", response_model=EncuentroResponse, status_code=status.HTTP_201_CREATED)
def crear_encuentro(
    data: EncuentroCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    enc = service.crear_encuentro(db, data, actor, grupos_actor)
    return service._build_encuentro_response(db, enc)


@router.get("/{encuentro_id}", response_model=EncuentroResponse)
def obtener_encuentro(
    encuentro_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    enc = service.obtener_encuentro(db, encuentro_id, actor, grupos_actor)
    return service._build_encuentro_response(db, enc)


@router.patch("/{encuentro_id}", response_model=EncuentroResponse)
def actualizar_encuentro(
    encuentro_id: uuid.UUID,
    data: EncuentroUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    enc = service.actualizar_encuentro(db, encuentro_id, data, actor, grupos_actor)
    return service._build_encuentro_response(db, enc)


@router.post("/{encuentro_id}/cerrar", response_model=CerrarEncuentroResponse)
def cerrar_encuentro(
    encuentro_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    result = service.cerrar_encuentro(db, encuentro_id, actor, grupos_actor)
    return CerrarEncuentroResponse(encuentro=result.encuentro, advertencia=result.advertencia)


@router.post("/{encuentro_id}/reabrir", response_model=EncuentroResponse)
def reabrir_encuentro(
    encuentro_id: uuid.UUID,
    body: ReaperturaRequest,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_admin),
):
    enc = service.reabrir_encuentro(db, encuentro_id, body.motivo, actor)
    return service._build_encuentro_response(db, enc)


# ── Asistencia ────────────────────────────────────────────────────────────────


@router.get("/{encuentro_id}/asistencia", response_model=list[AsistenciaResponse])
def listar_asistencia(
    encuentro_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    enc = service.obtener_encuentro(db, encuentro_id, actor, grupos_actor)
    from app.domains.encuentros import repository
    return repository.get_asistencias_encuentro(db, encuentro_id)


# IMPORTANTE: ruta literal /bulk ANTES que /{miembro_id}
@router.post("/{encuentro_id}/asistencia/bulk", response_model=list[AsistenciaResponse])
def registrar_asistencia_bulk(
    encuentro_id: uuid.UUID,
    body: AsistenciaBulkUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    return service.registrar_asistencia_bulk(
        db, encuentro_id, body.asistencias, actor, grupos_actor
    )


@router.put(
    "/{encuentro_id}/asistencia/{miembro_id}", response_model=AsistenciaResponse
)
def registrar_asistencia(
    encuentro_id: uuid.UUID,
    miembro_id: uuid.UUID,
    body: AsistenciaCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    return service.registrar_asistencia(
        db, encuentro_id, miembro_id, body.estado, actor, grupos_actor
    )


# ── Métricas ──────────────────────────────────────────────────────────────────


@router.get("/{encuentro_id}/metricas")
def metricas_encuentro(
    encuentro_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    service.obtener_encuentro(db, encuentro_id, actor, grupos_actor)
    return service.calcular_metricas_encuentro(db, encuentro_id)


# ── Métricas de miembro (en router secundario /api/v1/miembros) ───────────────


@miembros_router.get("/{miembro_id}/metricas-asistencia", response_model=MetricasMiembro)
def metricas_asistencia_miembro(
    miembro_id: uuid.UUID,
    grupo_id: uuid.UUID,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
    grupos_actor: list[uuid.UUID] = Depends(get_user_grupos),
):
    return service.calcular_metricas_miembro(db, miembro_id, grupo_id, desde, hasta)
