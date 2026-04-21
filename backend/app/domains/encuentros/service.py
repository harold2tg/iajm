from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domains.encuentros import repository
from app.domains.encuentros.models import (
    EstadoAsistenciaEnum,
    EstadoEncuentroEnum,
)
from app.domains.encuentros.schemas import (
    AsistenciaCreate,
    EncuentroCreate,
    EncuentroResponse,
    EncuentroUpdate,
    MetricasMiembro,
)
from app.domains.grupos.service import get_grupo_or_404
from app.domains.miembros.repository import get_by_grupo as get_miembros_by_grupo
from app.domains.usuarios.models import RolEnum, Usuario


@dataclass
class CerrarEncuentroResult:
    encuentro: object
    advertencia: Optional[str]

logger = logging.getLogger(__name__)

# ─── Helpers ──────────────────────────────────────────────────────────────────

CONSAGRACION_MESES_MINIMO = 6
CONSAGRACION_PORCENTAJE_MINIMO = 70.0


def _tiene_rol(actor: Usuario, rol: RolEnum) -> bool:
    return any(r.rol == rol for r in actor.roles)


def _es_admin(actor: Usuario) -> bool:
    return _tiene_rol(actor, RolEnum.administrador)


def _verificar_acceso_grupo(
    actor: Usuario,
    grupo_id: uuid.UUID,
    grupos_actor: list[uuid.UUID],
) -> None:
    """Lanza 403 si el actor no tiene acceso al grupo dado."""
    if _es_admin(actor):
        return
    if _tiene_rol(actor, RolEnum.asesor_grupo):
        if grupo_id not in grupos_actor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenés permiso para operar en este grupo",
            )
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tenés permiso para realizar esta acción",
    )


def _get_encuentro_or_404(db: Session, encuentro_id: uuid.UUID):
    enc = repository.get_by_id(db, encuentro_id)
    if enc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Encuentro '{encuentro_id}' no encontrado",
        )
    return enc


def _build_encuentro_response(db: Session, encuentro) -> EncuentroResponse:
    asistencias = repository.get_asistencias_encuentro(db, encuentro.id)
    total_asistentes = sum(
        1 for a in asistencias if a.estado == EstadoAsistenciaEnum.asistio
    )
    total = len(asistencias)
    porcentaje = (total_asistentes / total * 100) if total > 0 else 0.0
    return EncuentroResponse(
        id=encuentro.id,
        grupo_id=encuentro.grupo_id,
        fecha=encuentro.fecha,
        creado_por=encuentro.creado_por,
        tema=encuentro.tema,
        observaciones=encuentro.observaciones,
        estado=encuentro.estado,
        creado_en=encuentro.creado_en,
        cerrado_en=encuentro.cerrado_en,
        total_asistentes=total_asistentes,
        porcentaje_asistencia=round(porcentaje, 2),
    )


# ─── Service functions ────────────────────────────────────────────────────────


def crear_encuentro(
    db: Session,
    data: EncuentroCreate,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> object:
    # RN-ENC-002: verificar permiso
    _verificar_acceso_grupo(actor, data.grupo_id, grupos_actor)

    # Verificar que el grupo existe
    get_grupo_or_404(db, data.grupo_id)

    # RN-ENC-001: unicidad grupo+fecha
    existente = repository.get_by_grupo_y_fecha(db, data.grupo_id, data.fecha)
    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un encuentro para el grupo '{data.grupo_id}' en la fecha {data.fecha}",
        )

    # Crear encuentro
    encuentro = repository.create(
        db,
        grupo_id=data.grupo_id,
        fecha=data.fecha,
        tema=data.tema,
        observaciones=data.observaciones,
        estado=EstadoEncuentroEnum.abierto,
        creado_por=actor.id,
    )

    # Pre-poblar asistencia: un registro no_asistio por cada miembro activo
    miembros = get_miembros_by_grupo(db, data.grupo_id, solo_activos=True)
    for miembro in miembros:
        repository.create_asistencia(
            db,
            encuentro_id=encuentro.id,
            miembro_id=miembro.id,
            estado=EstadoAsistenciaEnum.no_asistio,
            registrado_por=None,
        )

    return encuentro


def obtener_encuentro(
    db: Session,
    encuentro_id: uuid.UUID,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> object:
    enc = _get_encuentro_or_404(db, encuentro_id)
    _verificar_acceso_grupo(actor, enc.grupo_id, grupos_actor)
    return enc


def listar_encuentros(
    db: Session,
    grupo_id: Optional[uuid.UUID],
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
    skip: int = 0,
    limit: int = 100,
) -> list:
    if grupo_id is not None:
        _verificar_acceso_grupo(actor, grupo_id, grupos_actor)
        return repository.get_by_grupo(db, grupo_id, skip=skip, limit=limit)

    # Sin filtro de grupo: admin ve todo, asesor ve sus grupos
    if _es_admin(actor):
        # Retornar todos — iteramos por grupos
        from sqlalchemy import select
        from app.domains.encuentros.models import Encuentro
        stmt = (
            select(Encuentro)
            .order_by(Encuentro.fecha.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())
    else:
        if not grupos_actor:
            return []
        from sqlalchemy import select
        from app.domains.encuentros.models import Encuentro
        stmt = (
            select(Encuentro)
            .where(Encuentro.grupo_id.in_(grupos_actor))
            .order_by(Encuentro.fecha.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())


def registrar_asistencia(
    db: Session,
    encuentro_id: uuid.UUID,
    miembro_id: uuid.UUID,
    estado: EstadoAsistenciaEnum,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> object:
    enc = _get_encuentro_or_404(db, encuentro_id)

    # RN-ENC-003: solo encuentros abiertos
    if enc.estado != EstadoEncuentroEnum.abierto:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede registrar asistencia en encuentros con estado 'abierto'",
        )

    _verificar_acceso_grupo(actor, enc.grupo_id, grupos_actor)

    asistencia = repository.get_asistencia(db, encuentro_id, miembro_id)
    if asistencia is not None:
        return repository.update_asistencia(db, asistencia, estado, actor.id)
    else:
        return repository.create_asistencia(
            db,
            encuentro_id=encuentro_id,
            miembro_id=miembro_id,
            estado=estado,
            registrado_por=actor.id,
        )


def registrar_asistencia_bulk(
    db: Session,
    encuentro_id: uuid.UUID,
    asistencias: list[AsistenciaCreate],
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> list:
    try:
        results = []
        for item in asistencias:
            a = registrar_asistencia(
                db, encuentro_id, item.miembro_id, item.estado, actor, grupos_actor
            )
            results.append(a)
        return results
    except Exception:
        db.rollback()
        raise


def cerrar_encuentro(
    db: Session,
    encuentro_id: uuid.UUID,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> CerrarEncuentroResponse:
    enc = _get_encuentro_or_404(db, encuentro_id)
    _verificar_acceso_grupo(actor, enc.grupo_id, grupos_actor)

    # RN-ENC-004: detectar miembros activos sin registro
    miembros = get_miembros_by_grupo(db, enc.grupo_id, solo_activos=True)
    asistencias = repository.get_asistencias_encuentro(db, encuentro_id)
    miembros_con_registro = {a.miembro_id for a in asistencias}

    sin_registro = [
        m for m in miembros if m.id not in miembros_con_registro
    ]

    advertencia: Optional[str] = None
    if sin_registro:
        nombres = ", ".join(m.nombre_completo for m in sin_registro)
        advertencia = f"Los siguientes miembros no tienen registro de asistencia: {nombres}"

    enc_actualizado = repository.update(
        db,
        enc,
        estado=EstadoEncuentroEnum.cerrado,
        cerrado_en=datetime.now(tz=timezone.utc),
    )

    enc_response = _build_encuentro_response(db, enc_actualizado)
    return CerrarEncuentroResult(encuentro=enc_response, advertencia=advertencia)


def reabrir_encuentro(
    db: Session,
    encuentro_id: uuid.UUID,
    motivo: str,
    actor: Usuario,
) -> object:
    # RN-ENC-006: solo admin
    if not _es_admin(actor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede reabrir un encuentro",
        )

    enc = _get_encuentro_or_404(db, encuentro_id)

    if enc.estado == EstadoEncuentroEnum.abierto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El encuentro ya está abierto",
        )

    logger.info(
        "Reapertura de encuentro: id=%s, motivo=%s, actor=%s (%s)",
        enc.id,
        motivo,
        actor.id,
        getattr(actor, "email", "?"),
    )

    enc_actualizado = repository.update(
        db,
        enc,
        estado=EstadoEncuentroEnum.abierto,
        cerrado_en=None,
    )

    repository.create_log_reapertura(
        db,
        encuentro_id=enc.id,
        reabierto_por=actor.id,
        motivo=motivo,
    )

    return enc_actualizado


def calcular_metricas_encuentro(db: Session, encuentro_id: uuid.UUID) -> dict:
    enc = _get_encuentro_or_404(db, encuentro_id)
    miembros_activos = get_miembros_by_grupo(db, enc.grupo_id, solo_activos=True)
    asistencias = repository.get_asistencias_encuentro(db, encuentro_id)
    total_asistentes = sum(
        1 for a in asistencias if a.estado == EstadoAsistenciaEnum.asistio
    )
    total_miembros = len(miembros_activos)
    porcentaje = (total_asistentes / total_miembros * 100) if total_miembros > 0 else 0.0
    return {
        "total_asistentes": total_asistentes,
        "total_miembros_activos": total_miembros,
        "porcentaje_asistencia": round(porcentaje, 2),
    }


def calcular_metricas_miembro(
    db: Session,
    miembro_id: uuid.UUID,
    grupo_id: uuid.UUID,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
) -> MetricasMiembro:
    from app.domains.miembros.repository import get_by_id as get_miembro_by_id

    miembro = get_miembro_by_id(db, miembro_id)
    if miembro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Miembro '{miembro_id}' no encontrado",
        )

    historial = repository.get_historial_asistencia_miembro(
        db, miembro_id, grupo_id=grupo_id, desde=desde, hasta=hasta
    )

    total_encuentros = len(historial)
    total_asistio = sum(1 for a in historial if a.estado == EstadoAsistenciaEnum.asistio)
    porcentaje = (total_asistio / total_encuentros * 100) if total_encuentros > 0 else 0.0

    # Racha: contar desde el más reciente hacia atrás mientras estado == asistio
    racha_actual = 0
    for a in historial:  # historial ya está ordenado desc por fecha
        if a.estado == EstadoAsistenciaEnum.asistio:
            racha_actual += 1
        else:
            break

    # Aptitud para consagración
    hoy = date.today()
    meses_ingreso = (
        (hoy.year - miembro.fecha_ingreso.year) * 12
        + (hoy.month - miembro.fecha_ingreso.month)
    )
    apto_consagracion = (
        meses_ingreso >= CONSAGRACION_MESES_MINIMO
        and porcentaje >= CONSAGRACION_PORCENTAJE_MINIMO
    )

    return MetricasMiembro(
        miembro_id=miembro_id,
        nombre=miembro.nombre_completo,
        total_encuentros=total_encuentros,
        total_asistio=total_asistio,
        porcentaje=round(porcentaje, 2),
        racha_actual=racha_actual,
        apto_consagracion=apto_consagracion,
    )


def actualizar_encuentro(
    db: Session,
    encuentro_id: uuid.UUID,
    data: EncuentroUpdate,
    actor: Usuario,
    grupos_actor: list[uuid.UUID],
) -> object:
    enc = _get_encuentro_or_404(db, encuentro_id)
    _verificar_acceso_grupo(actor, enc.grupo_id, grupos_actor)

    if enc.estado != EstadoEncuentroEnum.abierto:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede modificar un encuentro con estado 'abierto'",
        )

    campos = data.model_dump(exclude_unset=True)
    return repository.update(db, enc, **campos)
