import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EstadoEncuentroEnum(str, Enum):
    abierto = "abierto"
    cerrado = "cerrado"


class EstadoAsistenciaEnum(str, Enum):
    asistio = "asistio"
    no_asistio = "no_asistio"
    justificado = "justificado"


class Encuentro(Base):
    __tablename__ = "encuentros"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False, index=True
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    creado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    tema: Mapped[str | None] = mapped_column(String(300), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[EstadoEncuentroEnum] = mapped_column(
        nullable=False, default=EstadoEncuentroEnum.abierto
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    cerrado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    asistencias: Mapped[list["AsistenciaEncuentro"]] = relationship(
        "AsistenciaEncuentro", back_populates="encuentro"
    )


class LogReaperturaEncuentro(Base):
    __tablename__ = "log_reapertura_encuentro"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    encuentro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("encuentros.id"), nullable=False, index=True
    )
    reabierto_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    reabierto_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AsistenciaEncuentro(Base):
    __tablename__ = "asistencia_encuentro"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    encuentro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("encuentros.id"), nullable=False, index=True
    )
    miembro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("miembros.id"), nullable=False, index=True
    )
    estado: Mapped[EstadoAsistenciaEnum] = mapped_column(nullable=False)
    registrado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    registrado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    encuentro: Mapped["Encuentro"] = relationship("Encuentro", back_populates="asistencias")
