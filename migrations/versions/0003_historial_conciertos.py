"""Historial de conciertos: índices sobre conciertos.fecha y conciertos.ubicacion.

Desde esta versión la limpieza diaria ya no borra los conciertos pasados: quedan
como historial para las métricas, y los listados públicos filtran los vigentes
por fecha. La tabla crece con el tiempo, así que se indexan las dos columnas por
las que se filtra y se agrupa:

- fecha: todos los listados filtran `fecha >= hoy` y las métricas agrupan por mes.
- ubicacion: PostgreSQL no indexa solo las claves foráneas; las métricas agrupan
  por lugar y el borrado en cascada de una ubicación busca sus conciertos.

No hace falta mover ni transformar datos: "vigente" se deriva de la fecha (RN-02).

Revision ID: 0003_historial_conciertos
Revises: 0002_url_evento_text
Create Date: 2026-10-11
"""

from alembic import op

revision = "0003_historial_conciertos"
down_revision = "0002_url_evento_text"
branch_labels = None
depends_on = None


def upgrade():
    # Mismos nombres que generaría SQLAlchemy con index=True en el modelo (ix_<tabla>_<columna>)
    op.create_index("ix_conciertos_fecha", "conciertos", ["fecha"])
    op.create_index("ix_conciertos_ubicacion", "conciertos", ["ubicacion"])


def downgrade():
    op.drop_index("ix_conciertos_ubicacion", table_name="conciertos")
    op.drop_index("ix_conciertos_fecha", table_name="conciertos")
