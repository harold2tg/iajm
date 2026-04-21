from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.tienda import repository, service
from app.domains.tienda.schemas import VentaDiaCreate, VentaDiaCerrarResponse, VentaDiaResponse
from app.domains.usuarios.models import Usuario

router = APIRouter()


@router.get("/ventas", response_model=list[VentaDiaResponse])
def listar_ventas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return repository.listar_ventas(db, skip=skip, limit=limit)


@router.post("/ventas", response_model=VentaDiaResponse, status_code=status.HTTP_201_CREATED)
def registrar_venta(
    data: VentaDiaCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.registrar_venta(db, data, actor)


@router.get("/ventas/{venta_id}", response_model=VentaDiaResponse)
def get_venta(
    venta_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    from fastapi import HTTPException
    venta = repository.get_venta(db, venta_id)
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post("/ventas/{venta_id}/cerrar", response_model=VentaDiaCerrarResponse)
def cerrar_venta(
    venta_id: uuid.UUID,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.cerrar_venta(db, venta_id, actor)
