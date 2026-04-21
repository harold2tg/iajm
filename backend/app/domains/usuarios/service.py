from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.domains.usuarios import repository
from app.domains.usuarios.models import RolEnum, Usuario
from app.domains.usuarios.schemas import (
    AsignarRolRequest,
    TokenResponse,
    UsuarioCreate,
    UsuarioRolOut,
    UsuarioUpdate,
)


# ── Auth ──────────────────────────────────────────────────────────────────────

def login(
    db: Session,
    email: str,
    password: str,
    ip_address: str | None = None,
) -> TokenResponse:
    """RN-USR-005: lockout tras MAX_LOGIN_ATTEMPTS intentos fallidos en LOCKOUT_MINUTES."""
    desde = datetime.now(timezone.utc) - timedelta(minutes=settings.LOCKOUT_MINUTES)
    intentos = repository.count_intentos_fallidos_recientes(db, email, desde)

    if intentos >= settings.MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=423,
            detail=f"Cuenta bloqueada. Intentá de nuevo en {settings.LOCKOUT_MINUTES} minutos.",
        )

    usuario = repository.get_usuario_by_email(db, email)

    if usuario is None or not verify_password(password, usuario.password_hash):
        repository.registrar_log_acceso(
            db,
            email_intento=email,
            exitoso=False,
            usuario_id=usuario.id if usuario else None,
            ip_address=ip_address,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not usuario.activo:
        repository.registrar_log_acceso(
            db,
            email_intento=email,
            exitoso=False,
            usuario_id=usuario.id,
            ip_address=ip_address,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    repository.update_ultimo_acceso(db, usuario)
    repository.registrar_log_acceso(
        db,
        email_intento=email,
        exitoso=True,
        usuario_id=usuario.id,
        ip_address=ip_address,
    )
    db.commit()

    token_data = {"sub": str(usuario.id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


def refresh_tokens(db: Session, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no es de tipo refresh",
        )
    usuario_id = uuid.UUID(payload["sub"])
    usuario = repository.get_usuario_by_id(db, usuario_id)
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )
    token_data = {"sub": str(usuario.id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


# ── Usuarios ──────────────────────────────────────────────────────────────────

def crear_usuario(db: Session, data: UsuarioCreate, creado_por: Usuario) -> Usuario:
    existente = repository.get_usuario_by_email(db, data.email)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    usuario = repository.create_usuario(
        db,
        nombre_completo=data.nombre_completo,
        email=data.email,
        password_hash=hash_password(data.password),
    )

    for rol_req in data.roles:
        _validar_y_agregar_rol(db, usuario, rol_req, asignado_por=creado_por.id)

    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar_usuario(
    db: Session,
    usuario_id: uuid.UUID,
    data: UsuarioUpdate,
) -> Usuario:
    usuario = repository.get_usuario_by_id(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    usuario = repository.update_usuario(
        db,
        usuario,
        nombre_completo=data.nombre_completo,
        activo=data.activo,
    )
    db.commit()
    db.refresh(usuario)
    return usuario


def listar_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return repository.get_usuarios(db, skip=skip, limit=limit)


def obtener_usuario(db: Session, usuario_id: uuid.UUID) -> Usuario:
    usuario = repository.get_usuario_by_id(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


# ── Roles ─────────────────────────────────────────────────────────────────────

def asignar_rol(
    db: Session,
    usuario_id: uuid.UUID,
    data: AsignarRolRequest,
    asignado_por: Usuario,
) -> UsuarioRolOut:
    usuario = repository.get_usuario_by_id(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    _validar_y_agregar_rol(db, usuario, data, asignado_por=asignado_por.id)
    db.commit()
    db.refresh(usuario)

    nuevo_rol = next(r for r in reversed(usuario.roles) if r.rol == data.rol)
    return UsuarioRolOut.model_validate(nuevo_rol)


def remover_rol(
    db: Session,
    usuario_id: uuid.UUID,
    rol_id: uuid.UUID,
) -> None:
    usuario_rol = repository.get_rol_by_id(db, rol_id)
    if usuario_rol is None or usuario_rol.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    repository.remove_rol(db, usuario_rol)
    db.commit()


# ── Helpers internos ──────────────────────────────────────────────────────────

def _validar_y_agregar_rol(
    db: Session,
    usuario: Usuario,
    rol_req: AsignarRolRequest,
    asignado_por: uuid.UUID | None = None,
) -> None:
    """RN-USR-002 y RN-USR-003."""
    roles_actuales = [r.rol for r in usuario.roles]

    # RN-USR-002: observador es exclusivo
    if rol_req.rol == RolEnum.observador and roles_actuales:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="observador es un rol exclusivo: el usuario ya tiene otros roles asignados",
        )
    if rol_req.rol != RolEnum.observador and RolEnum.observador in roles_actuales:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se puede asignar otro rol a un usuario con rol observador",
        )

    # RN-USR-003: asesor_grupo requiere grupo_id
    if rol_req.rol == RolEnum.asesor_grupo and rol_req.grupo_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="asesor_grupo requiere grupo_id",
        )

    repository.add_rol(
        db,
        usuario_id=usuario.id,
        rol=rol_req.rol,
        grupo_id=rol_req.grupo_id,
        asignado_por=asignado_por,
    )
