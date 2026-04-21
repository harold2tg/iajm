from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import hash_password
from app.domains.usuarios.models import RolEnum, Usuario, UsuarioRol
from app.main import app


def crear_usuario_test(db: Session, email: str, roles: list[RolEnum]) -> Usuario:
    usuario = Usuario(
        nombre_completo="Test User",
        email=email,
        password_hash=hash_password("pass123"),
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    for rol in roles:
        db.add(UsuarioRol(usuario_id=usuario.id, rol=rol, grupo_id=None))
    db.commit()
    db.refresh(usuario)
    return usuario


def set_auth(usuario: Usuario) -> None:
    app.dependency_overrides[get_current_user] = lambda: usuario


def clear_auth() -> None:
    app.dependency_overrides.pop(get_current_user, None)


def test_crear_item_como_admin(client: TestClient, db: Session) -> None:
    """Admin puede crear item → 201."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp = client.post(
            "/api/v1/inventario/",
            json={"nombre": "Biblia", "cantidad": 10, "tipo": "formativo", "origen": "donacion"},
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Biblia"
    assert body["cantidad"] == 10
    assert body["tipo"] == "formativo"


def test_crear_item_sin_permiso(client: TestClient, db: Session) -> None:
    """Observador no puede crear item → 403."""
    obs = crear_usuario_test(db, "obs@test.com", [RolEnum.observador])
    set_auth(obs)
    try:
        resp = client.post(
            "/api/v1/inventario/",
            json={"nombre": "Cáliz", "cantidad": 1},
        )
    finally:
        clear_auth()

    assert resp.status_code == 403, resp.text


def test_listar_items(client: TestClient, db: Session) -> None:
    """GET /inventario/ → 200 con lista."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp = client.get("/api/v1/inventario/")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_actualizar_item(client: TestClient, db: Session) -> None:
    """Admin puede actualizar item → 200 con datos actualizados."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp_create = client.post(
            "/api/v1/inventario/",
            json={"nombre": "Rosario", "cantidad": 5},
        )
        assert resp_create.status_code == 201, resp_create.text
        item_id = resp_create.json()["id"]

        resp = client.patch(
            f"/api/v1/inventario/{item_id}",
            json={"cantidad": 15, "ubicacion": "Sala A"},
        )
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["cantidad"] == 15
    assert body["ubicacion"] == "Sala A"
