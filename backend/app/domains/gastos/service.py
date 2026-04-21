import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.gastos import repository
from app.domains.gastos.models import CategoriaGasto, Gasto
from app.domains.gastos.schemas import CategoriaGastoCreate, GastoCreate
from app.domains.usuarios.models import RolEnum, Usuario


def _require_tesoreria(actor: Usuario) -> None:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles and RolEnum.asesor_tesoreria not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador o asesor_tesoreria",
        )


def crear_categoria(db: Session, data: CategoriaGastoCreate, actor: Usuario) -> CategoriaGasto:
    _require_tesoreria(actor)
    return repository.crear_categoria(db, nombre=data.nombre)


def crear_gasto(db: Session, data: GastoCreate, actor: Usuario) -> Gasto:
    _require_tesoreria(actor)
    categoria = repository.get_categoria(db, data.categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    valor_total = data.cantidad * data.valor_unitario
    return repository.crear_gasto(
        db,
        fecha=data.fecha,
        mes=data.fecha.month,
        descripcion=data.descripcion,
        cantidad=data.cantidad,
        valor_unitario=data.valor_unitario,
        valor_total=valor_total,
        categoria_id=data.categoria_id,
    )


def listar_gastos(
    db: Session,
    skip: int,
    limit: int,
    mes: int | None,
    anio: int | None,
    actor: Usuario,
) -> list[Gasto]:
    return repository.listar_gastos(db, skip=skip, limit=limit, mes=mes, anio=anio)


def sum_gastos_mes(db: Session, mes: int, anio: int) -> float:
    return repository.sum_gastos_mes(db, mes=mes, anio=anio)
