from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.miembros.models import Miembro, TipoMiembroEnum
from app.domains.miembros.schemas import MiembroCreate, MiembroUpdate
from app.domains.miembros.repository import (
    get_by_id,
    get_all,
    get_by_grupo,
    get_by_grupos,
    create,
    update as repo_update,
    crear_asistencia_encuentro,
    get_historial_grupo,
)
from app.domains.grupos.repository import get_grupo_para_edad
from app.domains.usuarios.models import Usuario, RolEnum


def _calcular_edad_y_tipo(fecha_nacimiento: date) -> tuple[int, TipoMiembroEnum]:
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    if edad < 4 or edad > 24:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Edad {edad} fuera del rango permitido (4–24 años)",
        )
    if edad <= 12:
        return edad, TipoMiembroEnum.infancia
    elif edad <= 15:
        return edad, TipoMiembroEnum.adolescencia
    else:
        return edad, TipoMiembroEnum.juventud


def _validar_campos_por_tipo(
    tipo: TipoMiembroEnum, data: MiembroCreate | MiembroUpdate
) -> dict:
    campos: dict = {}

    telefono_personal = getattr(data, "telefono_personal", None)
    nombre_acudiente = getattr(data, "nombre_acudiente", None)
    telefono_acudiente = getattr(data, "telefono_acudiente", None)

    if tipo == TipoMiembroEnum.infancia:
        if not nombre_acudiente:
            raise HTTPException(422, detail="nombre_acudiente es obligatorio para infancia")
        if not telefono_acudiente:
            raise HTTPException(422, detail="telefono_acudiente es obligatorio para infancia")
        campos["telefono_personal"] = None
        campos["nombre_acudiente"] = nombre_acudiente
        campos["telefono_acudiente"] = telefono_acudiente

    elif tipo == TipoMiembroEnum.adolescencia:
        if not nombre_acudiente:
            raise HTTPException(422, detail="nombre_acudiente es obligatorio para adolescencia")
        if not telefono_acudiente:
            raise HTTPException(422, detail="telefono_acudiente es obligatorio para adolescencia")
        campos["telefono_personal"] = telefono_personal
        campos["nombre_acudiente"] = nombre_acudiente
        campos["telefono_acudiente"] = telefono_acudiente

    elif tipo == TipoMiembroEnum.juventud:
        if not telefono_personal:
            raise HTTPException(422, detail="telefono_personal es obligatorio para juventud")
        campos["telefono_personal"] = telefono_personal
        campos["nombre_acudiente"] = None
        campos["telefono_acudiente"] = None

    return campos


def _tiene_rol(actor: Usuario, *roles: RolEnum) -> bool:
    return any(r.rol in roles for r in actor.roles)


def crear_miembro(db: Session, data: MiembroCreate, actor: Usuario) -> Miembro:
    if not _tiene_rol(actor, RolEnum.administrador, RolEnum.asesor_grupo):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Sin permiso para crear miembros")

    edad, tipo = _calcular_edad_y_tipo(data.fecha_nacimiento)

    grupo = get_grupo_para_edad(db, edad)
    if grupo is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No hay grupo configurado para esa edad",
        )

    if _tiene_rol(actor, RolEnum.asesor_grupo) and not _tiene_rol(actor, RolEnum.administrador):
        grupos_actor = [r.grupo_id for r in actor.roles if r.grupo_id is not None]
        if grupo.id not in grupos_actor:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="No tenés acceso al grupo asignado a este miembro",
            )

    campos = _validar_campos_por_tipo(tipo, data)

    miembro = Miembro(
        nombre_completo=data.nombre_completo,
        fecha_nacimiento=data.fecha_nacimiento,
        edad=edad,
        tipo=tipo,
        grupo_id=grupo.id,
        fecha_ingreso=data.fecha_ingreso,
        activo=True,
        **campos,
    )
    miembro = create(db, miembro)

    if data.encuentro_id is not None:
        miembro.ingresado_en_encuentro_id = data.encuentro_id
        crear_asistencia_encuentro(db, data.encuentro_id, miembro.id, actor.id)

    db.commit()
    db.refresh(miembro)
    return miembro


def actualizar_miembro(
    db: Session, miembro_id: uuid.UUID, data: MiembroUpdate, actor: Usuario
) -> Miembro:
    if not _tiene_rol(actor, RolEnum.administrador, RolEnum.asesor_grupo):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Sin permiso")

    miembro = get_by_id(db, miembro_id)
    if miembro is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Miembro no encontrado")

    if _tiene_rol(actor, RolEnum.asesor_grupo) and not _tiene_rol(actor, RolEnum.administrador):
        grupos_actor = [r.grupo_id for r in actor.roles if r.grupo_id is not None]
        if miembro.grupo_id not in grupos_actor:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail="No tenés acceso a este miembro"
            )

    update_data = data.model_dump(exclude_unset=True)

    campos_condicionales = {"telefono_personal", "nombre_acudiente", "telefono_acudiente"}
    if update_data.keys() & campos_condicionales:
        merged = MiembroUpdate(
            telefono_personal=update_data.get("telefono_personal", miembro.telefono_personal),
            nombre_acudiente=update_data.get("nombre_acudiente", miembro.nombre_acudiente),
            telefono_acudiente=update_data.get("telefono_acudiente", miembro.telefono_acudiente),
        )
        campos = _validar_campos_por_tipo(miembro.tipo, merged)
        update_data.update(campos)

    for field, value in update_data.items():
        setattr(miembro, field, value)

    repo_update(db, miembro)
    db.commit()
    db.refresh(miembro)
    return miembro


def listar_miembros(
    db: Session, actor: Usuario, grupos_actor: list[uuid.UUID],
    grupo_id: Optional[uuid.UUID] = None,
) -> list[Miembro]:
    if _tiene_rol(actor, RolEnum.administrador, RolEnum.observador):
        if grupo_id is not None:
            return get_by_grupo(db, grupo_id)
        return get_all(db)
    elif _tiene_rol(actor, RolEnum.asesor_grupo):
        if grupo_id is not None:
            if grupo_id not in grupos_actor:
                raise HTTPException(status.HTTP_403_FORBIDDEN, detail="No tenés acceso a ese grupo")
            return get_by_grupo(db, grupo_id)
        return get_by_grupos(db, grupos_actor)
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Sin permiso para ver miembros")


def obtener_miembro(
    db: Session,
    miembro_id: uuid.UUID,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> Miembro:
    miembro = get_by_id(db, miembro_id)
    if miembro is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Miembro no encontrado")

    if _tiene_rol(actor, RolEnum.administrador, RolEnum.observador):
        return miembro
    elif _tiene_rol(actor, RolEnum.asesor_grupo):
        if miembro.grupo_id not in grupos_actor:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail="No tenés acceso a este miembro"
            )
        return miembro
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Sin permiso")


def desactivar_miembro(db: Session, miembro_id: uuid.UUID, actor: Usuario) -> Miembro:
    if not _tiene_rol(actor, RolEnum.administrador):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede desactivar miembros",
        )

    miembro = get_by_id(db, miembro_id)
    if miembro is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Miembro no encontrado")

    miembro.activo = False
    db.commit()
    db.refresh(miembro)
    return miembro


def listar_historial_grupo(
    db: Session,
    miembro_id: uuid.UUID,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> list:
    miembro = obtener_miembro(db, miembro_id, actor, grupos_actor)
    return get_historial_grupo(db, miembro.id)
