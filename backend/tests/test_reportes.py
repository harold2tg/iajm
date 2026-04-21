from __future__ import annotations

import uuid
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.domains.usuarios.models import RolEnum
from app.main import app

# Importar modelos para forzar creación de tablas en SQLite de tests
from app.domains.gastos.models import Gasto, CategoriaGasto  # noqa: F401
from app.domains.tesoreria.models import OtroIngreso, Donacion, ActividadProFondos, ProductoActividad  # noqa: F401
from app.domains.inventario.models import ItemInventario  # noqa: F401
from app.domains.tienda.models import VentaDia, DetalleVentaDia  # noqa: F401
from app.domains.encuentros.models import Encuentro, AsistenciaEncuentro  # noqa: F401
from app.domains.asesores.models import Asesor, CuotaAsesor, AsesorGrupo  # noqa: F401
from app.domains.miembros.models import Miembro  # noqa: F401
from app.domains.grupos.models import Grupo  # noqa: F401
from app.domains.usuarios.models import Usuario, UsuarioRol  # noqa: F401


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_rol(rol: RolEnum, grupo_id=None) -> SimpleNamespace:
    return SimpleNamespace(rol=rol, grupo_id=grupo_id)


def make_user(rol: RolEnum, grupo_id=None) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        activo=True,
        roles=[make_rol(rol, grupo_id)],
    )


def override_user(rol: RolEnum, grupo_id=None):
    u = make_user(rol, grupo_id)
    app.dependency_overrides[get_current_user] = lambda: u
    app.dependency_overrides[require_admin] = lambda: u if rol == RolEnum.administrador else None
    return u


def clear_overrides():
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)


# ── R01 Balance ───────────────────────────────────────────────────────────────

def test_balance_retorna_estructura(client: TestClient, db: Session):
    """R01: balance retorna estructura esperada con saldo correcto."""
    override_user(RolEnum.administrador)
    try:
        # Crear un OtroIngreso para el período
        ingreso = OtroIngreso(
            descripcion="Ingreso test",
            valor=500.0,
            fecha=date(2025, 4, 10),
        )
        db.add(ingreso)
        db.commit()

        resp = client.get("/api/v1/reportes/balance?mes=4&anio=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_ingresos" in data
        assert "total_gastos" in data
        assert "saldo" in data
        assert "detalle_ingresos" in data
        assert "detalle_gastos" in data
        assert data["saldo"] == data["total_ingresos"] - data["total_gastos"]
        assert data["total_ingresos"] >= 500.0
    finally:
        clear_overrides()


def test_balance_csv(client: TestClient, db: Session):
    """R01: balance con formato=csv retorna texto CSV."""
    override_user(RolEnum.asesor_tesoreria)
    try:
        resp = client.get("/api/v1/reportes/balance?mes=1&anio=2025&formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


def test_balance_acceso_denegado_sin_rol(client: TestClient):
    """R01: observador puede ver balance, asesor_grupo no."""
    override_user(RolEnum.asesor_grupo)
    try:
        resp = client.get("/api/v1/reportes/balance?mes=4&anio=2025")
        assert resp.status_code == 403
    finally:
        clear_overrides()


# ── R02 Actividad Pro-Fondos ──────────────────────────────────────────────────

def test_reporte_actividad_not_found(client: TestClient, db: Session):
    """R02: actividad inexistente retorna 404."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get(f"/api/v1/reportes/actividades/{uuid.uuid4()}")
        assert resp.status_code == 404
    finally:
        clear_overrides()


def test_reporte_actividad_con_productos(client: TestClient, db: Session):
    """R02: actividad con productos retorna utilidad calculada."""
    override_user(RolEnum.administrador)
    try:
        act = ActividadProFondos(
            nombre="Rifa test",
            tipo="rifa",
            fecha=date(2025, 4, 1),
            responsable="Juan",
        )
        db.add(act)
        db.commit()
        db.refresh(act)

        prod = ProductoActividad(
            actividad_id=act.id,
            nombre="Boleto",
            cantidad=10,
            costo_unitario=5.0,
            precio_venta=20.0,
            es_donado=False,
        )
        db.add(prod)
        db.commit()

        resp = client.get(f"/api/v1/reportes/actividades/{act.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_ingresos"] == 200.0  # 10 * 20
        assert data["total_costos"] == 50.0     # 10 * 5
        assert data["utilidad"] == 150.0
    finally:
        clear_overrides()


# ── R03 Donaciones ────────────────────────────────────────────────────────────

def test_reporte_donaciones_estructura(client: TestClient, db: Session):
    """R03: donaciones retorna estructura esperada."""
    override_user(RolEnum.asesor_tesoreria)
    try:
        donacion = Donacion(
            tipo="efectivo",
            donante="Pedro",
            fecha=date(2025, 4, 5),
            valor=1000.0,
        )
        db.add(donacion)
        db.commit()

        resp = client.get("/api/v1/reportes/donaciones?mes=4&anio=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_efectivo" in data
        assert "total_especie" in data
        assert "donaciones" in data
        assert data["total_efectivo"] >= 1000.0
    finally:
        clear_overrides()


def test_reporte_donaciones_csv(client: TestClient, db: Session):
    """R03: donaciones con formato=csv retorna CSV."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/donaciones?formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


# ── R04 Inventario ────────────────────────────────────────────────────────────

def test_reporte_inventario_estructura(client: TestClient, db: Session):
    """R04: inventario retorna estructura completa."""
    override_user(RolEnum.asesor_tienda)
    try:
        item = ItemInventario(
            nombre="Biblia test",
            cantidad=5,
            tipo="formativo",
            origen="compra",
        )
        db.add(item)
        db.commit()

        resp = client.get("/api/v1/reportes/inventario")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_items" in data
        assert "por_tipo" in data
        assert "por_origen" in data
        assert "items" in data
        assert data["total_items"] >= 5
    finally:
        clear_overrides()


def test_reporte_inventario_csv(client: TestClient, db: Session):
    """R04: inventario con formato=csv retorna CSV."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/inventario?formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


# ── R05 Asistencia ────────────────────────────────────────────────────────────

def test_reporte_asistencia_vacio(client: TestClient, db: Session):
    """R05: asistencia sin datos retorna lista vacía."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/asistencia")
        assert resp.status_code == 200
        data = resp.json()
        assert "miembros" in data
        assert isinstance(data["miembros"], list)
    finally:
        clear_overrides()


def test_reporte_asistencia_csv(client: TestClient, db: Session):
    """R05: asistencia con formato=csv retorna CSV."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/asistencia?formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


# ── R06 Encuentros ────────────────────────────────────────────────────────────

def test_reporte_encuentros_estructura(client: TestClient, db: Session):
    """R06: encuentros retorna lista."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/encuentros")
        assert resp.status_code == 200
        data = resp.json()
        assert "encuentros" in data
        assert isinstance(data["encuentros"], list)
    finally:
        clear_overrides()


def test_reporte_encuentros_csv(client: TestClient, db: Session):
    """R06: encuentros con formato=csv retorna CSV."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/encuentros?formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


# ── R07 Tienda ────────────────────────────────────────────────────────────────

def test_reporte_tienda_estructura(client: TestClient, db: Session):
    """R07: tienda retorna estructura con acumulado."""
    override_user(RolEnum.asesor_tienda)
    try:
        # Crear una venta cerrada
        venta = VentaDia(
            fecha=date(2025, 4, 10),
            total_calculado=300.0,
            estado="cerrado",
        )
        db.add(venta)
        db.commit()

        resp = client.get("/api/v1/reportes/tienda?mes=4&anio=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_mes" in data
        assert "ventas_por_dia" in data
        assert "acumulado_historico" in data
        assert data["total_mes"] >= 300.0
    finally:
        clear_overrides()


def test_reporte_tienda_csv(client: TestClient, db: Session):
    """R07: tienda con formato=csv retorna CSV."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/tienda?formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


# ── R08 Cuotas ────────────────────────────────────────────────────────────────

def test_reporte_cuotas_estructura(client: TestClient, db: Session):
    """R08: cuotas retorna lista de asesores con estado."""
    override_user(RolEnum.asesor_tesoreria)
    try:
        # Crear asesor y cuota
        asesor = Asesor(
            nombre_completo="Asesor Test",
            telefono="1234567890",
            tipo="base",
            activo=True,
        )
        db.add(asesor)
        db.commit()
        db.refresh(asesor)

        cuota = CuotaAsesor(
            asesor_id=asesor.id,
            mes=4,
            anio=2025,
            monto=50.0,
            estado="pendiente",
        )
        db.add(cuota)
        db.commit()

        resp = client.get("/api/v1/reportes/cuotas?mes=4&anio=2025")
        assert resp.status_code == 200
        data = resp.json()
        assert "cuotas" in data
        assert data["mes"] == 4
        assert data["anio"] == 2025
        assert len(data["cuotas"]) >= 1
        cuota_item = data["cuotas"][0]
        assert "asesor_id" in cuota_item
        assert "estado" in cuota_item
        assert cuota_item["estado"] in ("pagado", "pendiente")
    finally:
        clear_overrides()


def test_reporte_cuotas_csv(client: TestClient, db: Session):
    """R08: cuotas con formato=csv retorna CSV."""
    override_user(RolEnum.administrador)
    try:
        resp = client.get("/api/v1/reportes/cuotas?mes=4&anio=2025&formato=csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
    finally:
        clear_overrides()


# ── R09 Usuarios ─────────────────────────────────────────────────────────────

def test_reporte_usuarios_solo_admin(client: TestClient, db: Session):
    """R09: solo admin puede ver el reporte de usuarios."""
    # Observador no puede
    u_obs = make_user(RolEnum.observador)
    app.dependency_overrides[get_current_user] = lambda: u_obs
    app.dependency_overrides[require_admin] = lambda: (_ for _ in ()).throw(
        __import__("fastapi").HTTPException(status_code=403, detail="Solo admin")
    )
    try:
        resp = client.get("/api/v1/reportes/usuarios")
        assert resp.status_code == 403
    finally:
        clear_overrides()


def test_reporte_usuarios_admin_ok(client: TestClient, db: Session):
    """R09: admin puede ver reporte de usuarios."""
    u_admin = make_user(RolEnum.administrador)
    app.dependency_overrides[get_current_user] = lambda: u_admin
    app.dependency_overrides[require_admin] = lambda: u_admin
    try:
        resp = client.get("/api/v1/reportes/usuarios")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_activos" in data
        assert "usuarios" in data
        assert isinstance(data["usuarios"], list)
    finally:
        clear_overrides()
