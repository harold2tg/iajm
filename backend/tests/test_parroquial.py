from __future__ import annotations

from datetime import date

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


def test_crear_actividad_parroquial(client: TestClient, db: Session) -> None:
    """Admin puede crear actividad parroquial → 201."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp = client.post(
            "/api/v1/parroquial/actividades",
            json={
                "nombre": "Misa Aniversario",
                "fecha": "2025-10-15",
                "descripcion": "Misa por el 50 aniversario",
                "responsable": "Padre José",
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Misa Aniversario"
    assert body["responsable"] == "Padre José"
    assert body["entregado"] is False


def test_crear_actividad_sin_permiso(client: TestClient, db: Session) -> None:
    """Asesor_grupo no puede crear actividad parroquial → 403."""
    usuario = crear_usuario_test(db, "asesor@test.com", [RolEnum.asesor_grupo])
    set_auth(usuario)
    try:
        resp = client.post(
            "/api/v1/parroquial/actividades",
            json={"nombre": "Actividad no permitida", "fecha": "2025-11-01"},
        )
    finally:
        clear_auth()

    assert resp.status_code == 403, resp.text


def test_marcar_entrega(client: TestClient, db: Session) -> None:
    """Admin puede marcar entrega → entregado=True con monto y fecha."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp_create = client.post(
            "/api/v1/parroquial/actividades",
            json={"nombre": "Colecta Diciembre", "fecha": "2025-12-08"},
        )
        assert resp_create.status_code == 201, resp_create.text
        actividad_id = resp_create.json()["id"]

        resp = client.post(
            f"/api/v1/parroquial/actividades/{actividad_id}/entregar",
            json={"dinero_recolectado": 7500.0, "fecha_entrega": "2025-12-10"},
        )
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["entregado"] is True
    assert float(body["dinero_recolectado"]) == 7500.0
    assert body["fecha_entrega"] == "2025-12-10"


def test_listar_actividades(client: TestClient, db: Session) -> None:
    """GET /parroquial/actividades → 200 con lista."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp = client.get("/api/v1/parroquial/actividades")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)
