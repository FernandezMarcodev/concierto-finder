"""Migraciones de Alembic: se pueden revertir y coinciden con los modelos."""

from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from flask_migrate import downgrade, upgrade
from sqlalchemy import inspect

from app.extensions import db

DIRECTORIO_MIGRACIONES = str(Path(__file__).resolve().parent.parent / "migrations")
TABLAS_DEL_PROYECTO = {"conciertos", "ubicaciones"}


def _solo_tablas_del_proyecto(objeto, nombre, tipo, reflejado, comparado_con):
    # La imagen de PostGIS trae tablas propias (por ejemplo, las del geocodificador TIGER):
    # se comparan solo las tablas de este proyecto y sus índices o columnas.
    if tipo == "table":
        return nombre in TABLAS_DEL_PROYECTO
    return objeto.table.name in TABLAS_DEL_PROYECTO


def test_los_modelos_coinciden_con_las_migraciones(app):
    """Si falla, cambió un modelo sin su migración (correr `flask --app app db migrate`)."""
    with app.app_context(), db.engine.connect() as conexion:
        contexto = MigrationContext.configure(conexion, opts={"include_object": _solo_tablas_del_proyecto})
        diferencias = compare_metadata(contexto, db.metadata)

    assert diferencias == []


def test_downgrade_y_upgrade_completos(app):
    with app.app_context():
        downgrade(directory=DIRECTORIO_MIGRACIONES, revision="base")
        assert not inspect(db.engine).has_table("conciertos")

        upgrade(directory=DIRECTORIO_MIGRACIONES)
        indices = {i["name"] for i in inspect(db.engine).get_indexes("conciertos")}
        assert {"ix_conciertos_fecha", "ix_conciertos_ubicacion"} <= indices
