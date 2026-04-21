from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel


# ── R01 Balance ──────────────────────────────────────────────────────────────

class DetalleIngresoItem(BaseModel):
    descripcion: str
    valor: float
    fecha: date
    tipo: str  # "otro_ingreso" | "cuota_asesor" | "venta_tienda"


class DetalleGastoItem(BaseModel):
    descripcion: str
    valor_total: float
    fecha: date
    categoria: str


class BalanceResponse(BaseModel):
    mes: int
    anio: int
    total_ingresos: float
    total_gastos: float
    saldo: float
    detalle_ingresos: list[DetalleIngresoItem]
    detalle_gastos: list[DetalleGastoItem]


# ── R02 Actividad Pro-Fondos ──────────────────────────────────────────────────

class ProductoActividadItem(BaseModel):
    id: uuid.UUID
    nombre: str
    cantidad: int
    costo_unitario: Optional[float]
    precio_venta: float
    es_donado: bool

    model_config = {"from_attributes": True}


class ActividadReporteResponse(BaseModel):
    actividad_id: uuid.UUID
    nombre: str
    tipo: str
    fecha: date
    responsable: str
    productos: list[ProductoActividadItem]
    total_ingresos: float
    total_costos: float
    utilidad: float


# ── R03 Donaciones ────────────────────────────────────────────────────────────

class DonacionItem(BaseModel):
    id: uuid.UUID
    tipo: str
    donante: Optional[str]
    fecha: date
    valor: Optional[float]
    descripcion: Optional[str]
    cantidad_especie: Optional[int]
    valor_estimado: Optional[float]

    model_config = {"from_attributes": True}


class DonacionesResponse(BaseModel):
    total_efectivo: float
    total_especie: float
    donaciones: list[DonacionItem]


# ── R04 Inventario ────────────────────────────────────────────────────────────

class GrupoConteo(BaseModel):
    clave: str
    cantidad: int


class ItemInventarioItem(BaseModel):
    id: uuid.UUID
    nombre: str
    cantidad: int
    tipo: Optional[str]
    origen: Optional[str]
    estado: Optional[str]
    ubicacion: Optional[str]

    model_config = {"from_attributes": True}


class InventarioResponse(BaseModel):
    total_items: int
    por_tipo: list[GrupoConteo]
    por_origen: list[GrupoConteo]
    items: list[ItemInventarioItem]


# ── R05 Asistencia ────────────────────────────────────────────────────────────

class AsistenciaMiembroItem(BaseModel):
    miembro_id: uuid.UUID
    nombre: str
    fecha_ingreso: date
    total_encuentros: int
    total_asistencias: int
    porcentaje: float
    apto_consagracion: bool


class AsistenciaResponse(BaseModel):
    miembros: list[AsistenciaMiembroItem]


# ── R06 Encuentros ────────────────────────────────────────────────────────────

class EncuentroReporteItem(BaseModel):
    encuentro_id: uuid.UUID
    fecha: date
    grupo: str
    tema: Optional[str]
    total_miembros: int
    total_asistieron: int
    porcentaje_cobertura: float


class EncuentrosResponse(BaseModel):
    encuentros: list[EncuentroReporteItem]


# ── R07 Tienda ────────────────────────────────────────────────────────────────

class VentaDiaItem(BaseModel):
    fecha: date
    total: float


class TiendaResponse(BaseModel):
    total_mes: float
    ventas_por_dia: list[VentaDiaItem]
    acumulado_historico: float


# ── R08 Cuotas ────────────────────────────────────────────────────────────────

class CuotaAsesorItem(BaseModel):
    asesor_id: uuid.UUID
    nombre: str
    estado: str
    monto: float
    fecha_pago: Optional[date]


class CuotasResponse(BaseModel):
    mes: int
    anio: int
    cuotas: list[CuotaAsesorItem]


# ── R09 Usuarios ─────────────────────────────────────────────────────────────

class UsuarioReporteItem(BaseModel):
    id: uuid.UUID
    nombre: str
    email: str
    roles: list[str]
    ultimo_acceso: Optional[str]


class UsuariosResponse(BaseModel):
    total_activos: int
    usuarios: list[UsuarioReporteItem]
