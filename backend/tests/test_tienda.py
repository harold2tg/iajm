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


def test_registrar_venta_calcula_totales(client: TestClient, db: Session) -> None:
    """Admin registra venta → total_calculado y subtotales son correctos."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp = client.post(
            "/api/v1/tienda/ventas",
            json={
                "fecha": str(date.today()),
                "detalles": [
                    {"producto": "Remera", "cantidad": 2, "precio_unitario": 500.0},
                    {"producto": "Gorra", "cantidad": 1, "precio_unitario": 300.0},
                ],
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert float(body["total_calculado"]) == 1300.0
    subtotales = {d["producto"]: float(d["subtotal"]) for d in body["detalles"]}
    assert subtotales["Remera"] == 1000.0
    assert subtotales["Gorra"] == 300.0


def test_registrar_venta_sin_permiso(client: TestClient, db: Session) -> None:
    """asesor_grupo no puede registrar venta → 403."""
    usuario = crear_usuario_test(db, "asesor@test.com", [RolEnum.asesor_grupo])
    set_auth(usuario)
    try:
        resp = client.post(
            "/api/v1/tienda/ventas",
            json={
                "fecha": str(date.today()),
                "detalles": [{"producto": "Algo", "cantidad": 1, "precio_unitario": 100.0}],
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 403, resp.text


def test_listar_ventas(client: TestClient, db: Session) -> None:
    """GET /tienda/ventas → 200 con lista."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp = client.get("/api/v1/tienda/ventas")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_get_venta_por_id(client: TestClient, db: Session) -> None:
    """GET /tienda/ventas/{id} → 200 con datos correctos."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp_create = client.post(
            "/api/v1/tienda/ventas",
            json={
                "fecha": str(date.today()),
                "observaciones": "Nota test",
                "detalles": [{"producto": "Libro", "cantidad": 3, "precio_unitario": 200.0}],
            },
        )
        assert resp_create.status_code == 201, resp_create.text
        venta_id = resp_create.json()["id"]

        resp = client.get(f"/api/v1/tienda/ventas/{venta_id}")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == venta_id
    assert body["observaciones"] == "Nota test"
    assert float(body["total_calculado"]) == 600.0


def test_cerrar_venta_abierta(client: TestClient, db: Session) -> None:
    """RN-TIE-003: Cerrar venta abierta → 200, estado=cerrado, ingreso creado en tesorería."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        # Crear venta primero
        resp_create = client.post(
            "/api/v1/tienda/ventas",
            json={
                "fecha": str(date.today()),
                "detalles": [
                    {"producto": "Remera", "cantidad": 2, "precio_unitario": 500.0},
                    {"producto": "Gorra", "cantidad": 1, "precio_unitario": 300.0},
                ],
            },
        )
        assert resp_create.status_code == 201, resp_create.text
        venta_id = resp_create.json()["id"]

        # Cerrar la venta
        resp = client.post(f"/api/v1/tienda/ventas/{venta_id}/cerrar")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["estado"] == "cerrado"
    assert float(body["total_calculado"]) == 1300.0
    assert "ingreso_id" in body
    assert body["ingreso_id"] is not None


def test_cerrar_venta_ya_cerrada(client: TestClient, db: Session) -> None:
    """RN-TIE-003: Intentar cerrar una venta ya cerrada → 400."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp_create = client.post(
            "/api/v1/tienda/ventas",
            json={
                "fecha": str(date.today()),
                "detalles": [{"producto": "Libro", "cantidad": 1, "precio_unitario": 100.0}],
            },
        )
        assert resp_create.status_code == 201, resp_create.text
        venta_id = resp_create.json()["id"]

        # Primer cierre — debe funcionar
        resp_primer_cierre = client.post(f"/api/v1/tienda/ventas/{venta_id}/cerrar")
        assert resp_primer_cierre.status_code == 200, resp_primer_cierre.text

        # Segundo cierre — debe fallar con 400
        resp = client.post(f"/api/v1/tienda/ventas/{venta_id}/cerrar")
    finally:
        clear_auth()

    assert resp.status_code == 400, resp.text
    assert "cerrada" in resp.json()["detail"].lower()


def test_cerrar_venta_total_calculado_correcto(client: TestClient, db: Session) -> None:
    """RN-TIE-003: total_calculado al cerrar = suma real de detalles."""
    admin = crear_usuario_test(db, "admin@test.com", [RolEnum.administrador])
    set_auth(admin)
    try:
        resp_create = client.post(
            "/api/v1/tienda/ventas",
            json={
                "fecha": str(date.today()),
                "detalles": [
                    {"producto": "Item A", "cantidad": 3, "precio_unitario": 150.0},
                    {"producto": "Item B", "cantidad": 2, "precio_unitario": 75.0},
                    {"producto": "Item C", "cantidad": 1, "precio_unitario": 50.0},
                ],
            },
        )
        assert resp_create.status_code == 201, resp_create.text
        venta_id = resp_create.json()["id"]

        resp = client.post(f"/api/v1/tienda/ventas/{venta_id}/cerrar")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    # 3*150 + 2*75 + 1*50 = 450 + 150 + 50 = 650
    assert float(body["total_calculado"]) == 650.0
    assert body["estado"] == "cerrado"
