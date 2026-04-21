import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EstadoItemEnum(str, Enum):
    bueno = "bueno"
    regular = "regular"
    danado = "dañado"


class TipoItemEnum(str, Enum):
    formativo = "formativo"
    liturgico = "liturgico"
    insumo = "insumo"


class OrigenItemEnum(str, Enum):
    compra = "compra"
    donacion = "donacion"


class ItemInventario(Base):
    __tablename__ = "items_inventario"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[EstadoItemEnum | None] = mapped_column(nullable=True)
    ubicacion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    responsable: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tipo: Mapped[TipoItemEnum | None] = mapped_column(nullable=True)
    origen: Mapped[OrigenItemEnum | None] = mapped_column(nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
