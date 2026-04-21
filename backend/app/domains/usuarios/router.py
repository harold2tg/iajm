from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.domains.usuarios import service
from app.domains.usuarios.models import Usuario
from app.domains.usuarios.schemas import (
    AsignarRolRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UsuarioCreate,
    UsuarioListItem,
    UsuarioOut,
    UsuarioRolOut,
    UsuarioUpdate,
)

# ── Auth (público) ────────────────────────────────────────────────────────────
auth_router = APIRouter()


@auth_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    ip = request.client.host if request.client else "unknown"
    return service.login(db, email=body.email, password=body.password, ip_address=ip)


@auth_router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return service.refresh_tokens(db, body.refresh_token)


# ── Usuarios (protegido) ──────────────────────────────────────────────────────
router = APIRouter()


@router.get("/me", response_model=UsuarioOut)
def me(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    return current_user


@router.get("/", response_model=list[UsuarioListItem])
def listar(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> list[Usuario]:
    return service.listar_usuarios(db, skip=skip, limit=limit)


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear(
    body: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> Usuario:
    return service.crear_usuario(db, body, creado_por=admin)


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener(
    usuario_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Usuario:
    return service.obtener_usuario(db, usuario_id)


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar(
    usuario_id: uuid.UUID,
    body: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Usuario:
    return service.actualizar_usuario(db, usuario_id, body)


@router.post("/{usuario_id}/roles", response_model=UsuarioRolOut, status_code=status.HTTP_201_CREATED)
def asignar_rol(
    usuario_id: uuid.UUID,
    body: AsignarRolRequest,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
) -> UsuarioRolOut:
    return service.asignar_rol(db, usuario_id, body, asignado_por=admin)


@router.delete("/{usuario_id}/roles/{rol_id}")
def remover_rol(
    usuario_id: uuid.UUID,
    rol_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
) -> Response:
    service.remover_rol(db, usuario_id, rol_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
