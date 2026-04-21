from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.domains.miembros.models import TipoMiembroEnum


class MiembroCreate(BaseModel):
    nombre_completo: str
    fecha_nacimiento: date
    fecha_ingreso: date
    telefono_personal: str | None = None
    nombre_acudiente: str | None = None
    telefono_acudiente: str | None = None
    encuentro_id: uuid.UUID | None = None


class MiembroUpdate(BaseModel):
    nombre_completo: str | None = None
    telefono_personal: str | None = None
    nombre_acudiente: str | None = None
    telefono_acudiente: str | None = None
    activo: bool | None = None


class MiembroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre_completo: str
    fecha_nacimiento: date
    edad: int
    tipo: TipoMiembroEnum
    grupo_id: uuid.UUID
    fecha_ingreso: date
    telefono_personal: str | None
    nombre_acudiente: str | None
    telefono_acudiente: str | None
    activo: bool
    ingresado_en_encuentro_id: uuid.UUID | None
    creado_en: datetime
    nombre_grupo: str | None = None


class HistorialGrupoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    miembro_id: uuid.UUID
    grupo_id: uuid.UUID
    cambiado_en: datetime
