import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoMiembroEnum(str, Enum):
    infancia = "infancia"
    adolescencia = "adolescencia"
    juventud = "juventud"


class Miembro(Base):
    __tablename__ = "miembros"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[TipoMiembroEnum] = mapped_column(nullable=False)
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False, index=True
    )
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
    telefono_personal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nombre_acudiente: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telefono_acudiente: Mapped[str | None] = mapped_column(String(20), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ingresado_en_encuentro_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("encuentros.id"), nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    grupo: Mapped["Grupo"] = relationship("Grupo")  # type: ignore[name-defined]

    @property
    def nombre_grupo(self) -> str | None:
        return self.grupo.nombre if self.grupo else None


class HistorialGrupo(Base):
    __tablename__ = "historial_grupo"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("miembros.id"), nullable=False
    )
    grupo_anterior_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    grupo_nuevo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    cambiado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    motivo: Mapped[str | None] = mapped_column(String(300), nullable=True)
