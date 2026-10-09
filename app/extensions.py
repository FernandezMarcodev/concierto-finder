from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import alembic_helpers

db = SQLAlchemy()

# Los helpers de GeoAlchemy2 hacen que `flask db migrate` ignore las tablas de
# PostGIS (spatial_ref_sys, etc.) y sepa escribir columnas Geometry.
migrate = Migrate(
    include_object=alembic_helpers.include_object,
    render_item=alembic_helpers.render_item,
)
