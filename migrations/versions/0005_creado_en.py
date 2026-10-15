"""conciertos.creado_en: cuándo encontró la ingesta cada concierto.

Habilita dos métricas: la anticipación con que se anuncian los conciertos (fecha del concierto
menos fecha en que apareció) y la salud de la ingesta (cuántos conciertos nuevos entran por día).

La columna se agrega en dos pasos a propósito: primero sin valor por defecto y después con
DEFAULT now(). Si se agregara directamente con DEFAULT now(), PostgreSQL completaría todas las
filas existentes con la hora de la migración, y diría (en falso) que todos los conciertos
actuales se encontraron hoy. Así, los anteriores quedan en null ("no se sabe") y solo los nuevos
llevan la fecha real.

Revision ID: 0005_creado_en
Revises: 0004_seguridad_rls
Create Date: 2026-10-15
"""

import sqlalchemy as sa
from alembic import op

revision = "0005_creado_en"
down_revision = "0004_seguridad_rls"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("conciertos", sa.Column("creado_en", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("conciertos", "creado_en", server_default=sa.text("now()"))


def downgrade():
    op.drop_column("conciertos", "creado_en")
