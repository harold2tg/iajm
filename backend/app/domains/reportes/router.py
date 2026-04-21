from __future__ import annotations

import csv
import io
import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, get_user_grupos
from app.domains.reportes import service
from app.domains.reportes.schemas import (
    ActividadReporteResponse,
    AsistenciaResponse,
    BalanceResponse,
    CuotasResponse,
    DonacionesResponse,
    EncuentrosResponse,
    InventarioResponse,
    TiendaResponse,
    UsuariosResponse,
)
from app.domains.usuarios.models import RolEnum, Usuario

router = APIRouter()

ROLES_TESORERIA = {RolEnum.administrador, RolEnum.asesor_tesoreria, RolEnum.observador}
ROLES_GRUPO = {RolEnum.administrador, RolEnum.asesor_grupo, RolEnum.observador}
ROLES_TIENDA = {RolEnum.administrador, RolEnum.asesor_tienda, RolEnum.asesor_tesoreria, RolEnum.observador}


def _check_roles(actor: Usuario, allowed: set[RolEnum]) -> None:
    from fastapi import HTTPException, status
    roles = {r.rol for r in actor.roles}
    if not roles.intersection(allowed):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para acceder a este reporte",
        )


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ── R01 Balance ──────────────────────────────────────────────────────────────

@router.get("/balance", response_model=BalanceResponse)
def reporte_balance(
    mes: int,
    anio: int,
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_TESORERIA)
    resultado = service.get_balance(db, mes, anio)

    if formato == "csv":
        rows = [
            {"tipo": "ingreso", "descripcion": i.descripcion, "valor": i.valor, "fecha": str(i.fecha), "categoria": i.tipo}
            for i in resultado.detalle_ingresos
        ] + [
            {"tipo": "gasto", "descripcion": g.descripcion, "valor": g.valor_total, "fecha": str(g.fecha), "categoria": g.categoria}
            for g in resultado.detalle_gastos
        ]
        return _csv_response(rows, "reporte_balance.csv")

    return resultado


# ── R02 Actividad Pro-Fondos ──────────────────────────────────────────────────

@router.get("/actividades/{actividad_id}", response_model=ActividadReporteResponse)
def reporte_actividad(
    actividad_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_TESORERIA)
    return service.get_reporte_actividad(db, actividad_id)


# ── R03 Donaciones ────────────────────────────────────────────────────────────

@router.get("/donaciones", response_model=DonacionesResponse)
def reporte_donaciones(
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    tipo: Optional[str] = None,
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_TESORERIA)
    resultado = service.get_donaciones(db, mes, anio, tipo)

    if formato == "csv":
        rows = [
            {
                "id": str(d.id), "tipo": d.tipo, "donante": d.donante or "",
                "fecha": str(d.fecha), "valor": d.valor or "",
                "descripcion": d.descripcion or "", "cantidad_especie": d.cantidad_especie or "",
                "valor_estimado": d.valor_estimado or "",
            }
            for d in resultado.donaciones
        ]
        return _csv_response(rows, "reporte_donaciones.csv")

    return resultado


# ── R04 Inventario ────────────────────────────────────────────────────────────

@router.get("/inventario", response_model=InventarioResponse)
def reporte_inventario(
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_TIENDA)
    resultado = service.get_inventario(db)

    if formato == "csv":
        rows = [
            {
                "id": str(i.id), "nombre": i.nombre, "cantidad": i.cantidad,
                "tipo": i.tipo or "", "origen": i.origen or "",
                "estado": i.estado or "", "ubicacion": i.ubicacion or "",
            }
            for i in resultado.items
        ]
        return _csv_response(rows, "reporte_inventario.csv")

    return resultado


# ── R05 Asistencia ────────────────────────────────────────────────────────────

@router.get("/asistencia", response_model=AsistenciaResponse)
def reporte_asistencia(
    grupo_id: Optional[uuid.UUID] = None,
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_GRUPO)
    actor_roles = [r.rol.value for r in actor.roles]
    actor_grupos = [r.grupo_id for r in actor.roles if r.grupo_id is not None]
    resultado = service.get_asistencia(db, grupo_id, mes, anio, actor_grupos, actor_roles)

    if formato == "csv":
        rows = [
            {
                "miembro_id": str(m.miembro_id), "nombre": m.nombre,
                "total_encuentros": m.total_encuentros, "total_asistencias": m.total_asistencias,
                "porcentaje": m.porcentaje, "apto_consagracion": m.apto_consagracion,
            }
            for m in resultado.miembros
        ]
        return _csv_response(rows, "reporte_asistencia.csv")

    return resultado


# ── R06 Encuentros ────────────────────────────────────────────────────────────

@router.get("/encuentros", response_model=EncuentrosResponse)
def reporte_encuentros(
    grupo_id: Optional[uuid.UUID] = None,
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_GRUPO)
    actor_roles = [r.rol.value for r in actor.roles]
    actor_grupos = [r.grupo_id for r in actor.roles if r.grupo_id is not None]
    resultado = service.get_encuentros(db, grupo_id, mes, anio, actor_grupos, actor_roles)

    if formato == "csv":
        rows = [
            {
                "encuentro_id": str(e.encuentro_id), "fecha": str(e.fecha),
                "grupo": e.grupo, "tema": e.tema or "",
                "total_miembros": e.total_miembros, "total_asistieron": e.total_asistieron,
                "porcentaje_cobertura": e.porcentaje_cobertura,
            }
            for e in resultado.encuentros
        ]
        return _csv_response(rows, "reporte_encuentros.csv")

    return resultado


# ── R07 Tienda ────────────────────────────────────────────────────────────────

@router.get("/tienda", response_model=TiendaResponse)
def reporte_tienda(
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_TIENDA)
    resultado = service.get_tienda(db, mes, anio)

    if formato == "csv":
        rows = [{"fecha": str(v.fecha), "total": v.total} for v in resultado.ventas_por_dia]
        return _csv_response(rows, "reporte_tienda.csv")

    return resultado


# ── R08 Cuotas ────────────────────────────────────────────────────────────────

@router.get("/cuotas", response_model=CuotasResponse)
def reporte_cuotas(
    mes: int,
    anio: int,
    formato: Optional[str] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    _check_roles(actor, ROLES_TESORERIA)
    resultado = service.get_cuotas(db, mes, anio)

    if formato == "csv":
        rows = [
            {
                "asesor_id": str(c.asesor_id), "nombre": c.nombre,
                "estado": c.estado, "monto": c.monto,
                "fecha_pago": str(c.fecha_pago) if c.fecha_pago else "",
            }
            for c in resultado.cuotas
        ]
        return _csv_response(rows, "reporte_cuotas.csv")

    return resultado


# ── R09 Usuarios ─────────────────────────────────────────────────────────────

@router.get("/usuarios", response_model=UsuariosResponse)
def reporte_usuarios(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_admin),
):
    return service.get_usuarios(db)
