#!/usr/bin/env python
"""
Seed script para el sistema IAJM.

Crea datos iniciales de forma idempotente:
  - 1 usuario administrador
  - 4 grupos con rangos de edad
  - 3 asesores
  - 5 miembros distribuidos en los grupos
  - 1 encuentro por grupo con asistencia pre-poblada

Uso:
    cd backend
    poetry run python scripts/seed.py
"""
from __future__ import annotations

import sys
import os

# Permitir imports de app desde el directorio backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.domains.asesores.models import Asesor, AsesorGrupo, TipoAsesorEnum
from app.domains.encuentros.models import AsistenciaEncuentro, Encuentro, EstadoAsistenciaEnum
from app.domains.grupos.models import Grupo, TipoGrupoEnum
from app.domains.miembros.models import Miembro, TipoMiembroEnum
from app.domains.usuarios.models import RolEnum, Usuario, UsuarioRol


def _hoy_menos_anios(anios: int) -> date:
    """Fecha de nacimiento aproximada para tener exactamente `anios` años hoy."""
    hoy = date.today()
    return hoy.replace(year=hoy.year - anios)


def run_seed() -> None:
    db = SessionLocal()
    try:
        # ------------------------------------------------------------------ #
        # 1. Usuario administrador                                             #
        # ------------------------------------------------------------------ #
        admin_email = "admin@iajm.org"
        admin = db.query(Usuario).filter(Usuario.email == admin_email).first()
        if admin is None:
            admin = Usuario(
                nombre_completo="Administrador IAJM",
                email=admin_email,
                password_hash=hash_password("Admin1234!"),
                activo=True,
            )
            db.add(admin)
            db.flush()

            rol_admin = UsuarioRol(
                usuario_id=admin.id,
                rol=RolEnum.administrador,
            )
            db.add(rol_admin)
            db.flush()
            print(f"[seed] Usuario admin creado: {admin_email}")
        else:
            print(f"[seed] Admin ya existe — omitiendo: {admin_email}")

        # ------------------------------------------------------------------ #
        # 2. Grupos                                                            #
        # ------------------------------------------------------------------ #
        grupos_data = [
            ("Trigo Verde",          TipoGrupoEnum.infancia,     4,  6),
            ("Trigo Maduro",         TipoGrupoEnum.infancia,     7,  9),
            ("Trigo Maduro Avanzado",TipoGrupoEnum.infancia,    10, 12),
            ("Adolescencia",         TipoGrupoEnum.adolescencia, 13, 15),
            ("Juventud",             TipoGrupoEnum.juventud,     16, 24),
        ]

        grupos: list[Grupo] = []
        for nombre, tipo, edad_min, edad_max in grupos_data:
            g = db.query(Grupo).filter(Grupo.nombre == nombre).first()
            if g is None:
                g = Grupo(
                    nombre=nombre,
                    tipo=tipo,
                    edad_minima=edad_min,
                    edad_maxima=edad_max,
                )
                db.add(g)
                db.flush()
                print(f"[seed] Grupo creado: {nombre} ({edad_min}-{edad_max})")
            else:
                print(f"[seed] Grupo ya existe — omitiendo: {nombre}")
            grupos.append(g)

        # ------------------------------------------------------------------ #
        # 3. Asesores                                                          #
        # ------------------------------------------------------------------ #
        asesores_data = [
            ("María García",   "3001112233", TipoAsesorEnum.base),
            ("Carlos López",   "3009998877", TipoAsesorEnum.base),
            ("Ana Martínez",   "3015554444", TipoAsesorEnum.de_apoyo),
        ]

        asesores: list[Asesor] = []
        for nombre, telefono, tipo in asesores_data:
            a = db.query(Asesor).filter(Asesor.nombre_completo == nombre).first()
            if a is None:
                a = Asesor(
                    nombre_completo=nombre,
                    telefono=telefono,
                    tipo=tipo,
                    activo=True,
                )
                db.add(a)
                db.flush()

                # Asignar al primer grupo que haga match (rotación simple)
                grupo_asignado = grupos[asesores_data.index((nombre, telefono, tipo)) % len(grupos)]
                ag = AsesorGrupo(asesor_id=a.id, grupo_id=grupo_asignado.id)
                db.add(ag)
                db.flush()
                print(f"[seed] Asesor creado: {nombre} → grupo {grupo_asignado.nombre}")
            else:
                print(f"[seed] Asesor ya existe — omitiendo: {nombre}")
            asesores.append(a)

        # ------------------------------------------------------------------ #
        # 4. Miembros                                                          #
        # ------------------------------------------------------------------ #
        # 5 miembros distribuidos: 2 en Exploradores, 1 en Aventureros,
        #                          1 en Jóvenes, 1 en Mayores
        miembros_data = [
            ("Lucía Pérez",      _hoy_menos_anios(5),  TipoMiembroEnum.infancia,     grupos[0], None,         "Juana Pérez",  "3101010101"),
            ("Tomás Ruiz",       _hoy_menos_anios(8),  TipoMiembroEnum.infancia,     grupos[1], None,         "Pedro Ruiz",   "3102020202"),
            ("Valentina Torres", _hoy_menos_anios(11), TipoMiembroEnum.infancia,     grupos[2], None,         "Laura Torres", "3103030303"),
            ("Sebastián Díaz",   _hoy_menos_anios(14), TipoMiembroEnum.adolescencia, grupos[3], None,         "Rosa Díaz",    "3104040404"),
            ("Camila Rodríguez", _hoy_menos_anios(18), TipoMiembroEnum.juventud,     grupos[4], "3105050505", None,           None),
        ]

        miembros: list[Miembro] = []
        for nombre, fnac, tipo, grupo, tel_personal, nombre_acudiente, tel_acudiente in miembros_data:
            m = db.query(Miembro).filter(Miembro.nombre_completo == nombre).first()
            if m is None:
                hoy = date.today()
                edad = hoy.year - fnac.year - ((hoy.month, hoy.day) < (fnac.month, fnac.day))
                m = Miembro(
                    nombre_completo=nombre,
                    fecha_nacimiento=fnac,
                    edad=edad,
                    tipo=tipo,
                    grupo_id=grupo.id,
                    fecha_ingreso=date.today() - timedelta(days=30),
                    activo=True,
                    telefono_personal=tel_personal,
                    nombre_acudiente=nombre_acudiente,
                    telefono_acudiente=tel_acudiente,
                )
                db.add(m)
                db.flush()
                print(f"[seed] Miembro creado: {nombre} → grupo {grupo.nombre}")
            else:
                print(f"[seed] Miembro ya existe — omitiendo: {nombre}")
            miembros.append(m)

        # ------------------------------------------------------------------ #
        # 5. Encuentros (1 por grupo) + asistencia pre-poblada                #
        # ------------------------------------------------------------------ #
        hoy = date.today()
        for grupo in grupos:
            enc = (
                db.query(Encuentro)
                .filter(Encuentro.grupo_id == grupo.id, Encuentro.fecha == hoy)
                .first()
            )
            if enc is None:
                enc = Encuentro(
                    grupo_id=grupo.id,
                    fecha=hoy,
                    tema=f"Encuentro inicial - {grupo.nombre}",
                    creado_por=admin.id,
                )
                db.add(enc)
                db.flush()

                # Asistencia: todos los miembros del grupo
                miembros_grupo = [m for m in miembros if m.grupo_id == grupo.id]
                for m in miembros_grupo:
                    asistencia = AsistenciaEncuentro(
                        encuentro_id=enc.id,
                        miembro_id=m.id,
                        estado=EstadoAsistenciaEnum.asistio,
                        registrado_por=admin.id,
                    )
                    db.add(asistencia)
                db.flush()
                print(f"[seed] Encuentro creado para grupo '{grupo.nombre}' con {len(miembros_grupo)} asistentes")
            else:
                print(f"[seed] Encuentro ya existe para grupo '{grupo.nombre}' en {hoy} — omitiendo")

        db.commit()
        print("\n[seed] ✅ Seed completado exitosamente.")
    except Exception as e:
        db.rollback()
        print(f"\n[seed] ❌ Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
