from __future__ import annotations

import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.asesores import repository as repo
from app.domains.asesores.models import Asesor, AsesorGrupo, CuotaAsesor, EstadoCuotaEnum, TipoAsesorEnum
from app.domains.asesores.schemas import AsesorCreate, AsesorResponse, AsesorUpdate, GrupoSimple, RegistrarPagoCuotaRequest
from app.domains.grupos.models import Grupo
from app.domains.usuarios.models import RolEnum, Usuario


def obtener_asesor_or_404(db: Session, asesor_id: uuid.UUID) -> Asesor:
    asesor = repo.get_by_id(db, asesor_id)
    if asesor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asesor con id '{asesor_id}' no encontrado",
        )
    return asesor


def build_asesor_response(db: Session, asesor: Asesor) -> AsesorResponse:
    grupos: list[GrupoSimple] = []
    for ag in asesor.grupos:
        grupo = db.get(Grupo, ag.grupo_id)
        if grupo is not None:
            grupos.append(GrupoSimple(id=grupo.id, nombre=grupo.nombre))

    return AsesorResponse(
        id=asesor.id,
        nombre_completo=asesor.nombre_completo,
        telefono=asesor.telefono,
        tipo=asesor.tipo,
        fecha_nacimiento=asesor.fecha_nacimiento,
        usuario_id=asesor.usuario_id,
        activo=asesor.activo,
        creado_en=asesor.creado_en,
        grupos=grupos,
    )


def _require_admin_or_tesoreria(actor: Usuario, detail: str = "Acción no permitida") -> None:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles and RolEnum.asesor_tesoreria not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def crear_asesor(db: Session, data: AsesorCreate, actor: Usuario) -> Asesor:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear asesores",
        )
    asesor = repo.create(
        db,
        nombre_completo=data.nombre_completo,
        telefono=data.telefono,
        tipo=data.tipo,
        usuario_id=data.usuario_id,
    )
    for grupo_id in data.grupo_ids:
        # Verificar que el grupo existe
        grupo = db.get(Grupo, grupo_id)
        if grupo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grupo '{grupo_id}' no encontrado",
            )
        repo.add_grupo(db, asesor.id, grupo_id)
    db.refresh(asesor)
    return asesor


def actualizar_asesor(db: Session, asesor_id: uuid.UUID, data: AsesorUpdate, actor: Usuario) -> Asesor:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden actualizar asesores",
        )
    asesor = obtener_asesor_or_404(db, asesor_id)
    campos = data.model_dump(exclude_unset=True)
    return repo.update(db, asesor, **campos)


def desactivar_asesor(db: Session, asesor_id: uuid.UUID, actor: Usuario) -> Asesor:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar asesores",
        )
    asesor = obtener_asesor_or_404(db, asesor_id)

    # RN-ASE-001: asesor base no puede ser el único en algún grupo
    if asesor.tipo == TipoAsesorEnum.base:
        for ag in asesor.grupos:
            count = repo.count_asesores_base_en_grupo(db, ag.grupo_id)
            if count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El asesor es el único base activo en el grupo {ag.grupo_id}",
                )

    return repo.update(db, asesor, activo=False)


def listar_asesores(db: Session) -> list[Asesor]:
    return repo.get_all(db)


def asignar_grupo(db: Session, asesor_id: uuid.UUID, grupo_id: uuid.UUID, actor: Usuario) -> AsesorGrupo:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden asignar grupos",
        )
    obtener_asesor_or_404(db, asesor_id)

    grupo = db.get(Grupo, grupo_id)
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo '{grupo_id}' no encontrado",
        )

    # Verificar si ya está asignado
    existentes = repo.get_grupos_de_asesor(db, asesor_id)
    if any(ag.grupo_id == grupo_id for ag in existentes):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El asesor ya está asignado a ese grupo",
        )

    return repo.add_grupo(db, asesor_id, grupo_id)


def remover_grupo(db: Session, asesor_id: uuid.UUID, grupo_id: uuid.UUID, actor: Usuario) -> None:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden remover grupos",
        )
    asesor = obtener_asesor_or_404(db, asesor_id)

    # RN-ASE-001
    if asesor.tipo == TipoAsesorEnum.base:
        count = repo.count_asesores_base_en_grupo(db, grupo_id)
        if count <= 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El grupo quedaría sin asesor base",
            )

    removed = repo.remove_grupo(db, asesor_id, grupo_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El asesor no está asignado a ese grupo",
        )


def generar_cuotas_mes(db: Session, mes: int, anio: int, monto_default: float) -> int:
    asesores = repo.get_all(db, solo_activos=True)
    creadas = 0
    for asesor in asesores:
        if not repo.existe_cuota(db, asesor.id, mes, anio):
            repo.create_cuota(
                db,
                asesor_id=asesor.id,
                mes=mes,
                anio=anio,
                monto=Decimal(str(monto_default)),
                estado=EstadoCuotaEnum.pendiente,
            )
            creadas += 1
    return creadas


def registrar_pago_cuota(
    db: Session,
    cuota_id: uuid.UUID,
    data: RegistrarPagoCuotaRequest,
    actor: Usuario,
) -> CuotaAsesor:
    roles = [r.rol for r in actor.roles]
    if RolEnum.administrador not in roles and RolEnum.asesor_tesoreria not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador o asesor_tesoreria",
        )
    cuota = repo.get_cuota_by_id(db, cuota_id)
    if cuota is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuota '{cuota_id}' no encontrada",
        )
    return repo.update_cuota(
        db,
        cuota,
        fecha_pago=data.fecha_pago,
        monto=data.monto,
        estado=EstadoCuotaEnum.pagado,
    )


def listar_cuotas(
    db: Session,
    asesor_id: uuid.UUID | None = None,
    mes: int | None = None,
    anio: int | None = None,
) -> list[CuotaAsesor]:
    return repo.get_all_cuotas(db, asesor_id=asesor_id, mes=mes, anio=anio)
