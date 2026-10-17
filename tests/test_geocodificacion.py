"""Geocodificación: tabla de lugares conocidos, consulta a Nominatim y motivo de los descartes en el log."""

import logging

import pytest

from app.models.concierto import Concierto
from app.models.ubicacion import Ubicacion
from app.services import geocoding_service, scraper_service
from app.services.geocoding_service import dentro_de_amba, obtener_coordenadas
from app.services.lugares_conocidos import LUGARES_CONOCIDOS, _clave, coordenadas_conocidas


class SesionFalsa:
    """Reemplaza la sesión HTTP: guarda los parámetros de cada pedido y responde `resultados`."""

    def __init__(self, resultados):
        self.resultados = resultados
        self.pedidos = []

    def get(self, url, params=None, timeout=None):
        self.pedidos.append(params)
        sesion = self

        class Respuesta:
            def raise_for_status(self):
                pass

            def json(self):
                return sesion.resultados

        return Respuesta()


@pytest.fixture
def nominatim(monkeypatch):
    """Nominatim simulado, sin red. Por defecto no encuentra nada."""
    sesion = SesionFalsa([])
    monkeypatch.setattr(geocoding_service, "_sesion", sesion)
    return sesion


def evento(ubicacion, nombre="Gira"):
    return {
        "nombre_evento": nombre,
        "artista": "Artista",
        "url_evento": None,
        "ubicacion": ubicacion,
        "fecha": "20/10/26",
        "hora": "21:00",
    }


# ---------- Tabla de lugares conocidos (sin base) ----------


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("Estadio Huracán, CABA", "estadio huracan, caba"),
        ("  Estadio   Único Diego A. Maradona,  La Plata ", "estadio unico diego a. maradona, la plata"),
        ("ESTADIO VÉLEZ SARSFIELD, CABA", "estadio velez sarsfield, caba"),
    ],
)
def test_clave_normaliza_mayusculas_tildes_y_espacios(texto, esperado):
    assert _clave(texto) == esperado


def test_lugar_conocido_se_encuentra_aunque_cambien_tildes_o_mayusculas():
    assert coordenadas_conocidas("ESTADIO HURACAN, caba") == LUGARES_CONOCIDOS["estadio huracan, caba"]


def test_lugar_desconocido_devuelve_none():
    assert coordenadas_conocidas("Bar Inventado, CABA") == (None, None)
    assert coordenadas_conocidas(None) == (None, None)


@pytest.mark.parametrize("clave", sorted(LUGARES_CONOCIDOS))
def test_todos_los_lugares_conocidos_estan_en_amba(clave):
    # Protege de un error de tipeo (por ejemplo, invertir latitud y longitud)
    lat, lon = LUGARES_CONOCIDOS[clave]
    assert dentro_de_amba(lat, lon)


def test_las_claves_ya_estan_normalizadas():
    for clave in LUGARES_CONOCIDOS:
        assert _clave(clave) == clave


# ---------- obtener_coordenadas (Nominatim simulado) ----------


def test_lugar_conocido_no_consulta_nominatim(nominatim):
    assert obtener_coordenadas("Mandarine Park, CABA") == LUGARES_CONOCIDOS["mandarine park, caba"]
    assert nominatim.pedidos == []


def test_nominatim_se_consulta_solo_en_argentina(nominatim):
    nominatim.resultados = [{"lat": "-34.6", "lon": "-58.4"}]

    assert obtener_coordenadas("Niceto Club, CABA") == ("-34.6", "-58.4")
    assert nominatim.pedidos[0]["countrycodes"] == "ar"
    assert nominatim.pedidos[0]["q"] == "Niceto Club, CABA"


def test_sin_resultados_de_nominatim_devuelve_none(nominatim):
    assert obtener_coordenadas("Bar Inventado, CABA") == (None, None)


# ---------- Ingesta: lugar conocido y motivo de los descartes ----------


def test_concierto_en_lugar_conocido_se_guarda(base, nominatim):
    assert scraper_service._guardar_concierto(evento("Estadio Huracán, CABA"), {}) is True

    ubicacion = Ubicacion.query.one()
    assert ubicacion.nombre == "Estadio Huracán, CABA"
    assert Concierto.query.one().ubicacion == ubicacion.id
    assert nominatim.pedidos == []


def test_cada_descarte_dice_el_motivo_y_se_geocodifica_una_sola_vez(base, nominatim, caplog):
    descartadas = {}
    with caplog.at_level(logging.INFO, logger=scraper_service.__name__):
        for nombre in ("Show 1", "Show 2"):
            guardado = scraper_service._guardar_concierto(evento("Bar Inventado, CABA", nombre), descartadas)
            assert guardado is False

    assert len(nominatim.pedidos) == 1  # el segundo usa el motivo guardado
    mensajes = [registro.getMessage() for registro in caplog.records]
    assert mensajes == [
        "No se agrega el concierto 'Show 1': 'Bar Inventado, CABA' no se encontró la ubicación",
        "No se agrega el concierto 'Show 2': 'Bar Inventado, CABA' no se encontró la ubicación",
    ]


def test_lugar_fuera_de_amba_dice_el_motivo(base, nominatim, caplog):
    nominatim.resultados = [{"lat": "-32.95", "lon": "-60.64"}]  # Rosario
    with caplog.at_level(logging.INFO, logger=scraper_service.__name__):
        assert scraper_service._guardar_concierto(evento("Teatro El Círculo, Rosario"), {}) is False

    assert "'Teatro El Círculo, Rosario' está fuera de AMBA" in caplog.text
    assert Ubicacion.query.count() == 0
