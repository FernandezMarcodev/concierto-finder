"""url_evento pasa de VARCHAR(100) a TEXT.

Muchas URLs de compra de entradas superan los 100 caracteres y el INSERT
fallaba, perdiendo el concierto.

Revision ID: 0002_url_evento_text
Revises: 0001_esquema_inicial
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_url_evento_text"
down_revision = "0001_esquema_inicial"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "conciertos",
        "url_evento",
        type_=sa.Text(),
        existing_type=sa.String(length=100),
        existing_nullable=True,
    )


def downgrade():
    # Las URLs más largas se recortan: sin el USING el ALTER fallaría.
    op.alter_column(
        "conciertos",
        "url_evento",
        type_=sa.String(length=100),
        existing_type=sa.Text(),
        existing_nullable=True,
        postgresql_using="left(url_evento, 100)",
    )
