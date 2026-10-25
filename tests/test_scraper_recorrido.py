"""Recorrido de la agenda: qué se registra cuando una página no trae la lista de eventos (sin red)."""

import logging

from bs4 import BeautifulSoup

from app.services import scraper_service

PAGINA_SIN_LISTA = "<html><head><title>Just a moment...</title></head><body></body></html>"
PAGINA_CON_LISTA_VACIA = (
    '<html><body><div fs-cmsload-element="list" fs-cmsfilter-element="list"></div></body></html>'
)


def simular_paginas(monkeypatch, paginas):
    """Cada pedido devuelve la siguiente página de `paginas` (HTML)."""
    pendientes = iter(paginas)
    monkeypatch.setattr(
        scraper_service, "_obtener_html", lambda sesion, url: BeautifulSoup(next(pendientes), "html.parser")
    )


def test_primera_pagina_sin_lista_se_registra_como_error(monkeypatch, caplog):
    simular_paginas(monkeypatch, [PAGINA_SIN_LISTA])

    with caplog.at_level(logging.INFO, logger=scraper_service.__name__):
        assert scraper_service._recorrer_agenda() == []

    errores = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(errores) == 1
    assert "no tiene la lista de eventos" in errores[0].getMessage()
    assert "Just a moment..." in errores[0].getMessage()


def test_pagina_siguiente_sin_lista_es_el_fin_de_la_agenda(monkeypatch, caplog):
    simular_paginas(monkeypatch, [PAGINA_CON_LISTA_VACIA, PAGINA_SIN_LISTA])

    with caplog.at_level(logging.INFO, logger=scraper_service.__name__):
        scraper_service._recorrer_agenda()

    assert not [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert "fin de la agenda" in caplog.text
