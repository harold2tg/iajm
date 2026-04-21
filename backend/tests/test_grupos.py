from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domains.grupos.models import Grupo, TipoGrupoEnum
from app.domains.usuarios.models import RolEnum, Usuario, UsuarioRol


# ── Helpers ───────────────────────────────────────────────────────────────────

def crear_grupo_test(
    db: Session,
    nombre: str = "Grupo Test",
    tipo: TipoGrupoEnum = TipoGrupoEnum.infancia,
    edad_minima: int = 4,
    edad_maxima: int = 6,
) -> Grupo:
    grupo = Grupo(
        nombre=nombre,
        tipo=tipo,
        edad_minima=edad_minima,
        edad_maxima=edad_maxima,
    )
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


def crear_usuario_test(
    db: Session,
    email: str,
    password: str,
    roles: list[RolEnum] | None = None,
    grupo_id: uuid.UUID | None = None,
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
        gid = grupo_id if rol == RolEnum.asesor_grupo else None
        usuario_rol = UsuarioRol(usuario_id=usuario.id, rol=rol, grupo_id=gid)
        db.add(usuario_rol)
    db.commit()
    db.refresh(usuario)
    return usuario


def get_token(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_listar_grupos_autenticado(client: TestClient, db: Session) -> None:
    """Usuario autenticado puede listar todos los grupos."""
    crear_grupo_test(db, nombre="Trigo Verde", edad_minima=4, edad_maxima=6)
    crear_grupo_test(db, nombre="Adolescencia", tipo=TipoGrupoEnum.adolescencia, edad_minima=13, edad_maxima=15)
    crear_usuario_test(db, "user@test.com", "pass123", roles=[RolEnum.observador])
    token = get_token(client, "user@test.com", "pass123")

    resp = client.get("/api/v1/grupos/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2
    nombres = [g["nombre"] for g in body]
    assert "Trigo Verde" in nombres
    assert "Adolescencia" in nombres


def test_listar_grupos_sin_token(client: TestClient, db: Session) -> None:
    """Sin JWT la respuesta es 401."""
    crear_grupo_test(db)

    resp = client.get("/api/v1/grupos/")
    assert resp.status_code == 401


def test_mis_grupos_asesor(client: TestClient, db: Session) -> None:
    """Asesor de grupo ve solo los grupos asignados a él."""
    grupo = crear_grupo_test(db, nombre="Juventud", tipo=TipoGrupoEnum.juventud, edad_minima=16, edad_maxima=24)
    crear_grupo_test(db, nombre="Otro Grupo", edad_minima=4, edad_maxima=6)
    crear_usuario_test(
        db,
        email="asesor@test.com",
        password="pass123",
        roles=[RolEnum.asesor_grupo],
        grupo_id=grupo.id,
    )
    token = get_token(client, "asesor@test.com", "pass123")

    resp = client.get("/api/v1/grupos/mis-grupos", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == str(grupo.id)
    assert body[0]["nombre"] == "Juventud"


def test_actualizar_grupo_como_admin(client: TestClient, db: Session) -> None:
    """Admin puede actualizar el nombre de un grupo."""
    grupo = crear_grupo_test(db, nombre="Nombre Viejo", edad_minima=4, edad_maxima=6)
    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    resp = client.patch(
        f"/api/v1/grupos/{grupo.id}",
        json={"nombre": "Nombre Nuevo"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["nombre"] == "Nombre Nuevo"
    assert body["edad_minima"] == 4  # no cambió
    assert body["edad_maxima"] == 6  # no cambió


def test_actualizar_grupo_sin_ser_admin(client: TestClient, db: Session) -> None:
    """Un no-admin recibe 403 al intentar actualizar un grupo."""
    grupo = crear_grupo_test(db)
    crear_usuario_test(db, "obs@test.com", "pass123", roles=[RolEnum.observador])
    token = get_token(client, "obs@test.com", "pass123")

    resp = client.patch(
        f"/api/v1/grupos/{grupo.id}",
        json={"nombre": "Intruso"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_actualizar_rango_invalido(client: TestClient, db: Session) -> None:
    """RN-GRP-001: edad_minima >= edad_maxima debe devolver 422."""
    grupo = crear_grupo_test(db, edad_minima=4, edad_maxima=6)
    crear_usuario_test(db, "admin2@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin2@test.com", "adminpass")

    # Caso 1: ambos enviados, minima >= maxima en el payload
    resp = client.patch(
        f"/api/v1/grupos/{grupo.id}",
        json={"edad_minima": 10, "edad_maxima": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422

    # Caso 2: solo edad_minima, que queda mayor que la maxima actual (6)
    resp2 = client.patch(
        f"/api/v1/grupos/{grupo.id}",
        json={"edad_minima": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 422
