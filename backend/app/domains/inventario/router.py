from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.inventario import repository, service
from app.domains.inventario.models import TipoItemEnum
from app.domains.inventario.schemas import (
    ItemInventarioCreate,
    ItemInventarioResponse,
    ItemInventarioUpdate,
)
from app.domains.usuarios.models import Usuario

router = APIRouter()


@router.get("/", response_model=list[ItemInventarioResponse])
def listar_items(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoItemEnum] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.listar_items(db, skip=skip, limit=limit, tipo=tipo, actor=actor)


@router.post("/", response_model=ItemInventarioResponse, status_code=status.HTTP_201_CREATED)
def crear_item(
    data: ItemInventarioCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.crear_item(db, data, actor)


@router.get("/{item_id}", response_model=ItemInventarioResponse)
def get_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    from fastapi import HTTPException
    item = repository.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item


@router.patch("/{item_id}", response_model=ItemInventarioResponse)
def actualizar_item(
    item_id: uuid.UUID,
    data: ItemInventarioUpdate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.actualizar_item(db, item_id, data, actor)
