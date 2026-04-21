from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.tesoreria import service
from app.domains.tesoreria.schemas import (
    ActividadProFondosCreate,
    ActividadProFondosResponse,
    DonacionCreate,
    DonacionResponse,
    OtroIngresoCreate,
    OtroIngresoResponse,
    ProductoActividadCreate,
    ProductoActividadResponse,
    ResumenTesoreriaResponse,
)
from app.domains.usuarios.models import Usuario

router = APIRouter()


@router.post("/actividades", response_model=ActividadProFondosResponse, status_code=status.HTTP_201_CREATED)
def crear_actividad(
    data: ActividadProFondosCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> ActividadProFondosResponse:
    return service.crear_actividad_profondos(db, data, current_user)


@router.get("/actividades", response_model=list[ActividadProFondosResponse])
def listar_actividades(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[ActividadProFondosResponse]:
    from app.domains.tesoreria import repository
    return repository.listar_actividades(db, skip=skip, limit=limit)


@router.get("/actividades/{actividad_id}", response_model=ActividadProFondosResponse)
def get_actividad(
    actividad_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> ActividadProFondosResponse:
    """G04: Devuelve actividad con total_ingresos, total_costos y utilidad calculados."""
    return service.get_actividad_con_utilidad(db, actividad_id)


# LITERAL antes que /{actividad_id}
@router.get("/resumen", response_model=ResumenTesoreriaResponse)
def get_resumen(
    mes: int = Query(..., ge=1, le=12),
    anio: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> ResumenTesoreriaResponse:
    result = service.get_resumen(db, mes, anio, current_user)
    return ResumenTesoreriaResponse(**result)


@router.post(
    "/actividades/{actividad_id}/productos",
    response_model=ProductoActividadResponse,
    status_code=status.HTTP_201_CREATED,
)
def agregar_producto(
    actividad_id: uuid.UUID,
    data: ProductoActividadCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> ProductoActividadResponse:
    return service.agregar_producto(db, actividad_id, data, current_user)


@router.post("/donaciones", response_model=DonacionResponse, status_code=status.HTTP_201_CREATED)
def registrar_donacion(
    data: DonacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> DonacionResponse:
    return service.registrar_donacion(db, data, current_user)


@router.get("/donaciones", response_model=list[DonacionResponse])
def listar_donaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> list[DonacionResponse]:
    from app.domains.tesoreria import repository
    return repository.listar_donaciones(db, skip=skip, limit=limit)


@router.post("/otros-ingresos", response_model=OtroIngresoResponse, status_code=status.HTTP_201_CREATED)
def registrar_otro_ingreso(
    data: OtroIngresoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> OtroIngresoResponse:
    return service.registrar_otro_ingreso(db, data, current_user)
