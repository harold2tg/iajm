from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import hash_password
from app.domains.inventario.models import ItemInventario  # noqa: F401 — fuerza registro en metadata
from app.domains.usuarios.models import RolEnum, Usuario, UsuarioRol
from app.main import app


# ── Helpers ───────────────────────────────────────────────────────────────────

def crear_usuario_test(
    db: Session,
    email: str,
    password: str,
    roles: list[RolEnum] | None = None,
) -> Usuario:
    usuario = Usuario(
        nombre_completo="Test User",
        email=email,
        password_hash=hash_password(password),
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    for rol in (roles or []):
        usuario_rol = UsuarioRol(usuario_id=usuario.id, rol=rol, grupo_id=None)
        db.add(usuario_rol)
    db.commit()
    db.refresh(usuario)
    return usuario


def auth_headers(client: TestClient, usuario: Usuario) -> dict[str, str]:
    """Override get_current_user para evitar el login y el flush problemático."""
    app.dependency_overrides[get_current_user] = lambda: usuario
    return {}


def clear_auth() -> None:
    app.dependency_overrides.pop(get_current_user, None)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_crear_actividad_como_admin(client: TestClient, db: Session) -> None:
    """Admin puede crear actividad pro-fondos → 201."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/actividades",
            json={
                "nombre": "Rifa Navideña",
                "tipo": "rifa",
                "fecha": "2025-12-01",
                "responsable": "Ana García",
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Rifa Navideña"
    assert body["responsable"] == "Ana García"
    assert "id" in body


def test_crear_actividad_sin_permiso(client: TestClient, db: Session) -> None:
    """Observador no puede crear actividad → 403."""
    obs = crear_usuario_test(db, "obs@test.com", "pass123", roles=[RolEnum.observador])
    auth_headers(client, obs)

    try:
        resp = client.post(
            "/api/v1/tesoreria/actividades",
            json={
                "nombre": "Actividad Intruso",
                "tipo": "venta",
                "fecha": "2025-06-15",
                "responsable": "Nadie",
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 403, resp.text


def test_agregar_producto_a_actividad(client: TestClient, db: Session) -> None:
    """Admin puede agregar producto a una actividad → 201."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        # Crear actividad primero
        resp_act = client.post(
            "/api/v1/tesoreria/actividades",
            json={
                "nombre": "Venta de Empanadas",
                "tipo": "venta_comida",
                "fecha": "2025-09-10",
                "responsable": "Luis Pérez",
            },
        )
        assert resp_act.status_code == 201, resp_act.text
        actividad_id = resp_act.json()["id"]

        resp = client.post(
            f"/api/v1/tesoreria/actividades/{actividad_id}/productos",
            json={
                "nombre": "Empanada de carne",
                "cantidad": 50,
                "costo_unitario": 200.0,
                "precio_venta": 400.0,
                "es_donado": False,
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre"] == "Empanada de carne"
    assert body["cantidad"] == 50
    assert body["actividad_id"] == actividad_id


def test_registrar_donacion_efectivo(client: TestClient, db: Session) -> None:
    """Admin registra donación en efectivo → 201 con tipo correcto."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "efectivo",
                "donante": "Juan Benefactor",
                "fecha": "2025-08-20",
                "valor": 5000.0,
                "descripcion": "Donación para campamento",
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["tipo"] == "efectivo"
    assert body["donante"] == "Juan Benefactor"
    assert float(body["valor"]) == 5000.0


def test_registrar_otro_ingreso(client: TestClient, db: Session) -> None:
    """Admin registra otro ingreso → 201."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/otros-ingresos",
            json={
                "descripcion": "Subsidio parroquial",
                "valor": 10000.0,
                "fecha": "2025-07-01",
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["descripcion"] == "Subsidio parroquial"
    assert float(body["valor"]) == 10000.0


def test_resumen_tesoreria(client: TestClient, db: Session) -> None:
    """GET /tesoreria/resumen responde 200 con total_ingresos."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.get("/api/v1/tesoreria/resumen?mes=7&anio=2025")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "total_ingresos" in body
    assert "total_gastos" in body
    assert "balance" in body
    assert isinstance(body["total_ingresos"], (int, float))


# ── G02 — RN-TES-002: Validación XOR efectivo/especie ────────────────────────

def test_donacion_efectivo_no_acepta_campos_especie(client: TestClient, db: Session) -> None:
    """G02: Efectivo con cantidad_especie → 422."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "efectivo",
                "fecha": "2025-08-20",
                "valor": 5000.0,
                "cantidad_especie": 10,  # inválido para efectivo
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 422, resp.text
    assert "especie" in resp.json()["detail"].lower()


def test_donacion_efectivo_no_acepta_valor_estimado(client: TestClient, db: Session) -> None:
    """G02: Efectivo con valor_estimado → 422."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "efectivo",
                "fecha": "2025-08-20",
                "valor": 5000.0,
                "valor_estimado": 1000.0,  # inválido para efectivo
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 422, resp.text


def test_donacion_especie_no_acepta_valor_monetario(client: TestClient, db: Session) -> None:
    """G02: Especie con campo 'valor' (monetario) → 422."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "especie",
                "fecha": "2025-08-20",
                "valor": 5000.0,  # inválido para especie
                "descripcion": "Sillas de plástico",
                "cantidad_especie": 5,
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 422, resp.text
    assert "valor" in resp.json()["detail"].lower()


def test_donacion_no_puede_tener_actividad_y_ser_general(client: TestClient, db: Session) -> None:
    """G02: actividad_id + es_general=True → 422."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    # Crear actividad primero
    resp_act = client.post(
        "/api/v1/tesoreria/actividades",
        json={"nombre": "Kermesse", "tipo": "venta", "fecha": "2025-09-01", "responsable": "Pedro"},
    )
    actividad_id = resp_act.json()["id"]

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "efectivo",
                "fecha": "2025-08-20",
                "valor": 3000.0,
                "actividad_id": actividad_id,
                "es_general": True,  # inválido: no puede ser ambos
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 422, resp.text
    assert "general" in resp.json()["detail"].lower() or "actividad" in resp.json()["detail"].lower()


# ── G03 — RN-TES-003: Donación especie crea item en inventario ────────────────

def test_donacion_especie_crea_item_inventario(client: TestClient, db: Session) -> None:
    """G03: Donación en especie debe crear un ItemInventario automáticamente."""
    from app.domains.inventario.models import ItemInventario

    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "especie",
                "donante": "Parroquia San José",
                "fecha": "2025-08-25",
                "descripcion": "Sillas plegables",
                "cantidad_especie": 20,
                "valor_estimado": 15000.0,
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["tipo"] == "especie"

    # Verificar que se creó el item en inventario y está vinculado
    item_id = body.get("item_inventario_id")
    assert item_id is not None, "La donación en especie debe tener item_inventario_id"

    item = db.get(ItemInventario, uuid.UUID(item_id))
    assert item is not None, "El ItemInventario debe existir en la DB"
    assert item.nombre == "Sillas plegables"
    assert item.cantidad == 20
    assert item.origen.value == "donacion"
    assert item.estado.value == "bueno"


def test_donacion_especie_sin_descripcion_usa_default(client: TestClient, db: Session) -> None:
    """G03: Donación especie sin descripcion usa nombre por defecto en el item."""
    from app.domains.inventario.models import ItemInventario

    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        resp = client.post(
            "/api/v1/tesoreria/donaciones",
            json={
                "tipo": "especie",
                "fecha": "2025-08-25",
                "cantidad_especie": 3,
            },
        )
    finally:
        clear_auth()

    assert resp.status_code == 201, resp.text
    item_id = resp.json().get("item_inventario_id")
    assert item_id is not None

    item = db.get(ItemInventario, uuid.UUID(item_id))
    assert item is not None
    assert "sin descripción" in item.nombre.lower() or item.nombre != ""


# ── G04 — RN-TES-001: Utilidad calculada en actividad pro-fondos ──────────────

def test_actividad_response_incluye_utilidad(client: TestClient, db: Session) -> None:
    """G04: Actividad en respuesta incluye total_ingresos, total_costos, utilidad."""
    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    try:
        # Crear actividad
        resp_act = client.post(
            "/api/v1/tesoreria/actividades",
            json={"nombre": "Venta de tortas", "tipo": "venta", "fecha": "2025-10-15", "responsable": "María"},
        )
        assert resp_act.status_code == 201, resp_act.text
        actividad_id = resp_act.json()["id"]

        # Agregar producto comprado (tiene costo)
        client.post(
            f"/api/v1/tesoreria/actividades/{actividad_id}/productos",
            json={"nombre": "Torta de chocolate", "cantidad": 10, "costo_unitario": 500.0, "precio_venta": 1000.0, "es_donado": False},
        )
        # Agregar producto donado (sin costo)
        client.post(
            f"/api/v1/tesoreria/actividades/{actividad_id}/productos",
            json={"nombre": "Alfajores donados", "cantidad": 20, "precio_venta": 200.0, "es_donado": True},
        )

        resp = client.get(f"/api/v1/tesoreria/actividades/{actividad_id}")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()

    # total_ingresos = (10 * 1000) + (20 * 200) = 10000 + 4000 = 14000
    assert float(body["total_ingresos"]) == 14000.0
    # total_costos = solo no donados: 10 * 500 = 5000
    assert float(body["total_costos"]) == 5000.0
    # utilidad = 14000 - 5000 = 9000
    assert float(body["utilidad"]) == 9000.0


# ── G05 — Ventas de tienda incluidas en el balance ───────────────────────────

def test_resumen_incluye_ventas_tienda(client: TestClient, db: Session) -> None:
    """G05: El resumen suma ventas de tienda al total_ingresos."""
    from app.domains.tienda.models import VentaDia
    from datetime import date as d

    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    # Crear una VentaDia directamente en la DB para el mes 8/2025
    venta = VentaDia(
        fecha=d(2025, 8, 15),
        total_calculado=7500.0,
        registrado_por=None,
    )
    db.add(venta)
    db.commit()

    try:
        resp = client.get("/api/v1/tesoreria/resumen?mes=8&anio=2025")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    body = resp.json()
    # El total_ingresos debe incluir los 7500 de la venta de tienda
    assert float(body["total_ingresos"]) >= 7500.0


def test_resumen_no_incluye_ventas_otro_mes(client: TestClient, db: Session) -> None:
    """G05: El resumen no suma ventas de tienda de otro mes."""
    from app.domains.tienda.models import VentaDia
    from datetime import date as d

    admin = crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    auth_headers(client, admin)

    # Venta en septiembre, pero consulta agosto
    venta = VentaDia(
        fecha=d(2025, 9, 1),
        total_calculado=7500.0,
        registrado_por=None,
    )
    db.add(venta)
    db.commit()

    try:
        resp = client.get("/api/v1/tesoreria/resumen?mes=8&anio=2025")
    finally:
        clear_auth()

    assert resp.status_code == 200, resp.text
    # Agosto no tiene ventas de tienda → total_ingresos no debe incluir esos 7500
    assert float(resp.json()["total_ingresos"]) == 0.0
