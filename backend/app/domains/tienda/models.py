import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EstadoVentaEnum(str, Enum):
    abierto = "abierto"
    cerrado = "cerrado"


class VentaDia(Base):
    __tablename__ = "ventas_dia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    registrado_por: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    observaciones: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_calculado: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    estado: Mapped[EstadoVentaEnum] = mapped_column(String(20), nullable=False, default=EstadoVentaEnum.abierto)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    detalles: Mapped[list["DetalleVentaDia"]] = relationship("DetalleVentaDia", back_populates="venta")


class DetalleVentaDia(Base):
    __tablename__ = "detalle_venta_dia"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venta_dia_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ventas_dia.id"), nullable=False)
    producto: Mapped[str] = mapped_column(String(200), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    venta: Mapped["VentaDia"] = relationship("VentaDia", back_populates="detalles")
