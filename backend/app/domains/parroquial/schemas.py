from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ActividadParroquialCreate(BaseModel):
    nombre: str
    fecha: date
    descripcion: str | None = None
    responsable: str | None = None


class ActividadParroquialUpdate(BaseModel):
    nombre: str | None = None
    fecha: date | None = None
    descripcion: str | None = None
    responsable: str | None = None


class ActividadParroquialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    fecha: date
    descripcion: str | None
    responsable: str | None
    dinero_recolectado: float | None
    fecha_entrega: date | None
    entregado: bool
    creado_en: datetime


class MarcarEntregaRequest(BaseModel):
    dinero_recolectado: float
    fecha_entrega: date
