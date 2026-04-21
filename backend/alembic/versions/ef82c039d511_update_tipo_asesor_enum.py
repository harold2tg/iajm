"""update_tipo_asesor_enum

Revision ID: ef82c039d511
Revises: 9fb7c0742a5c
Create Date: 2026-04-20 18:20:51.818643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef82c039d511'
down_revision: Union[str, None] = '9fb7c0742a5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE tipoasesorenum ADD VALUE IF NOT EXISTS 'coordinador'")
    op.execute("ALTER TYPE tipoasesorenum ADD VALUE IF NOT EXISTS 'de_apoyo'")
    op.execute("ALTER TYPE tipoasesorenum ADD VALUE IF NOT EXISTS 'de_contingencia'")


def downgrade() -> None:
    # Postgres no permite DROP VALUE de un enum — la única forma es recrear el tipo
    # Se deja vacío intencionalmente: no se puede revertir ADD VALUE fácilmente
    pass
