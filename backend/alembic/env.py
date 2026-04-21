import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base  # noqa: F401
from app.domains.usuarios.models import Usuario, UsuarioRol, LogAcceso  # noqa: F401
from app.domains.grupos.models import Grupo  # noqa: F401
from app.domains.miembros.models import Miembro, HistorialGrupo  # noqa: F401
from app.domains.asesores.models import Asesor, AsesorGrupo, CuotaAsesor  # noqa: F401
from app.domains.encuentros.models import Encuentro, AsistenciaEncuentro  # noqa: F401
from app.domains.tesoreria.models import ActividadProFondos, ProductoActividad, Donacion, OtroIngreso  # noqa: F401
from app.domains.gastos.models import CategoriaGasto, Gasto  # noqa: F401
from app.domains.tienda.models import VentaDia, DetalleVentaDia  # noqa: F401
from app.domains.inventario.models import ItemInventario  # noqa: F401
from app.domains.parroquial.models import ActividadParroquial  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow DATABASE_URL env var to override alembic.ini
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
