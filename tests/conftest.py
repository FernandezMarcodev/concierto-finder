"""
Configuración compartida de los tests.

Los tests corren contra una base PostgreSQL + PostGIS real (no SQLite ni mocks): las consultas
usan funciones de PostGIS (ST_DWithin, Geography) y `IS NOT DISTINCT FROM`, que solo se pueden
probar en serio contra el mismo motor que usa producción.

La base se indica con TEST_DATABASE_URL y su nombre tiene que terminar en `_test`. Los tests
borran todas las filas después de cada caso: el control evita apuntarlos por error a la base de
desarrollo o a la de producción.
"""

import os
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import pytest

# Fecha fija para los tests: el resultado no depende del día en que se corren.
HOY = date(2026, 10, 15)

DIRECTORIO_MIGRACIONES = str(Path(__file__).resolve().parent.parent / "migrations")


def pytest_configure(config):
    """Corre antes de importar los tests: valida la base y define DATABASE_URL."""
    url = os.getenv("TEST_DATABASE_URL", "")
    nombre_base = urlparse(url).path.lstrip("/")
    if not nombre_base.endswith("_test"):
        raise pytest.UsageError(
            "Definí TEST_DATABASE_URL apuntando a una base cuyo nombre termine en '_test' "
            f"(recibido: {nombre_base or 'nada'}). Ver docs/OPERACION.md §9."
        )
    # app/config.py lee DATABASE_URL al importarse: tiene que estar definida antes de `import app`.
    os.environ["DATABASE_URL"] = url
    # Que un SCRAPER_TOKEN del entorno no cambie el resultado de los tests de autorización.
    os.environ.pop("SCRAPER_TOKEN", None)


@pytest.fixture
def hoy():
    return HOY


@pytest.fixture(scope="session")
def app():
    """La aplicación Flask, con el esquema creado por las migraciones (como en producción)."""
    from flask_migrate import upgrade

    from app import create_app

    aplicacion = create_app()
    aplicacion.config["TESTING"] = True
    with aplicacion.app_context():
        upgrade(directory=DIRECTORIO_MIGRACIONES)
    return aplicacion


@pytest.fixture
def base(app):
    """
    Sesión de base de datos para un test. Vacía las tablas antes y después: cada test arranca de
    cero, aunque la base tuviera datos de antes, y no depende del orden en que se ejecutan.
    """
    from sqlalchemy import text

    from app.extensions import db

    def vaciar():
        db.session.rollback()
        db.session.execute(text("TRUNCATE conciertos, ubicaciones RESTART IDENTITY CASCADE"))
        db.session.commit()

    with app.app_context():
        vaciar()
        yield db.session
        vaciar()
        db.session.remove()


@pytest.fixture
def cliente(app, base):
    """Cliente HTTP de prueba: hace pedidos a la API sin levantar un servidor."""
    return app.test_client()


@pytest.fixture
def crear_ubicacion(base):
    """Fábrica de ubicaciones. Por defecto, Estadio Obras."""
    from app.models.ubicacion import Ubicacion

    def _crear(nombre="Estadio Obras", lat=-34.5452, lng=-58.4472):
        ubicacion = Ubicacion(
            nombre=nombre,
            capacidad_total=0,
            # EWKT: el SRID y el punto en orden (lng lat), igual que PostGIS
            coordenadas=f"SRID=4326;POINT({lng} {lat})",
        )
        base.add(ubicacion)
        base.commit()
        return ubicacion

    return _crear


@pytest.fixture
def crear_concierto(base):
    """Fábrica de conciertos. Se guardan con commit para que los vea cualquier sesión."""
    from app.models.concierto import Concierto

    def _crear(nombre="Gira", artista="Artista", fecha=HOY, hora=None, ubicacion=None):
        concierto = Concierto(
            nombre=nombre,
            artista=artista,
            fecha=fecha,
            hora=hora,
            ubicacion=ubicacion.id if ubicacion else None,
        )
        base.add(concierto)
        base.commit()
        return concierto

    return _crear
