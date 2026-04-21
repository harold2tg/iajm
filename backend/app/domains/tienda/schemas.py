from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domains.tienda.models import EstadoVentaEnum


class DetalleVentaDiaCreate(BaseModel):
    producto: str
    cantidad: int
    precio_unitario: float


class DetalleVentaDiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    venta_dia_id: uuid.UUID
    producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class VentaDiaCreate(BaseModel):
    fecha: date
    observaciones: str | None = None
    detalles: list[DetalleVentaDiaCreate]


class VentaDiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fecha: date
    registrado_por: uuid.UUID | None
    observaciones: str | None
    total_calculado: float
    estado: EstadoVentaEnum
    creado_en: datetime
    detalles: list[DetalleVentaDiaResponse]


class VentaDiaCerrarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fecha: date
    registrado_por: uuid.UUID | None
    observaciones: str | None
    total_calculado: float
    estado: EstadoVentaEnum
    creado_en: datetime
    detalles: list[DetalleVentaDiaResponse]
    ingreso_id: uuid.UUID
