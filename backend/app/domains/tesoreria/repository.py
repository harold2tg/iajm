from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.domains.asesores.models import CuotaAsesor, EstadoCuotaEnum
from app.domains.tesoreria.models import (
    ActividadProFondos,
    Donacion,
    OtroIngreso,
    ProductoActividad,
    TipoDonacionEnum,
)


def crear_actividad(db: Session, **kwargs) -> ActividadProFondos:
    actividad = ActividadProFondos(**kwargs)
    db.add(actividad)
    db.commit()
    db.refresh(actividad)
    return actividad


def get_actividad(db: Session, id: uuid.UUID) -> ActividadProFondos | None:
    return db.execute(
        select(ActividadProFondos).where(ActividadProFondos.id == id)
    ).scalar_one_or_none()


def listar_actividades(db: Session, skip: int = 0, limit: int = 50) -> list[ActividadProFondos]:
    return list(
        db.execute(select(ActividadProFondos).offset(skip).limit(limit)).scalars().all()
    )


def crear_producto(db: Session, **kwargs) -> ProductoActividad:
    producto = ProductoActividad(**kwargs)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def registrar_donacion(db: Session, **kwargs) -> Donacion:
    donacion = Donacion(**kwargs)
    db.add(donacion)
    db.commit()
    db.refresh(donacion)
    return donacion


def listar_donaciones(db: Session, skip: int = 0, limit: int = 50) -> list[Donacion]:
    return list(
        db.execute(select(Donacion).offset(skip).limit(limit)).scalars().all()
    )


def registrar_otro_ingreso(db: Session, **kwargs) -> OtroIngreso:
    ingreso = OtroIngreso(**kwargs)
    db.add(ingreso)
    db.commit()
    db.refresh(ingreso)
    return ingreso


def listar_otros_ingresos(db: Session, skip: int = 0, limit: int = 50) -> list[OtroIngreso]:
    return list(
        db.execute(select(OtroIngreso).offset(skip).limit(limit)).scalars().all()
    )


def sum_ingresos_mes(db: Session, mes: int, anio: int) -> float:
    # 1. Cuotas pagadas de asesores
    stmt_cuotas = select(func.coalesce(func.sum(CuotaAsesor.monto), 0)).where(
        CuotaAsesor.mes == mes,
        CuotaAsesor.anio == anio,
        CuotaAsesor.estado == EstadoCuotaEnum.pagado,
    )
    total_cuotas = db.execute(stmt_cuotas).scalar_one() or 0.0

    # 2. Ventas de actividades pro-fondos del mes (precio_venta * cantidad por producto)
    stmt_ventas = (
        select(func.coalesce(func.sum(ProductoActividad.precio_venta * ProductoActividad.cantidad), 0))
        .join(ActividadProFondos, ActividadProFondos.id == ProductoActividad.actividad_id)
        .where(
            extract("month", ActividadProFondos.fecha) == mes,
            extract("year", ActividadProFondos.fecha) == anio,
        )
    )
    total_ventas = db.execute(stmt_ventas).scalar_one() or 0.0

    # 3. Donaciones en efectivo del mes
    stmt_donaciones = select(func.coalesce(func.sum(Donacion.valor), 0)).where(
        Donacion.tipo == TipoDonacionEnum.efectivo,
        extract("month", Donacion.fecha) == mes,
        extract("year", Donacion.fecha) == anio,
    )
    total_donaciones = db.execute(stmt_donaciones).scalar_one() or 0.0

    # 4. Otros ingresos del mes
    stmt_otros = select(func.coalesce(func.sum(OtroIngreso.valor), 0)).where(
        extract("month", OtroIngreso.fecha) == mes,
        extract("year", OtroIngreso.fecha) == anio,
    )
    total_otros = db.execute(stmt_otros).scalar_one() or 0.0

    return float(total_cuotas) + float(total_ventas) + float(total_donaciones) + float(total_otros)


def sum_ventas_tienda_mes(db: Session, mes: int, anio: int) -> float:
    """G05 — RN: Suma ventas de tienda misionera (VentaDia) para el mes/año dado."""
    from app.domains.tienda.models import VentaDia

    stmt = select(func.coalesce(func.sum(VentaDia.total_calculado), 0)).where(
        extract("month", VentaDia.fecha) == mes,
        extract("year", VentaDia.fecha) == anio,
    )
    return float(db.execute(stmt).scalar_one() or 0.0)
