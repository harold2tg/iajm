from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.tesoreria import repository
from app.domains.tesoreria.models import ActividadProFondos, Donacion, OtroIngreso, ProductoActividad, TipoDonacionEnum
from app.domains.tesoreria.schemas import (
    ActividadProFondosCreate,
    ActividadProFondosResponse,
    DonacionCreate,
    OtroIngresoCreate,
    ProductoActividadCreate,
)
from app.domains.usuarios.models import RolEnum, Usuario

logger = logging.getLogger(__name__)


def _require_admin_o_tesoreria(actor: Usuario) -> None:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles and RolEnum.asesor_tesoreria not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador o tesoreria",
        )


def crear_actividad_profondos(
    db: Session,
    data: ActividadProFondosCreate,
    actor: Usuario,
) -> ActividadProFondos:
    _require_admin_o_tesoreria(actor)
    return repository.crear_actividad(db, **data.model_dump())


def agregar_producto(
    db: Session,
    actividad_id: uuid.UUID,
    data: ProductoActividadCreate,
    actor: Usuario,
) -> ProductoActividad:
    _require_admin_o_tesoreria(actor)
    actividad = repository.get_actividad(db, actividad_id)
    if actividad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")
    return repository.crear_producto(db, actividad_id=actividad_id, **data.model_dump())


def _calcular_utilidad_actividad(actividad: ActividadProFondos) -> dict:
    """G04 — RN-TES-001: Calcula total_ingresos, total_costos y utilidad en tiempo de consulta."""
    total_ingresos = sum(
        (p.cantidad * float(p.precio_venta))
        for p in actividad.productos
    )
    total_costos = sum(
        (p.cantidad * float(p.costo_unitario))
        for p in actividad.productos
        if not p.es_donado and p.costo_unitario is not None
    )
    return {
        "total_ingresos": total_ingresos,
        "total_costos": total_costos,
        "utilidad": total_ingresos - total_costos,
    }


def get_actividad_con_utilidad(db: Session, actividad_id: uuid.UUID) -> ActividadProFondosResponse:
    """G04: Devuelve una actividad con los campos de utilidad calculados."""
    actividad = repository.get_actividad(db, actividad_id)
    if actividad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

    calc = _calcular_utilidad_actividad(actividad)
    data = ActividadProFondosResponse.model_validate(actividad)
    data.total_ingresos = calc["total_ingresos"]
    data.total_costos = calc["total_costos"]
    data.utilidad = calc["utilidad"]
    return data


def _validar_donacion(data: DonacionCreate) -> None:
    """G02 — RN-TES-002: Valida reglas XOR para donaciones."""
    # Regla 1: efectivo no puede tener campos de especie
    if data.tipo == TipoDonacionEnum.efectivo:
        if data.cantidad_especie is not None or data.valor_estimado is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Una donación en efectivo no puede tener campos de especie "
                    "(cantidad_especie, valor_estimado). Use tipo='especie' para donar artículos."
                ),
            )

    # Regla 2: especie no puede tener valor (campo de efectivo)
    if data.tipo == TipoDonacionEnum.especie:
        if data.valor is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Una donación en especie no puede tener el campo 'valor' (monetario). "
                    "Use 'valor_estimado' para indicar el valor aproximado del artículo."
                ),
            )

    # Regla 3: no puede tener actividad_id Y es_general=True al mismo tiempo
    if data.actividad_id is not None and data.es_general:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Una donación no puede estar asociada a una actividad (actividad_id) "
                "y ser general (es_general=True) al mismo tiempo. Elegí una sola opción."
            ),
        )


def registrar_donacion(
    db: Session,
    data: DonacionCreate,
    actor: Usuario,
) -> Donacion:
    _require_admin_o_tesoreria(actor)

    # G02 — validación XOR efectivo/especie y actividad/general
    _validar_donacion(data)

    # es_general es campo virtual del schema, no va a la DB
    datos_db = data.model_dump(exclude={"es_general"})

    # G03 — donación en especie: crear item en inventario automáticamente
    if data.tipo == TipoDonacionEnum.especie:
        from app.domains.inventario import repository as inv_repo
        from app.domains.inventario.models import EstadoItemEnum, OrigenItemEnum

        nombre_item = data.descripcion or "Item donado (sin descripción)"
        cantidad_item = data.cantidad_especie or 1

        item = inv_repo.crear_item(
            db,
            nombre=nombre_item,
            cantidad=cantidad_item,
            origen=OrigenItemEnum.donacion,
            estado=EstadoItemEnum.bueno,
        )
        datos_db["item_inventario_id"] = item.id
        logger.info(
            "G03: Item inventario creado automáticamente por donación en especie. "
            "item_id=%s nombre=%s cantidad=%s",
            item.id,
            nombre_item,
            cantidad_item,
        )

    return repository.registrar_donacion(db, **datos_db)


def registrar_otro_ingreso(
    db: Session,
    data: OtroIngresoCreate,
    actor: Usuario,
) -> OtroIngreso:
    _require_admin_o_tesoreria(actor)
    return repository.registrar_otro_ingreso(db, **data.model_dump())


def get_resumen(db: Session, mes: int, anio: int, actor: Usuario) -> dict:
    total_ingresos = repository.sum_ingresos_mes(db, mes, anio)

    # G05 — sumar ventas de tienda misionera al total de ingresos
    total_tienda = repository.sum_ventas_tienda_mes(db, mes, anio)
    total_ingresos += total_tienda

    total_gastos = 0.0
    try:
        from app.domains.gastos import service as gastos_service
        total_gastos = gastos_service.sum_gastos_mes(db, mes, anio)
    except (ImportError, AttributeError):
        pass

    return {
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": total_ingresos - total_gastos,
    }
