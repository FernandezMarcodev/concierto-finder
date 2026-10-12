"""Endpoints /api/metricas/...: forma de las respuestas, caché y errores 400."""

from datetime import date

import pytest

ENDPOINTS = ["resumen", "conciertos_por_mes", "lugares", "artistas", "densidad", "distancias"]


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch, hoy):
    monkeypatch.setattr("app.services.metricas_service.hoy_argentina", lambda: hoy)


@pytest.fixture
def datos(crear_ubicacion, crear_concierto):
    obras = crear_ubicacion("Estadio Obras", lat=-34.5452, lng=-58.4472)
    crear_concierto(artista="Fito", fecha=date(2026, 1, 10), ubicacion=obras)
    crear_concierto(artista="Fito", fecha=date(2026, 3, 5), ubicacion=obras)


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_todos_responden_con_filtro_y_cache(cliente, datos, endpoint):
    respuesta = cliente.get(f"/api/metricas/{endpoint}?desde=2026-01-01&hasta=2026-12-31")

    assert respuesta.status_code == 200
    assert respuesta.get_json()["filtro"] == {"desde": "2026-01-01", "hasta": "2026-12-31"}
    assert respuesta.headers["Cache-Control"] == "public, max-age=300"


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_todos_rechazan_fechas_invalidas(cliente, endpoint):
    respuesta = cliente.get(f"/api/metricas/{endpoint}?desde=ayer")

    assert respuesta.status_code == 400
    assert "desde" in respuesta.get_json()["error"]


def test_resumen(cliente, datos):
    cuerpo = cliente.get("/api/metricas/resumen").get_json()

    assert cuerpo["total"] == 2
    assert cuerpo["pasados"] == 2  # hoy es el 15/10/2026
    assert cuerpo["primera_fecha"] == "2026-01-10"


def test_conciertos_por_mes(cliente, datos):
    meses = cliente.get("/api/metricas/conciertos_por_mes").get_json()["meses"]

    assert meses == [
        {"mes": "2026-01", "cantidad": 1},
        {"mes": "2026-02", "cantidad": 0},
        {"mes": "2026-03", "cantidad": 1},
    ]


def test_lugares_y_artistas(cliente, datos):
    lugares = cliente.get("/api/metricas/lugares?limite=5").get_json()["lugares"]
    artistas = cliente.get("/api/metricas/artistas").get_json()["artistas"]

    assert lugares == [{"id": 1, "nombre": "Estadio Obras", "cantidad": 2}]
    assert artistas == [{"artista": "Fito", "cantidad": 2, "lugares": 1}]


def test_densidad_devuelve_lng_lat_cantidad(cliente, datos):
    cuerpo = cliente.get("/api/metricas/densidad?celda=0.01").get_json()

    assert cuerpo["celda"] == 0.01
    assert cuerpo["puntos"] == [[-58.45, -34.55, 2]]  # [lng, lat, cantidad]


def test_distancias_con_punto_y_rangos(cliente, datos):
    cuerpo = cliente.get("/api/metricas/distancias?lat=-34.5452&lng=-58.4472&rangos=0,1").get_json()

    assert cuerpo["punto"] == [-58.4472, -34.5452]
    assert cuerpo["rangos"] == [
        {"desde_km": 0, "hasta_km": 1, "cantidad": 2},
        {"desde_km": 1, "hasta_km": None, "cantidad": 0},
    ]


def test_limite_invalido(cliente):
    respuesta = cliente.get("/api/metricas/lugares?limite=500")

    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "'limite' debe estar entre 1 y 50"}
