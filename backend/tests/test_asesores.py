from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domains.asesores.models import Asesor, AsesorGrupo, TipoAsesorEnum
from app.domains.grupos.models import Grupo, TipoGrupoEnum
from app.domains.usuarios.models import RolEnum, Usuario, UsuarioRol


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def crear_grupo_test(
    db: Session,
    nombre: str = "Grupo Test",
    tipo: TipoGrupoEnum = TipoGrupoEnum.infancia,
    edad_minima: int = 4,
    edad_maxima: int = 10,
) -> Grupo:
    grupo = Grupo(nombre=nombre, tipo=tipo, edad_minima=edad_minima, edad_maxima=edad_maxima)
    db.add(grupo)
    db.commit()
    db.refresh(grupo)
    return grupo


def crear_asesor_test(
    db: Session,
    nombre: str = "Asesor Test",
    telefono: str = "1234567890",
    tipo: TipoAsesorEnum = TipoAsesorEnum.base,
    usuario_id: uuid.UUID | None = None,
    activo: bool = True,
) -> Asesor:
    asesor = Asesor(
        nombre_completo=nombre,
        telefono=telefono,
        tipo=tipo,
        usuario_id=usuario_id,
        activo=activo,
    )
    db.add(asesor)
    db.commit()
    db.refresh(asesor)
    return asesor


def asignar_grupo_test(db: Session, asesor_id: uuid.UUID, grupo_id: uuid.UUID) -> AsesorGrupo:
    ag = AsesorGrupo(asesor_id=asesor_id, grupo_id=grupo_id)
    db.add(ag)
    db.commit()
    db.refresh(ag)
    return ag


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_crear_asesor_como_admin(client: TestClient, db: Session) -> None:
    """Admin puede crear un asesor → 201 con datos correctos."""
    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    resp = client.post(
        "/api/v1/asesores/",
        json={
            "nombre_completo": "Juan Pérez",
            "telefono": "1122334455",
            "tipo": "base",
            "grupo_ids": [],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["nombre_completo"] == "Juan Pérez"
    assert body["tipo"] == "base"
    assert body["activo"] is True
    assert body["grupos"] == []


def test_crear_asesor_sin_ser_admin(client: TestClient, db: Session) -> None:
    """Un observador no puede crear asesores → 403."""
    crear_usuario_test(db, "obs@test.com", "pass123", roles=[RolEnum.observador])
    token = get_token(client, "obs@test.com", "pass123")

    resp = client.post(
        "/api/v1/asesores/",
        json={
            "nombre_completo": "Intruso",
            "telefono": "000",
            "tipo": "auxiliar",
            "grupo_ids": [],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403, resp.text


def test_desactivar_unico_asesor_base_de_grupo(client: TestClient, db: Session) -> None:
    """RN-ASE-001: no se puede desactivar al único asesor base de un grupo → 409."""
    grupo = crear_grupo_test(db, nombre="Grupo Único")
    asesor = crear_asesor_test(db, nombre="Asesor Base Único", tipo=TipoAsesorEnum.base)
    asignar_grupo_test(db, asesor.id, grupo.id)

    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    resp = client.delete(
        f"/api/v1/asesores/{asesor.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409, resp.text


def test_remover_unico_asesor_base_de_grupo(client: TestClient, db: Session) -> None:
    """RN-ASE-001: no se puede remover al único asesor base de un grupo → 409."""
    grupo = crear_grupo_test(db, nombre="Grupo Protegido")
    asesor = crear_asesor_test(db, nombre="Asesor Base Solo", tipo=TipoAsesorEnum.base)
    asignar_grupo_test(db, asesor.id, grupo.id)

    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    resp = client.delete(
        f"/api/v1/asesores/{asesor.id}/grupos/{grupo.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409, resp.text


def test_generar_cuotas_mes(db: Session) -> None:
    """generar_cuotas_mes genera cuotas para asesores activos y no duplica."""
    from app.domains.asesores import service

    asesor1 = crear_asesor_test(db, nombre="Asesor A", activo=True)
    asesor2 = crear_asesor_test(db, nombre="Asesor B", activo=True)
    crear_asesor_test(db, nombre="Asesor Inactivo", activo=False)

    # Primera generación: debe crear 2 cuotas (solo activos)
    creadas = service.generar_cuotas_mes(db, mes=3, anio=2025, monto_default=5000.0)
    assert creadas == 2

    # Segunda generación mismo mes/año: no debe duplicar
    creadas_segunda = service.generar_cuotas_mes(db, mes=3, anio=2025, monto_default=5000.0)
    assert creadas_segunda == 0


def test_registrar_pago_cuota(client: TestClient, db: Session) -> None:
    """Admin puede registrar pago de cuota → estado queda 'pagado'."""
    from app.domains.asesores import service
    from app.domains.asesores.models import EstadoCuotaEnum

    asesor = crear_asesor_test(db, nombre="Asesor Pago")
    # Generar cuota directamente en DB
    service.generar_cuotas_mes(db, mes=4, anio=2025, monto_default=3000.0)

    from app.domains.asesores import repository as repo
    cuotas = repo.get_cuotas_asesor(db, asesor.id, mes=4, anio=2025)
    assert len(cuotas) == 1
    cuota = cuotas[0]
    assert cuota.estado == EstadoCuotaEnum.pendiente

    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    resp = client.patch(
        f"/api/v1/asesores/cuotas/{cuota.id}",
        json={"fecha_pago": "2025-04-15", "monto": "3000.00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["estado"] == "pagado"
    assert body["fecha_pago"] == "2025-04-15"


def test_asignar_grupo_inexistente(client: TestClient, db: Session) -> None:
    """Asignar asesor a grupo inexistente → 404."""
    asesor = crear_asesor_test(db, nombre="Asesor Sin Grupo")

    crear_usuario_test(db, "admin@test.com", "adminpass", roles=[RolEnum.administrador])
    token = get_token(client, "admin@test.com", "adminpass")

    grupo_fake_id = str(uuid.uuid4())
    resp = client.post(
        f"/api/v1/asesores/{asesor.id}/grupos",
        json={"grupo_id": grupo_fake_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404, resp.text


def test_me_asesor_vinculado(client: TestClient, db: Session) -> None:
    """GET /me retorna el asesor vinculado al usuario autenticado."""
    usuario = crear_usuario_test(db, "asesor@test.com", "pass123", roles=[RolEnum.observador])
    asesor = crear_asesor_test(db, nombre="Mi Asesor", usuario_id=usuario.id)

    token = get_token(client, "asesor@test.com", "pass123")

    resp = client.get(
        "/api/v1/asesores/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == str(asesor.id)
    assert body["nombre_completo"] == "Mi Asesor"
    assert body["usuario_id"] == str(usuario.id)
