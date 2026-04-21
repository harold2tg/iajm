from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, model_validator

from app.domains.grupos.models import TipoGrupoEnum


class GrupoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    tipo: TipoGrupoEnum
    edad_minima: int
    edad_maxima: int


class GrupoUpdate(BaseModel):
    nombre: str | None = None
    tipo: TipoGrupoEnum | None = None
    edad_minima: int | None = None
    edad_maxima: int | None = None

    @model_validator(mode="after")
    def validar_rango_si_ambos_presentes(self) -> "GrupoUpdate":
        if self.edad_minima is not None and self.edad_maxima is not None:
            if self.edad_minima >= self.edad_maxima:
                raise ValueError("edad_minima debe ser menor que edad_maxima")
        return self
