"""Parseo de fechas, horas y textos de la fuente (funciones puras: no tocan la red ni la base)."""

from datetime import date, time

import pytest

from app.models.concierto import LARGO_TEXTO
from app.services.scraper_service import _parsear_fecha, _parsear_hora, _recortar


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("05/10/26", date(2026, 10, 5)),
        ("05/10/2026", date(2026, 10, 5)),
        (" 31/12/26 ", date(2026, 12, 31)),
        ("31/02/26", None),  # fecha imposible
        ("A confirmar", None),
        ("", None),
        (None, None),
    ],
)
def test_parsear_fecha(texto, esperado):
    assert _parsear_fecha(texto) == esperado


@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("21:00", time(21, 0)),
        ("21:00:30", time(21, 0, 30)),
        ("25:00", None),
        ("", None),
        (None, None),
    ],
)
def test_parsear_hora(texto, esperado):
    assert _parsear_hora(texto) == esperado


def test_recortar_al_largo_de_la_columna():
    assert len(_recortar("x" * 80)) == LARGO_TEXTO
    assert _recortar("corto") == "corto"
    assert _recortar(None) is None
