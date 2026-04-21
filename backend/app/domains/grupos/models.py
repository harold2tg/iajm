import uuid
from enum import Enum

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TipoGrupoEnum(str, Enum):
    infancia = "infancia"
    adolescencia = "adolescencia"
    juventud = "juventud"


class Grupo(Base):
    __tablename__ = "grupos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tipo: Mapped[TipoGrupoEnum] = mapped_column(nullable=False)
    edad_minima: Mapped[int] = mapped_column(Integer, nullable=False)
    edad_maxima: Mapped[int] = mapped_column(Integer, nullable=False)
