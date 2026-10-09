"""Esquema inicial: ubicaciones y conciertos.

Refleja las tablas que antes se creaban a mano con db.create_all(). Si ya
existen (bases creadas antes de usar migraciones) no se tocan, así que
`flask db upgrade` funciona igual sobre una base nueva o una existente.

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

revision = "0001_esquema_inicial"
down_revision = None
branch_labels = None
depends_on = None


def _existe(tabla):
    # En modo --sql no hay conexión para inspeccionar: se emite el DDL completo.
    if op.get_context().as_sql:
        return False
    return sa.inspect(op.get_bind()).has_table(tabla)


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    if not _existe("ubicaciones"):
        op.create_table(
            "ubicaciones",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("nombre", sa.String(length=50), nullable=False),
            sa.Column("capacidad_total", sa.Integer(), nullable=False),
            sa.Column("coordenadas", Geometry("POINT", srid=4326, spatial_index=False), nullable=True),
            sa.Column("url_maps", sa.String(length=100), nullable=True),
        )
        # Mismo nombre que crea GeoAlchemy2 con create_all()
        op.create_index(
            "idx_ubicaciones_coordenadas", "ubicaciones", ["coordenadas"], postgresql_using="gist"
        )

    if not _existe("conciertos"):
        op.create_table(
            "conciertos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("nombre", sa.String(length=50), nullable=False),
            sa.Column("artista", sa.String(length=50), nullable=False),
            sa.Column("url_evento", sa.String(length=100), nullable=True),
            sa.Column(
                "ubicacion",
                sa.Integer(),
                sa.ForeignKey("ubicaciones.id", ondelete="CASCADE"),
                nullable=True,
            ),
            sa.Column("fecha", sa.Date(), nullable=True),
            sa.Column("hora", sa.Time(), nullable=True),
        )


def downgrade():
    op.drop_table("conciertos")
    op.drop_table("ubicaciones")
