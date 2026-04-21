from __future__ import annotations

import uuid
import pytest
from datetime import date
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.domains.miembros.schemas import MiembroCreate, MiembroUpdate
from app.domains.miembros import service
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


def fecha_para_edad(edad: int) -> date:
    hoy = date.today()
    return hoy.replace(year=hoy.year - edad)


# Test 1
def test_crear_miembro_infancia_sin_acudiente():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    data = MiembroCreate(
        nombre_completo="Juan Perez",
        fecha_nacimiento=fecha_para_edad(8),
        fecha_ingreso=date.today(),
        nombre_acudiente=None,
        telefono_acudiente=None,
    )
    grupo_mock = MagicMock()
    grupo_mock.id = uuid.uuid4()

    with patch("app.domains.miembros.service.get_grupo_para_edad", return_value=grupo_mock):
        with pytest.raises(HTTPException) as exc_info:
            service.crear_miembro(db, data, actor)
    assert exc_info.value.status_code == 422


# Test 2
def test_crear_miembro_infancia_con_acudiente():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    data = MiembroCreate(
        nombre_completo="Maria Lopez",
        fecha_nacimiento=fecha_para_edad(8),
        fecha_ingreso=date.today(),
        nombre_acudiente="Carlos Lopez",
        telefono_acudiente="3001234567",
    )
    grupo_mock = MagicMock()
    grupo_mock.id = uuid.uuid4()

    miembro_mock = MagicMock()
    miembro_mock.tipo = "infancia"

    with patch("app.domains.miembros.service.get_grupo_para_edad", return_value=grupo_mock), \
         patch("app.domains.miembros.service.create", return_value=miembro_mock):
        result = service.crear_miembro(db, data, actor)

    assert result is not None


# Test 3
def test_crear_miembro_juventud_sin_telefono():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    data = MiembroCreate(
        nombre_completo="Pedro Ramirez",
        fecha_nacimiento=fecha_para_edad(18),
        fecha_ingreso=date.today(),
        telefono_personal=None,
    )
    grupo_mock = MagicMock()
    grupo_mock.id = uuid.uuid4()

    with patch("app.domains.miembros.service.get_grupo_para_edad", return_value=grupo_mock):
        with pytest.raises(HTTPException) as exc_info:
            service.crear_miembro(db, data, actor)
    assert exc_info.value.status_code == 422


# Test 4
def test_crear_miembro_edad_fuera_de_rango():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    data = MiembroCreate(
        nombre_completo="Bebe Test",
        fecha_nacimiento=fecha_para_edad(3),
        fecha_ingreso=date.today(),
    )

    with pytest.raises(HTTPException) as exc_info:
        service.crear_miembro(db, data, actor)
    assert exc_info.value.status_code == 422


# Test 5
def test_crear_miembro_edad_fuera_de_rango_mayor():
    db = MagicMock()
    actor = make_actor(RolEnum.administrador)
    data = MiembroCreate(
        nombre_completo="Adulto Test",
        fecha_nacimiento=fecha_para_edad(25),
        fecha_ingreso=date.today(),
    )

    with pytest.raises(HTTPException) as exc_info:
        service.crear_miembro(db, data, actor)
    assert exc_info.value.status_code == 422


# Test 6
def test_asesor_no_ve_miembros_de_otro_grupo():
    db = MagicMock()
    grupo_id_asesor = uuid.uuid4()
    grupo_id_otro = uuid.uuid4()
    actor = make_actor(RolEnum.asesor_grupo, grupo_id=grupo_id_asesor)
    grupos_actor = [grupo_id_asesor]

    miembro_mock = MagicMock()
    miembro_mock.grupo_id = grupo_id_otro

    with patch("app.domains.miembros.service.get_by_id", return_value=miembro_mock):
        with pytest.raises(HTTPException) as exc_info:
            service.obtener_miembro(db, uuid.uuid4(), actor, grupos_actor)
    assert exc_info.value.status_code == 403


# Test 7
def test_observador_ve_todos_los_miembros():
    db = MagicMock()
    actor = make_actor(RolEnum.observador)
    grupos_actor: list[uuid.UUID] = []

    miembros_mock = [MagicMock(), MagicMock()]

    with patch("app.domains.miembros.service.get_all", return_value=miembros_mock) as mock_get_all:
        result = service.listar_miembros(db, actor, grupos_actor)

    mock_get_all.assert_called_once_with(db)
    assert result == miembros_mock


# Test 8
def test_asesor_tesoreria_no_puede_crear_miembro():
    db = MagicMock()
    actor = make_actor(RolEnum.asesor_tesoreria)
    data = MiembroCreate(
        nombre_completo="Test User",
        fecha_nacimiento=fecha_para_edad(10),
        fecha_ingreso=date.today(),
        nombre_acudiente="Acudiente Test",
        telefono_acudiente="3009999999",
    )

    with pytest.raises(HTTPException) as exc_info:
        service.crear_miembro(db, data, actor)
    assert exc_info.value.status_code == 403
