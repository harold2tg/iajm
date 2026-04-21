import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class CategoriaGastoCreate(BaseModel):
    nombre: str


class CategoriaGastoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str


class GastoCreate(BaseModel):
    fecha: date
    descripcion: str
    cantidad: int
    valor_unitario: float
    categoria_id: uuid.UUID


class GastoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fecha: date
    mes: int
    descripcion: str
    cantidad: int
    valor_unitario: float
    valor_total: float
    categoria_id: uuid.UUID
    categoria: CategoriaGastoResponse
