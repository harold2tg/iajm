from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.domains.encuentros.models import EstadoAsistenciaEnum, EstadoEncuentroEnum


class EncuentroCreate(BaseModel):
    grupo_id: uuid.UUID
    fecha: date
    tema: Optional[str] = None
    observaciones: Optional[str] = None


class EncuentroUpdate(BaseModel):
    tema: Optional[str] = None
    observaciones: Optional[str] = None


class EncuentroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    grupo_id: uuid.UUID
    fecha: date
    creado_por: Optional[uuid.UUID]
    tema: Optional[str]
    observaciones: Optional[str]
    estado: EstadoEncuentroEnum
    creado_en: datetime
    cerrado_en: Optional[datetime]
    total_asistentes: int = 0
    porcentaje_asistencia: float = 0.0


class CerrarEncuentroResponse(BaseModel):
    encuentro: EncuentroResponse
    advertencia: Optional[str] = None


class AsistenciaCreate(BaseModel):
    miembro_id: uuid.UUID
    estado: EstadoAsistenciaEnum


class AsistenciaBulkUpdate(BaseModel):
    asistencias: list[AsistenciaCreate]


class AsistenciaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    encuentro_id: uuid.UUID
    miembro_id: uuid.UUID
    estado: EstadoAsistenciaEnum
    registrado_por: Optional[uuid.UUID]
    registrado_en: datetime


class MetricasMiembro(BaseModel):
    miembro_id: uuid.UUID
    nombre: str
    total_encuentros: int
    total_asistio: int
    porcentaje: float
    racha_actual: int
    apto_consagracion: bool


class ReaperturaRequest(BaseModel):
    motivo: str
