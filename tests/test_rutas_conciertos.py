"""Endpoints HTTP de conciertos: respuestas, serialización, validación y token de ingesta."""

from datetime import time, timedelta

import pytest


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch, hoy):
    """Las rutas calculan hoy en hora argentina: en los tests se fija para no depender del reloj."""
    monkeypatch.setattr("app.routes.conciertos.hoy_argentina", lambda: hoy)


def test_estado(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok"}


def test_conciertos_devuelve_solo_vigentes_y_se_puede_cachear(cliente, hoy, crear_concierto):
    crear_concierto(nombre="Ayer", fecha=hoy - timedelta(days=1))
    crear_concierto(nombre="Hoy", fecha=hoy)

    respuesta = cliente.get("/conciertos")

    assert respuesta.status_code == 200
    assert [c["nombre"] for c in respuesta.get_json()["conciertos"]] == ["Hoy"]
    assert respuesta.headers["Cache-Control"] == "public, max-age=300"


def test_serializacion_de_un_concierto(cliente, hoy, crear_ubicacion, crear_concierto):
    obras = crear_ubicacion(lat=-34.5452, lng=-58.4472)
    crear_concierto(nombre="Gira", artista="Fito", fecha=hoy, hora=time(21, 0), ubicacion=obras)
    crear_concierto(nombre="Sin lugar", fecha=None)

    con_lugar, sin_lugar = cliente.get("/conciertos").get_json()["conciertos"]

    assert con_lugar["fecha"] == "2026-10-15"
    assert con_lugar["hora"] == "21:00:00"
    # Orden [lng, lat], como en PostGIS
    assert con_lugar["ubicacion_detalle"]["coordenadas"] == pytest.approx([-58.4472, -34.5452])
    assert sin_lugar["fecha"] is None
    assert sin_lugar["hora"] is None
    assert sin_lugar["ubicacion_detalle"] is None


def test_conciertos_cerca(cliente, crear_ubicacion, crear_concierto):
    crear_concierto(nombre="En Obras", ubicacion=crear_ubicacion())

    respuesta = cliente.get("/conciertos_cerca?lat=-34.6037&lng=-58.3816&km=10")

    assert respuesta.status_code == 200
    assert [c["nombre"] for c in respuesta.get_json()["conciertos"]] == ["En Obras"]


@pytest.mark.parametrize(
    "parametros",
    [
        "",  # faltan todos
        "lat=-34.6&lng=-58.4",  # falta km
        "lat=-34.6&lng=-58.4&km=0",
        "lat=-34.6&lng=-58.4&km=-5",
        "lat=texto&lng=-58.4&km=5",
    ],
)
def test_conciertos_cerca_rechaza_parametros_invalidos(cliente, parametros):
    respuesta = cliente.get(f"/conciertos_cerca?{parametros}")

    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "Parámetros inválidos"}


def test_ingesta_deshabilitada_sin_token_configurado(cliente):
    assert cliente.post("/ingestar_agendade").status_code == 503


@pytest.mark.parametrize(
    "encabezados, url",
    [
        ({}, "/ingestar_agendade"),  # sin token
        ({"Authorization": "Bearer incorrecto"}, "/ingestar_agendade"),
        ({}, "/ingestar_agendade?token=incorrecto"),
    ],
)
def test_ingesta_rechaza_token_incorrecto(app, cliente, monkeypatch, encabezados, url):
    monkeypatch.setitem(app.config, "SCRAPER_TOKEN", "secreto")

    respuesta = cliente.post(url, headers=encabezados)

    assert respuesta.status_code == 401
    assert respuesta.get_json() == {"error": "No autorizado"}
