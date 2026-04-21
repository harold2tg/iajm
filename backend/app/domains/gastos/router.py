from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domains.gastos import service
from app.domains.gastos.schemas import (
    CategoriaGastoCreate,
    CategoriaGastoResponse,
    GastoCreate,
    GastoResponse,
)
from app.domains.usuarios.models import Usuario

router = APIRouter()


@router.get("/categorias", response_model=list[CategoriaGastoResponse])
def listar_categorias(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    from app.domains.gastos import repository
    return repository.listar_categorias(db)


@router.post("/categorias", response_model=CategoriaGastoResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: CategoriaGastoCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.crear_categoria(db, data, actor)


@router.get("", response_model=list[GastoResponse])
def listar_gastos(
    skip: int = 0,
    limit: int = 100,
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.listar_gastos(db, skip=skip, limit=limit, mes=mes, anio=anio, actor=actor)


@router.post("", response_model=GastoResponse, status_code=status.HTTP_201_CREATED)
def crear_gasto(
    data: GastoCreate,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return service.crear_gasto(db, data, actor)
