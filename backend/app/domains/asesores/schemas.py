from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domains.asesores.models import EstadoCuotaEnum, TipoAsesorEnum


class GrupoSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str


class AsesorCreate(BaseModel):
    nombre_completo: str
    telefono: str
    tipo: TipoAsesorEnum
    fecha_nacimiento: Optional[date] = None
    usuario_id: Optional[uuid.UUID] = None
    grupo_ids: list[uuid.UUID] = []


class AsesorUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    activo: Optional[bool] = None


class AsesorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre_completo: str
    telefono: str
    tipo: TipoAsesorEnum
    fecha_nacimiento: Optional[date]
    usuario_id: Optional[uuid.UUID]
    activo: bool
    creado_en: datetime
    grupos: list[GrupoSimple] = []


class AsignarGrupoRequest(BaseModel):
    grupo_id: uuid.UUID


class CuotaAsesorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asesor_id: uuid.UUID
    mes: int
    anio: int
    monto: Decimal
    fecha_pago: Optional[date]
    estado: EstadoCuotaEnum


class RegistrarPagoCuotaRequest(BaseModel):
    fecha_pago: date
    monto: Decimal
