from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domains.tesoreria.models import TipoDonacionEnum


# ── ProductoActividad ─────────────────────────────────────────────────────────

class ProductoActividadCreate(BaseModel):
    nombre: str
    cantidad: int
    costo_unitario: Optional[float] = None
    precio_venta: float
    es_donado: bool = False


class ProductoActividadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actividad_id: uuid.UUID
    nombre: str
    cantidad: int
    costo_unitario: Optional[float] = None
    precio_venta: float
    es_donado: bool


# ── ActividadProFondos ────────────────────────────────────────────────────────

class ActividadProFondosCreate(BaseModel):
    nombre: str
    tipo: str
    fecha: date
    responsable: str


class ActividadProFondosResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    tipo: str
    fecha: date
    responsable: str
    creado_en: datetime
    productos: list[ProductoActividadResponse] = []
    # G04 — RN-TES-001: campos calculados en tiempo de consulta, no en DB
    total_ingresos: float = 0.0
    total_costos: float = 0.0
    utilidad: float = 0.0


# ── Donacion ──────────────────────────────────────────────────────────────────

class DonacionCreate(BaseModel):
    tipo: TipoDonacionEnum
    actividad_id: Optional[uuid.UUID] = None
    es_general: bool = False  # G02: True = donación general (sin actividad asociada)
    donante: Optional[str] = None
    fecha: date
    valor: Optional[float] = None
    descripcion: Optional[str] = None
    cantidad_especie: Optional[int] = None
    valor_estimado: Optional[float] = None
    item_inventario_id: Optional[uuid.UUID] = None


class DonacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: TipoDonacionEnum
    actividad_id: Optional[uuid.UUID] = None
    donante: Optional[str] = None
    fecha: date
    valor: Optional[float] = None
    descripcion: Optional[str] = None
    cantidad_especie: Optional[int] = None
    valor_estimado: Optional[float] = None
    item_inventario_id: Optional[uuid.UUID] = None
    creado_en: datetime


# ── OtroIngreso ───────────────────────────────────────────────────────────────

class OtroIngresoCreate(BaseModel):
    descripcion: str
    valor: float
    fecha: date


class OtroIngresoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    descripcion: str
    valor: float
    fecha: date
    creado_en: datetime


# ── Resumen ───────────────────────────────────────────────────────────────────

class ResumenTesoreriaResponse(BaseModel):
    total_ingresos: float
    total_gastos: float
    balance: float
