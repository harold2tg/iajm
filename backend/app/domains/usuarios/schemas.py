from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domains.usuarios.models import RolEnum


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Roles ─────────────────────────────────────────────────────────────────────

class UsuarioRolOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rol: RolEnum
    grupo_id: uuid.UUID | None
    asignado_en: datetime


class AsignarRolRequest(BaseModel):
    rol: RolEnum
    grupo_id: uuid.UUID | None = None


# ── Usuario ───────────────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    roles: list[AsignarRolRequest] = []


class UsuarioUpdate(BaseModel):
    nombre_completo: str | None = None
    activo: bool | None = None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre_completo: str
    email: str
    activo: bool
    creado_en: datetime
    ultimo_acceso: datetime | None
    roles: list[UsuarioRolOut]


class UsuarioListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre_completo: str
    email: str
    activo: bool
    creado_en: datetime
