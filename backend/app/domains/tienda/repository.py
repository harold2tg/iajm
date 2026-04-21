from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.tienda.models import DetalleVentaDia, EstadoVentaEnum, VentaDia


def crear_venta(db: Session, **kwargs) -> VentaDia:
    venta = VentaDia(**kwargs)
    db.add(venta)
    db.commit()
    db.refresh(venta)
    return venta


def crear_detalle(db: Session, **kwargs) -> DetalleVentaDia:
    detalle = DetalleVentaDia(**kwargs)
    db.add(detalle)
    db.commit()
    db.refresh(detalle)
    return detalle


def get_venta(db: Session, id: uuid.UUID) -> Optional[VentaDia]:
    return db.get(VentaDia, id)


def listar_ventas(db: Session, skip: int = 0, limit: int = 100) -> list[VentaDia]:
    stmt = select(VentaDia).order_by(VentaDia.fecha.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def sum_ventas_mes(db: Session, mes: int, anio: int) -> float:
    stmt = (
        select(func.sum(VentaDia.total_calculado))
        .where(func.extract("month", VentaDia.fecha) == mes)
        .where(func.extract("year", VentaDia.fecha) == anio)
    )
    result = db.scalar(stmt)
    return float(result) if result is not None else 0.0


def cerrar_venta(db: Session, venta: VentaDia) -> VentaDia:
    """Marca la venta como cerrada y persiste los cambios."""
    venta.estado = EstadoVentaEnum.cerrado
    db.add(venta)
    db.commit()
    db.refresh(venta)
    return venta
