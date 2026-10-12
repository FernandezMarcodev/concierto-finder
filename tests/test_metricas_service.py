"""Validación de parámetros de las métricas (funciones puras: no tocan la base)."""

from datetime import date

import pytest

from app.services import metricas_service as servicio
from app.services.metricas_service import ParametroInvalido


def test_filtro_vacio():
    filtro = servicio.leer_filtro({})

    assert filtro.desde is None and filtro.hasta is None
    assert filtro.a_dict() == {"desde": None, "hasta": None}


def test_filtro_con_fechas():
    filtro = servicio.leer_filtro({"desde": "2026-01-01", "hasta": "2026-03-31"})

    assert filtro.desde == date(2026, 1, 1)
    assert filtro.a_dict() == {"desde": "2026-01-01", "hasta": "2026-03-31"}


@pytest.mark.parametrize(
    "args",
    [
        {"desde": "01/01/2026"},  # formato argentino: la API usa ISO
        {"desde": "2026-02-30"},
        {"desde": "2026-03-01", "hasta": "2026-01-01"},  # desde > hasta
        {"desde": "2000-01-01", "hasta": "2026-01-01"},  # más de 10 años
    ],
)
def test_filtro_invalido(args):
    with pytest.raises(ParametroInvalido):
        servicio.leer_filtro(args)


def test_valores_por_defecto():
    assert servicio.leer_limite({}) == 10
    assert servicio.leer_celda({}) == 0.005
    assert servicio.leer_punto({}) == (servicio.LAT_OBELISCO, servicio.LNG_OBELISCO)
    assert servicio.leer_rangos({}) == [0, 5, 10, 20, 40]


def test_rangos_personalizados():
    assert servicio.leer_rangos({"rangos": "0,2.5,15"}) == [0, 2.5, 15]


@pytest.mark.parametrize(
    "lector, args",
    [
        (servicio.leer_limite, {"limite": "0"}),
        (servicio.leer_limite, {"limite": "51"}),
        (servicio.leer_limite, {"limite": "diez"}),
        (servicio.leer_celda, {"celda": "1"}),
        (servicio.leer_punto, {"lat": "-34.6"}),  # falta lng
        (servicio.leer_punto, {"lat": "-134.6", "lng": "-58.4"}),
        (servicio.leer_rangos, {"rangos": "5,10"}),  # no empieza en 0
        (servicio.leer_rangos, {"rangos": "0,10,5"}),  # no es creciente
        (servicio.leer_rangos, {"rangos": "0,a"}),
        (servicio.leer_rangos, {"rangos": ",".join(str(i) for i in range(11))}),  # demasiados
    ],
)
def test_parametros_invalidos(lector, args):
    with pytest.raises(ParametroInvalido):
        lector(args)
