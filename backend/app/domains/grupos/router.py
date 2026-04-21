from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_user_grupos, require_admin
from app.domains.grupos import service
from app.domains.grupos.models import Grupo
from app.domains.grupos.schemas import GrupoResponse, GrupoUpdate
from app.domains.usuarios.models import Usuario

router = APIRouter()


@router.get("/", response_model=list[GrupoResponse])
def listar(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> list[Grupo]:
    return service.listar_grupos(db)


# IMPORTANTE: esta ruta estática debe ir ANTES de /{grupo_id}
# para que FastAPI no intente parsear "mis-grupos" como UUID
@router.get("/mis-grupos", response_model=list[GrupoResponse])
def mis_grupos(
    db: Session = Depends(get_db),
    grupos_ids: list[uuid.UUID] = Depends(get_user_grupos),
) -> list[Grupo]:
    return [service.obtener_grupo(db, gid) for gid in grupos_ids]


@router.get("/{grupo_id}", response_model=GrupoResponse)
def obtener(
    grupo_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> Grupo:
    return service.obtener_grupo(db, grupo_id)


@router.patch("/{grupo_id}", response_model=GrupoResponse)
def actualizar(
    grupo_id: uuid.UUID,
    body: GrupoUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> Grupo:
    return service.actualizar_grupo(db, grupo_id, body, actor=admin)
