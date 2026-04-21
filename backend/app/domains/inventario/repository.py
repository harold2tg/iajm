from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.inventario.models import ItemInventario, TipoItemEnum


def crear_item(db: Session, **kwargs) -> ItemInventario:
    item = ItemInventario(**kwargs)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, id: uuid.UUID) -> Optional[ItemInventario]:
    return db.get(ItemInventario, id)


def listar_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoItemEnum] = None,
) -> list[ItemInventario]:
    stmt = select(ItemInventario)
    if tipo is not None:
        stmt = stmt.where(ItemInventario.tipo == tipo)
    stmt = stmt.order_by(ItemInventario.nombre).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def actualizar_item(db: Session, item: ItemInventario, data: dict) -> ItemInventario:
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
