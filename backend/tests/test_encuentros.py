from __future__ import annotations

import uuid
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.domains.encuentros.schemas import AsistenciaCreate, EncuentroCreate
from app.domains.encuentros.models import EstadoAsistenciaEnum, EstadoEncuentroEnum
from app.domains.encuentros import service
from app.domains.usuarios.models import RolEnum


def make_actor(*roles: RolEnum, grupo_id: uuid.UUID | None = None):
    actor = MagicMock()
    actor.id = uuid.uuid4()
    mock_roles = []
    for rol in roles:
        r = MagicMock()
        r.rol = rol
        r.grupo_id = grupo_id
        mock_roles.append(r)
    actor.roles = mock_roles
    return actor


def make_encuentro(
    grupo_id: uuid.UUID | None = None,
    estado: EstadoEncuentroEnum = EstadoEncuentroEnum.abierto,
) -> MagicMock:
    enc = MagicMock()
    enc.id = uuid.uuid4()
    enc.grupo_id = grupo_id or uuid.uuid4()
    enc.estado = estado
    enc.fecha = date.today()
    enc.creado_por = uuid.uuid4()
    enc.tema = None
    enc.observaciones = None
    enc.cerrado_en = None
    return enc


def make_miembro(grupo_id: uuid.UUID, nombre: str = "Test Miembro") -> MagicMock:
    m = MagicMock()
    m.id = uuid.uuid4()
    m.grupo_id = grupo_id
    m.nombre_completo = nombre
    m.activo = True
    m.fecha_ingreso = date.today() - timedelta(days=365)
    return m


# ─── Test 1: crear encuentro como asesor de grupo ─────────────────────────────

def test_crear_encuentro_como_asesor_de_grupo():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.asesor_grupo, grupo_id=grupo_id)
    grupos_actor = [grupo_id]

    data = EncuentroCreate(grupo_id=grupo_id, fecha=date.today())
    encuentro_mock = make_encuentro(grupo_id=grupo_id)

    with patch("app.domains.encuentros.service.get_grupo_or_404"), \
         patch("app.domains.encuentros.service.repository.get_by_grupo_y_fecha", return_value=None), \
         patch("app.domains.encuentros.service.repository.create", return_value=encuentro_mock), \
         patch("app.domains.encuentros.service.get_miembros_by_grupo", return_value=[]), \
         patch("app.domains.encuentros.service.repository.create_asistencia"):
        result = service.crear_encuentro(db, data, actor, grupos_actor)

    assert result is not None
    assert result.grupo_id == grupo_id


# ─── Test 2: encuentro duplicado mismo grupo+fecha → 409 ─────────────────────

def test_crear_encuentro_duplicado_mismo_grupo_fecha():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.administrador)
    grupos_actor: list[uuid.UUID] = []

    data = EncuentroCreate(grupo_id=grupo_id, fecha=date.today())
    existente = make_encuentro(grupo_id=grupo_id)

    with patch("app.domains.encuentros.service.get_grupo_or_404"), \
         patch("app.domains.encuentros.service.repository.get_by_grupo_y_fecha", return_value=existente):
        with pytest.raises(HTTPException) as exc_info:
            service.crear_encuentro(db, data, actor, grupos_actor)

    assert exc_info.value.status_code == 409


# ─── Test 3: asesor no puede crear encuentro en otro grupo → 403 ──────────────

def test_asesor_no_puede_crear_encuentro_en_otro_grupo():
    db = MagicMock()
    grupo_propio = uuid.uuid4()
    grupo_ajeno = uuid.uuid4()
    actor = make_actor(RolEnum.asesor_grupo, grupo_id=grupo_propio)
    grupos_actor = [grupo_propio]

    data = EncuentroCreate(grupo_id=grupo_ajeno, fecha=date.today())

    with pytest.raises(HTTPException) as exc_info:
        service.crear_encuentro(db, data, actor, grupos_actor)

    assert exc_info.value.status_code == 403


# ─── Test 4: registrar asistencia en encuentro abierto → 200 ─────────────────

def test_registrar_asistencia_en_encuentro_abierto():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.asesor_grupo, grupo_id=grupo_id)
    grupos_actor = [grupo_id]

    encuentro = make_encuentro(grupo_id=grupo_id, estado=EstadoEncuentroEnum.abierto)
    miembro_id = uuid.uuid4()
    asistencia_mock = MagicMock()

    with patch("app.domains.encuentros.service.repository.get_by_id", return_value=encuentro), \
         patch("app.domains.encuentros.service.repository.get_asistencia", return_value=None), \
         patch("app.domains.encuentros.service.repository.create_asistencia", return_value=asistencia_mock):
        result = service.registrar_asistencia(
            db, encuentro.id, miembro_id, EstadoAsistenciaEnum.asistio, actor, grupos_actor
        )

    assert result is not None


# ─── Test 5: registrar asistencia en encuentro cerrado → 409 ─────────────────

def test_registrar_asistencia_en_encuentro_cerrado():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.asesor_grupo, grupo_id=grupo_id)
    grupos_actor = [grupo_id]

    encuentro = make_encuentro(grupo_id=grupo_id, estado=EstadoEncuentroEnum.cerrado)
    miembro_id = uuid.uuid4()

    with patch("app.domains.encuentros.service.repository.get_by_id", return_value=encuentro):
        with pytest.raises(HTTPException) as exc_info:
            service.registrar_asistencia(
                db, encuentro.id, miembro_id, EstadoAsistenciaEnum.asistio, actor, grupos_actor
            )

    assert exc_info.value.status_code == 409


# ─── Test 6: cerrar encuentro con advertencia ─────────────────────────────────

def test_cerrar_encuentro_con_advertencia():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.administrador)
    grupos_actor: list[uuid.UUID] = []

    encuentro = make_encuentro(grupo_id=grupo_id, estado=EstadoEncuentroEnum.abierto)
    miembro1 = make_miembro(grupo_id, "Pedro Pérez")
    miembro2 = make_miembro(grupo_id, "Ana García")

    # Solo miembro2 tiene asistencia registrada
    asistencia_mock = MagicMock()
    asistencia_mock.miembro_id = miembro2.id

    with patch("app.domains.encuentros.service.repository.get_by_id", return_value=encuentro), \
         patch("app.domains.encuentros.service.get_miembros_by_grupo", return_value=[miembro1, miembro2]), \
         patch("app.domains.encuentros.service.repository.get_asistencias_encuentro", return_value=[asistencia_mock]), \
         patch("app.domains.encuentros.service.repository.update", return_value=encuentro), \
         patch("app.domains.encuentros.service._build_encuentro_response") as mock_build:
        mock_build.return_value = MagicMock()
        result = service.cerrar_encuentro(db, encuentro.id, actor, grupos_actor)

    assert result.advertencia is not None
    assert "Pedro Pérez" in result.advertencia


# ─── Test 7: cerrar encuentro completo sin advertencia ───────────────────────

def test_cerrar_encuentro_completo_sin_advertencia():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.administrador)
    grupos_actor: list[uuid.UUID] = []

    encuentro = make_encuentro(grupo_id=grupo_id, estado=EstadoEncuentroEnum.abierto)
    miembro1 = make_miembro(grupo_id, "Pedro Pérez")

    asistencia_mock = MagicMock()
    asistencia_mock.miembro_id = miembro1.id

    with patch("app.domains.encuentros.service.repository.get_by_id", return_value=encuentro), \
         patch("app.domains.encuentros.service.get_miembros_by_grupo", return_value=[miembro1]), \
         patch("app.domains.encuentros.service.repository.get_asistencias_encuentro", return_value=[asistencia_mock]), \
         patch("app.domains.encuentros.service.repository.update", return_value=encuentro), \
         patch("app.domains.encuentros.service._build_encuentro_response") as mock_build:
        mock_build.return_value = MagicMock()
        result = service.cerrar_encuentro(db, encuentro.id, actor, grupos_actor)

    assert result.advertencia is None


# ─── Test 8: reabrir encuentro como admin → log persiste en DB ───────────────

def test_reabrir_encuentro_como_admin():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    encuentro = make_encuentro(estado=EstadoEncuentroEnum.cerrado)
    log_mock = MagicMock()

    with patch("app.domains.encuentros.service.repository.get_by_id", return_value=encuentro), \
         patch("app.domains.encuentros.service.repository.update", return_value=encuentro), \
         patch("app.domains.encuentros.service.repository.create_log_reapertura", return_value=log_mock) as mock_log:
        result = service.reabrir_encuentro(db, encuentro.id, "Corrección de datos", actor)

    assert result is not None
    mock_log.assert_called_once_with(
        db,
        encuentro_id=encuentro.id,
        reabierto_por=actor.id,
        motivo="Corrección de datos",
    )


# ─── Test 9: reabrir encuentro como asesor → 403 ─────────────────────────────

def test_reabrir_encuentro_como_asesor():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.asesor_grupo, grupo_id=grupo_id)
    encuentro = make_encuentro(grupo_id=grupo_id, estado=EstadoEncuentroEnum.cerrado)

    with pytest.raises(HTTPException) as exc_info:
        service.reabrir_encuentro(db, encuentro.id, "quiero reabrir", actor)

    assert exc_info.value.status_code == 403


# ─── Test 11: reabrir encuentro ya abierto → 400 ─────────────────────────────

def test_reabrir_encuentro_ya_abierto():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    encuentro = make_encuentro(estado=EstadoEncuentroEnum.abierto)

    with patch("app.domains.encuentros.service.repository.get_by_id", return_value=encuentro):
        with pytest.raises(HTTPException) as exc_info:
            service.reabrir_encuentro(db, encuentro.id, "ya está abierto", actor)

    assert exc_info.value.status_code == 400


# ─── Test 10: pre-población asistencia al crear ───────────────────────────────

def test_pre_poblacion_asistencia_al_crear():
    db = MagicMock()
    grupo_id = uuid.uuid4()
    actor = make_actor(RolEnum.administrador)
    grupos_actor: list[uuid.UUID] = []

    data = EncuentroCreate(grupo_id=grupo_id, fecha=date.today())
    encuentro_mock = make_encuentro(grupo_id=grupo_id)

    miembro1 = make_miembro(grupo_id, "Ana")
    miembro2 = make_miembro(grupo_id, "Luis")
    miembro3 = make_miembro(grupo_id, "Marta")

    asistencias_creadas: list[dict] = []

    def fake_create_asistencia(db, **kwargs):
        asistencias_creadas.append(kwargs)
        return MagicMock()

    with patch("app.domains.encuentros.service.get_grupo_or_404"), \
         patch("app.domains.encuentros.service.repository.get_by_grupo_y_fecha", return_value=None), \
         patch("app.domains.encuentros.service.repository.create", return_value=encuentro_mock), \
         patch("app.domains.encuentros.service.get_miembros_by_grupo", return_value=[miembro1, miembro2, miembro3]), \
         patch("app.domains.encuentros.service.repository.create_asistencia", side_effect=fake_create_asistencia):
        service.crear_encuentro(db, data, actor, grupos_actor)

    assert len(asistencias_creadas) == 3
    for a in asistencias_creadas:
        assert a["estado"] == EstadoAsistenciaEnum.no_asistio
        assert a["encuentro_id"] == encuentro_mock.id
