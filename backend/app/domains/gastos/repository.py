import uuid
from datetime import date

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.domains.gastos.models import CategoriaGasto, Gasto


def crear_categoria(db: Session, nombre: str) -> CategoriaGasto:
    categoria = CategoriaGasto(nombre=nombre)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def get_categoria(db: Session, id: uuid.UUID) -> CategoriaGasto | None:
    return db.get(CategoriaGasto, id)


def listar_categorias(db: Session) -> list[CategoriaGasto]:
    return db.query(CategoriaGasto).all()


def crear_gasto(
    db: Session,
    *,
    fecha: date,
    mes: int,
    descripcion: str,
    cantidad: int,
    valor_unitario: float,
    valor_total: float,
    categoria_id: uuid.UUID,
) -> Gasto:
    gasto = Gasto(
        fecha=fecha,
        mes=mes,
        descripcion=descripcion,
        cantidad=cantidad,
        valor_unitario=valor_unitario,
        valor_total=valor_total,
        categoria_id=categoria_id,
    )
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto


def listar_gastos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    mes: int | None = None,
    anio: int | None = None,
) -> list[Gasto]:
    q = db.query(Gasto)
    if mes is not None and anio is not None:
        q = q.filter(Gasto.mes == mes, extract("year", Gasto.fecha) == anio)
    return q.offset(skip).limit(limit).all()


def sum_gastos_mes(db: Session, mes: int, anio: int) -> float:
    resultado = (
        db.query(func.sum(Gasto.valor_total))
        .filter(Gasto.mes == mes, extract("year", Gasto.fecha) == anio)
        .scalar()
    )
    return float(resultado) if resultado is not None else 0.0
