from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.tienda import repository
from app.domains.tienda.models import EstadoVentaEnum, VentaDia
from app.domains.tienda.schemas import VentaDiaCreate, VentaDiaCerrarResponse
from app.domains.usuarios.models import RolEnum, Usuario


def _puede_registrar(actor: Usuario) -> bool:
    roles = [r.rol for r in actor.roles]
    return RolEnum.administrador in roles or RolEnum.asesor_tienda in roles


def registrar_venta(db: Session, data: VentaDiaCreate, actor: Usuario) -> VentaDia:
    if not _puede_registrar(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador o asesor_tienda",
        )

    detalles_data = []
    total = 0.0
    for d in data.detalles:
        subtotal = d.cantidad * d.precio_unitario
        total += subtotal
        detalles_data.append({
            "producto": d.producto,
            "cantidad": d.cantidad,
            "precio_unitario": d.precio_unitario,
            "subtotal": subtotal,
        })

    venta = repository.crear_venta(
        db,
        fecha=data.fecha,
        observaciones=data.observaciones,
        registrado_por=actor.id,
        total_calculado=total,
    )

    for d in detalles_data:
        repository.crear_detalle(db, venta_dia_id=venta.id, **d)

    db.refresh(venta)
    return venta


def cerrar_venta(db: Session, venta_id: uuid.UUID, actor: Usuario) -> VentaDiaCerrarResponse:
    """RN-TIE-003: Cierra una VentaDia y crea automáticamente un ingreso en tesorería."""
    if not _puede_registrar(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador o asesor_tienda",
        )

    venta = repository.get_venta(db, venta_id)
    if venta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

    if venta.estado == EstadoVentaEnum.cerrado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La venta del {venta.fecha} ya está cerrada y no puede cerrarse nuevamente",
        )

    # Calcular total desde los detalles (fuente de verdad)
    total_calculado = sum(
        float(d.cantidad) * float(d.precio_unitario) for d in venta.detalles
    )
    venta.total_calculado = total_calculado

    # Crear ingreso en tesorería — import local para evitar ciclo circular
    from app.domains.tesoreria import repository as tes_repo
    from app.domains.tesoreria.models import TipoIngresoEnum

    ingreso = tes_repo.registrar_otro_ingreso(
        db,
        descripcion=f"Venta tienda misionera - {venta.fecha}",
        valor=total_calculado,
        fecha=venta.fecha,
    )

    # Cerrar la venta en DB
    venta = repository.cerrar_venta(db, venta)

    # Construir response con ingreso_id — model_validate desde dict para incluir ingreso_id
    venta_dict = {
        "id": venta.id,
        "fecha": venta.fecha,
        "registrado_por": venta.registrado_por,
        "observaciones": venta.observaciones,
        "total_calculado": venta.total_calculado,
        "estado": venta.estado,
        "creado_en": venta.creado_en,
        "detalles": venta.detalles,
        "ingreso_id": ingreso.id,
    }
    return VentaDiaCerrarResponse.model_validate(venta_dict)
