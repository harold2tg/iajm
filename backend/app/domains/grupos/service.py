from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.grupos import repository
from app.domains.grupos.models import Grupo
from app.domains.grupos.schemas import GrupoUpdate
from app.domains.usuarios.models import Usuario


def get_grupo_or_404(db: Session, grupo_id: uuid.UUID) -> Grupo:
    grupo = repository.get_by_id(db, grupo_id)
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo con id '{grupo_id}' no encontrado",
        )
    return grupo


def listar_grupos(db: Session) -> list[Grupo]:
    return repository.get_all(db)


def obtener_grupo(db: Session, grupo_id: uuid.UUID) -> Grupo:
    return get_grupo_or_404(db, grupo_id)


def actualizar_grupo(
    db: Session,
    grupo_id: uuid.UUID,
    data: GrupoUpdate,
    actor: Usuario,  # noqa: ARG001 — autorización delegada al router via require_admin
) -> Grupo:
    grupo = get_grupo_or_404(db, grupo_id)

    # Combinar valores actuales con los nuevos para validar el rango final
    nueva_minima = data.edad_minima if data.edad_minima is not None else grupo.edad_minima
    nueva_maxima = data.edad_maxima if data.edad_maxima is not None else grupo.edad_maxima

    if nueva_minima >= nueva_maxima:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"edad_minima ({nueva_minima}) debe ser menor que edad_maxima ({nueva_maxima})",
        )

    campos = data.model_dump(exclude_unset=True)
    grupo = repository.update(db, grupo, **campos)
    db.commit()
    db.refresh(grupo)
    return grupo


def get_grupo_para_edad(db: Session, edad: int) -> Grupo:
    grupo = repository.get_grupo_para_edad(db, edad)
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe grupo configurado para la edad {edad}",
        )
    return grupo
