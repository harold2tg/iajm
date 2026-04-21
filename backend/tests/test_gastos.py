import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.domains.gastos.models import CategoriaGasto, Gasto  # noqa: F401 — fuerza creación de tablas
from app.domains.usuarios.models import RolEnum
from app.main import app


def make_rol(rol: RolEnum) -> SimpleNamespace:
    return SimpleNamespace(rol=rol, grupo_id=None)


def make_user(rol: RolEnum) -> SimpleNamespace:
    """Crea un objeto usuario en memoria — NO instancia SQLAlchemy."""
    return SimpleNamespace(
        id=uuid.uuid4(),
        activo=True,
        roles=[make_rol(rol)],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_crear_categoria_como_admin(client):
    app.dependency_overrides[get_current_user] = lambda: make_user(RolEnum.administrador)
    try:
        resp = client.post("/api/v1/gastos/categorias", json={"nombre": "Servicios"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Servicios"
        assert "id" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_crear_categoria_sin_permiso(client):
    app.dependency_overrides[get_current_user] = lambda: make_user(RolEnum.observador)
    try:
        resp = client.post("/api/v1/gastos/categorias", json={"nombre": "Sin permiso"})
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def _crear_categoria(client, nombre: str = "Cat Test") -> str:
    app.dependency_overrides[get_current_user] = lambda: make_user(RolEnum.administrador)
    resp = client.post("/api/v1/gastos/categorias", json={"nombre": nombre})
    assert resp.status_code == 201
    return resp.json()["id"]


def _crear_gasto(client, categoria_id: str, fecha: str = "2025-04-01") -> dict:
    app.dependency_overrides[get_current_user] = lambda: make_user(RolEnum.asesor_tesoreria)
    resp = client.post(
        "/api/v1/gastos",
        json={
            "fecha": fecha,
            "descripcion": "Gasto de prueba",
            "cantidad": 3,
            "valor_unitario": 100.0,
            "categoria_id": categoria_id,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_crear_gasto_calcula_total(client):
    cat_id = _crear_categoria(client, "Alimentación")
    gasto = _crear_gasto(client, cat_id)
    assert gasto["valor_total"] == 300.0
    assert gasto["cantidad"] == 3
    assert gasto["valor_unitario"] == 100.0


def test_listar_gastos(client):
    cat_id = _crear_categoria(client, "Transporte")
    _crear_gasto(client, cat_id)

    app.dependency_overrides[get_current_user] = lambda: make_user(RolEnum.observador)
    resp = client.get("/api/v1/gastos")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


def test_listar_gastos_filtro_mes(client):
    cat_id = _crear_categoria(client, "Limpieza")
    _crear_gasto(client, cat_id, fecha="2025-04-15")

    app.dependency_overrides[get_current_user] = lambda: make_user(RolEnum.observador)
    # Filtro que SÍ debe retornar el gasto
    resp = client.get("/api/v1/gastos?mes=4&anio=2025")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["mes"] == 4

    # Filtro que NO debe retornar nada
    resp2 = client.get("/api/v1/gastos?mes=1&anio=2020")
    assert resp2.status_code == 200
    assert resp2.json() == []
