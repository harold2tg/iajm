import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoIngresoEnum(str, Enum):
    cuota_asesor = "cuota_asesor"
    actividad_profondos = "actividad_profondos"
    tienda_misionera = "tienda_misionera"
    donacion_efectivo = "donacion_efectivo"
    otro = "otro"


class TipoDonacionEnum(str, Enum):
    efectivo = "efectivo"
    especie = "especie"


class ActividadProFondos(Base):
    __tablename__ = "actividades_profondos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    responsable: Mapped[str] = mapped_column(String(200), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    productos: Mapped[list["ProductoActividad"]] = relationship("ProductoActividad", back_populates="actividad")


class ProductoActividad(Base):
    __tablename__ = "productos_actividad"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actividad_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("actividades_profondos.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    costo_unitario: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    precio_venta: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    es_donado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    actividad: Mapped["ActividadProFondos"] = relationship("ActividadProFondos", back_populates="productos")


class Donacion(Base):
    __tablename__ = "donaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo: Mapped[TipoDonacionEnum] = mapped_column(nullable=False)
    actividad_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("actividades_profondos.id"), nullable=True)
    donante: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    cantidad_especie: Mapped[int | None] = mapped_column(nullable=True)
    valor_estimado: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    item_inventario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("items_inventario.id"), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OtroIngreso(Base):
    __tablename__ = "otros_ingresos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
