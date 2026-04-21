from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.inventario import repository
from app.domains.inventario.models import ItemInventario, TipoItemEnum
from app.domains.inventario.schemas import ItemInventarioCreate, ItemInventarioUpdate
from app.domains.usuarios.models import RolEnum, Usuario


def _es_admin(actor: Usuario) -> bool:
    return any(r.rol == RolEnum.administrador for r in actor.roles)


def crear_item(db: Session, data: ItemInventarioCreate, actor: Usuario) -> ItemInventario:
    if not _es_admin(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador",
        )
    return repository.crear_item(db, **data.model_dump())


def actualizar_item(
    db: Session,
    item_id,
    data: ItemInventarioUpdate,
    actor: Usuario,
) -> ItemInventario:
    if not _es_admin(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador",
        )
    item = repository.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado")
    return repository.actualizar_item(db, item, data.model_dump(exclude_none=True))


def listar_items(
    db: Session,
    skip: int,
    limit: int,
    tipo: Optional[TipoItemEnum],
    actor: Usuario,
) -> list[ItemInventario]:
    return repository.listar_items(db, skip=skip, limit=limit, tipo=tipo)
