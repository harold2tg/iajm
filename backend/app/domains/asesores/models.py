import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoAsesorEnum(str, Enum):
    base = "base"
    coordinador = "coordinador"
    de_apoyo = "de_apoyo"
    de_contingencia = "de_contingencia"


class EstadoCuotaEnum(str, Enum):
    pagado = "pagado"
    pendiente = "pendiente"


class Asesor(Base):
    __tablename__ = "asesores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo: Mapped[TipoAsesorEnum] = mapped_column(nullable=False)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    grupos: Mapped[list["AsesorGrupo"]] = relationship("AsesorGrupo", back_populates="asesor")
    cuotas: Mapped[list["CuotaAsesor"]] = relationship("CuotaAsesor", back_populates="asesor")


class AsesorGrupo(Base):
    __tablename__ = "asesor_grupo"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asesor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )

    asesor: Mapped["Asesor"] = relationship("Asesor", back_populates="grupos")


class CuotaAsesor(Base):
    __tablename__ = "cuotas_asesor"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asesor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("asesores.id"), nullable=False
    )
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fecha_pago: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[EstadoCuotaEnum] = mapped_column(nullable=False, default=EstadoCuotaEnum.pendiente)

    asesor: Mapped["Asesor"] = relationship("Asesor", back_populates="cuotas")
