from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domains.usuarios.models import LogAcceso, Usuario, UsuarioRol


# ── Usuario ───────────────────────────────────────────────────────────────────

def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    stmt = (
        select(Usuario)
        .where(Usuario.email == email)
        .options(selectinload(Usuario.roles))
    )
    return db.execute(stmt).scalar_one_or_none()


def get_usuario_by_id(db: Session, usuario_id: uuid.UUID) -> Usuario | None:
    stmt = (
        select(Usuario)
        .where(Usuario.id == usuario_id)
        .options(selectinload(Usuario.roles))
    )
    return db.execute(stmt).scalar_one_or_none()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    stmt = select(Usuario).offset(skip).limit(limit).options(selectinload(Usuario.roles))
    return list(db.execute(stmt).scalars().all())


def create_usuario(
    db: Session,
    nombre_completo: str,
    email: str,
    password_hash: str,
) -> Usuario:
    usuario = Usuario(
        nombre_completo=nombre_completo,
        email=email,
        password_hash=password_hash,
    )
    db.add(usuario)
    db.flush()
    db.refresh(usuario)
    return usuario


def update_ultimo_acceso(db: Session, usuario: Usuario) -> None:
    usuario.ultimo_acceso = datetime.now(timezone.utc)
    db.flush()


def update_usuario(
    db: Session,
    usuario: Usuario,
    nombre_completo: str | None = None,
    activo: bool | None = None,
) -> Usuario:
    if nombre_completo is not None:
        usuario.nombre_completo = nombre_completo
    if activo is not None:
        usuario.activo = activo
    db.flush()
    db.refresh(usuario)
    return usuario


# ── Roles ─────────────────────────────────────────────────────────────────────

def add_rol(
    db: Session,
    usuario_id: uuid.UUID,
    rol: str,
    grupo_id: uuid.UUID | None = None,
    asignado_por: uuid.UUID | None = None,
) -> UsuarioRol:
    usuario_rol = UsuarioRol(
        usuario_id=usuario_id,
        rol=rol,
        grupo_id=grupo_id,
        asignado_por=asignado_por,
    )
    db.add(usuario_rol)
    db.flush()
    return usuario_rol


def remove_rol(db: Session, usuario_rol: UsuarioRol) -> None:
    db.delete(usuario_rol)
    db.flush()


def get_rol_by_id(db: Session, rol_id: uuid.UUID) -> UsuarioRol | None:
    return db.get(UsuarioRol, rol_id)


# ── Log de acceso ─────────────────────────────────────────────────────────────

def registrar_log_acceso(
    db: Session,
    email_intento: str,
    exitoso: bool,
    usuario_id: uuid.UUID | None = None,
    ip_address: str | None = None,
) -> None:
    log = LogAcceso(
        usuario_id=usuario_id,
        email_intento=email_intento,
        exitoso=exitoso,
        ip_address=ip_address,
    )
    db.add(log)
    db.flush()


def count_intentos_fallidos_recientes(
    db: Session,
    email: str,
    desde: datetime,
) -> int:
    from sqlalchemy import func

    stmt = (
        select(func.count())
        .select_from(LogAcceso)
        .where(
            LogAcceso.email_intento == email,
            LogAcceso.exitoso == False,  # noqa: E712
            LogAcceso.registrado_en >= desde,
        )
    )
    result = db.execute(stmt).scalar_one()
    return result or 0
