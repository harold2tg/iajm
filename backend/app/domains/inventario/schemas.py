from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domains.inventario.models import EstadoItemEnum, OrigenItemEnum, TipoItemEnum


class ItemInventarioCreate(BaseModel):
    nombre: str
    cantidad: int
    estado: EstadoItemEnum | None = None
    ubicacion: str | None = None
    responsable: str | None = None
    tipo: TipoItemEnum | None = None
    origen: OrigenItemEnum | None = None


class ItemInventarioUpdate(BaseModel):
    nombre: str | None = None
    cantidad: int | None = None
    estado: EstadoItemEnum | None = None
    ubicacion: str | None = None
    responsable: str | None = None
    tipo: TipoItemEnum | None = None
    origen: OrigenItemEnum | None = None


class ItemInventarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    cantidad: int
    estado: EstadoItemEnum | None
    ubicacion: str | None
    responsable: str | None
    tipo: TipoItemEnum | None
    origen: OrigenItemEnum | None
    creado_en: datetime
