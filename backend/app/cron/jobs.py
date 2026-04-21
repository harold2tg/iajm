"""
Cron jobs del sistema IAJM.

- reasignar_grupos_diario: cada día a las 02:00 AM.
  Itera todos los miembros activos y reasigna al grupo correcto según edad actual.

- generar_cuotas_mensual: día 1 de cada mes a las 03:00 AM.
  Genera cuotas mensuales para todos los asesores activos.
"""
from __future__ import annotations

import logging
from datetime import date

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.domains.grupos.repository import get_grupo_para_edad
from app.domains.miembros.models import Miembro
from app.domains.miembros.models import HistorialGrupo

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _calcular_edad(fecha_nacimiento: date) -> int:
    hoy = date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


# ---------------------------------------------------------------------------
# Job 1 — Reasignar grupos diario (02:00 AM)
# ---------------------------------------------------------------------------

def reasignar_grupos_diario() -> None:
    """Reasigna cada miembro activo al grupo que corresponde a su edad actual."""
    db = SessionLocal()
    try:
        miembros = db.query(Miembro).filter(Miembro.activo == True).all()
        reasignados = 0

        for miembro in miembros:
            edad_actual = _calcular_edad(miembro.fecha_nacimiento)
            grupo_correcto = get_grupo_para_edad(db, edad_actual)

            if grupo_correcto is None:
                logger.warning(
                    "No hay grupo configurado para edad %d (miembro %s)",
                    edad_actual,
                    miembro.id,
                )
                continue

            if miembro.grupo_id != grupo_correcto.id:
                historial = HistorialGrupo(
                    miembro_id=miembro.id,
                    grupo_anterior_id=miembro.grupo_id,
                    grupo_nuevo_id=grupo_correcto.id,
                    motivo="Reasignación automática diaria por edad",
                )
                db.add(historial)
                miembro.grupo_id = grupo_correcto.id
                miembro.edad = edad_actual
                reasignados += 1

        db.commit()
        logger.info("reasignar_grupos_diario: %d miembros reasignados", reasignados)
    except Exception:
        db.rollback()
        logger.exception("Error en reasignar_grupos_diario")
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Job 2 — Generar cuotas mensual (día 1 de cada mes, 03:00 AM)
# ---------------------------------------------------------------------------

def generar_cuotas_mensual() -> None:
    """Genera cuotas mensuales para todos los asesores activos."""
    from app.domains.asesores.service import generar_cuotas_mes  # import local para evitar circular

    hoy = date.today()
    db = SessionLocal()
    try:
        creadas = generar_cuotas_mes(db, mes=hoy.month, anio=hoy.year, monto_default=0.0)
        db.commit()
        logger.info(
            "generar_cuotas_mensual: %d cuotas creadas para %d/%d",
            creadas,
            hoy.month,
            hoy.year,
        )
    except Exception:
        db.rollback()
        logger.exception("Error en generar_cuotas_mensual")
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Registro de jobs en el scheduler
# ---------------------------------------------------------------------------

scheduler.add_job(
    reasignar_grupos_diario,
    trigger="cron",
    hour=2,
    minute=0,
    id="reasignar_grupos_diario",
    replace_existing=True,
)

scheduler.add_job(
    generar_cuotas_mensual,
    trigger="cron",
    day=1,
    hour=3,
    minute=0,
    id="generar_cuotas_mensual",
    replace_existing=True,
)
