from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Importar Grupo para registrar la tabla en Base.metadata antes de create_all
from app.domains.grupos.models import Grupo  # noqa: F401 - needed for FK resolution
from app.core.security import hash_password
from app.domains.usuarios.models import RolEnum, Usuario, UsuarioRol


# ── Helpers ───────────────────────────────────────────────────────────────────

def crear_usuario_test(
    db: Session,
    email: str,
    password: str,
    roles: list[RolEnum] | None = None,
    nombre: str = "Test User",
) -> Usuario:
    usuario = Usuario(
        nombre_completo=nombre,
        email=email,
        password_hash=hash_password(password),
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    for rol in (roles or []):
        usuario_rol = UsuarioRol(usuario_id=usuario.id, rol=rol)
        db.add(usuario_rol)
    db.commit()
    db.refresh(usuario)
    return usuario


def get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── Tests de autenticación ────────────────────────────────────────────────────

def test_login_exitoso(client: TestClient, db: Session) -> None:
    crear_usuario_test(db, "user@test.com", "secret123")
    resp = client.post("/api/v1/auth/login", json={"email": "user@test.com", "password": "secret123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_credenciales_incorrectas(client: TestClient, db: Session) -> None:
    crear_usuario_test(db, "user2@test.com", "correcta")
    resp = client.post("/api/v1/auth/login", json={"email": "user2@test.com", "password": "incorrecta"})
    assert resp.status_code == 401
    assert "Credenciales" in resp.json()["detail"]


def test_login_lockout(client: TestClient, db: Session) -> None:
    crear_usuario_test(db, "lockme@test.com", "correcta")

    # Generar MAX_LOGIN_ATTEMPTS (5) intentos fallidos
    for _ in range(5):
        client.post("/api/v1/auth/login", json={"email": "lockme@test.com", "password": "mal"})

    # El 6to intento debe devolver 423
    resp = client.post("/api/v1/auth/login", json={"email": "lockme@test.com", "password": "correcta"})
    assert resp.status_code == 423
    assert "bloqueada" in resp.json()["detail"].lower()


# ── Tests de usuarios ─────────────────────────────────────────────────────────

def test_crear_usuario_como_admin(client: TestClient, db: Session) -> None:
    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    resp = client.post(
        "/api/v1/usuarios/",
        json={"nombre_completo": "Nuevo User", "email": "nuevo@test.com", "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "nuevo@test.com"
    assert body["activo"] is True


def test_crear_usuario_sin_ser_admin(client: TestClient, db: Session) -> None:
    crear_usuario_test(db, "obs@test.com", "pass", roles=[RolEnum.observador])
    token = get_token(client, "obs@test.com", "pass")

    resp = client.post(
        "/api/v1/usuarios/",
        json={"nombre_completo": "Intruso", "email": "intruso@test.com", "password": "pass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


# ── Tests de reglas de negocio de roles ───────────────────────────────────────

def test_asignar_rol_observador_con_otro_rol(client: TestClient, db: Session) -> None:
    """RN-USR-002: no se puede asignar observador a usuario con roles existentes."""
    admin = crear_usuario_test(db, "admin2@test.com", "adminpass", roles=[RolEnum.administrador])
    target = crear_usuario_test(db, "target@test.com", "pass", roles=[RolEnum.asesor_tesoreria])
    token = get_token(client, "admin2@test.com", "adminpass")

    resp = client.post(
        f"/api/v1/usuarios/{target.id}/roles",
        json={"rol": "observador"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
    assert "observador" in resp.json()["detail"].lower()


def test_asignar_rol_asesor_grupo_sin_grupo_id(client: TestClient, db: Session) -> None:
    """RN-USR-003: asesor_grupo requiere grupo_id."""
    admin = crear_usuario_test(db, "admin3@test.com", "adminpass", roles=[RolEnum.administrador])
    target = crear_usuario_test(db, "target2@test.com", "pass")
    token = get_token(client, "admin3@test.com", "adminpass")

    resp = client.post(
        f"/api/v1/usuarios/{target.id}/roles",
        json={"rol": "asesor_grupo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
    assert "grupo_id" in resp.json()["detail"].lower()


# ── Test de perfil autenticado ────────────────────────────────────────────────

def test_me_retorna_usuario_autenticado(client: TestClient, db: Session) -> None:
    crear_usuario_test(db, "me@test.com", "mypass")
    token = get_token(client, "me@test.com", "mypass")

    resp = client.get("/api/v1/usuarios/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "me@test.com"
    assert body["activo"] is True
