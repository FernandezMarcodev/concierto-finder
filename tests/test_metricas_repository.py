"""Consultas SQL de las métricas, con datos chicos cuyo resultado se puede calcular a mano."""

from datetime import date

import pytest

from app.repositories import metricas_repository as repo

ENERO = date(2026, 1, 10)
MARZO = date(2026, 3, 20)


@pytest.fixture
def lugares(crear_ubicacion):
    return {
        "gran_rex": crear_ubicacion("Teatro Gran Rex", lat=-34.6033, lng=-58.3786),  # ≈ 0,1 km del Obelisco
        "opera": crear_ubicacion("Teatro Ópera", lat=-34.6036, lng=-58.3789),  # a ≈ 40 m del Gran Rex
        "obras": crear_ubicacion("Estadio Obras", lat=-34.5452, lng=-58.4472),  # ≈ 9 km
        "la_plata": crear_ubicacion("Estadio La Plata", lat=-34.9139, lng=-57.9893),  # ≈ 52 km
    }


def test_conciertos_por_mes_completa_los_meses_vacios(crear_concierto):
    crear_concierto(fecha=ENERO)
    crear_concierto(fecha=ENERO)
    crear_concierto(fecha=MARZO)
    crear_concierto(fecha=None)  # sin fecha: no entra en una serie temporal

    meses = [dict(m) for m in repo.conciertos_por_mes(None, None)]

    assert meses == [
        {"mes": "2026-01", "cantidad": 2},
        {"mes": "2026-02", "cantidad": 0},
        {"mes": "2026-03", "cantidad": 1},
    ]


def test_conciertos_por_mes_usa_los_limites_del_filtro(crear_concierto):
    crear_concierto(fecha=ENERO)

    meses = repo.conciertos_por_mes(date(2025, 12, 1), date(2026, 2, 28))

    assert [(m["mes"], m["cantidad"]) for m in meses] == [("2025-12", 0), ("2026-01", 1), ("2026-02", 0)]


def test_conciertos_por_mes_sin_datos(base):
    assert repo.conciertos_por_mes(None, None) == []


def test_resumen(hoy, lugares, crear_concierto):
    crear_concierto(artista="Fito", fecha=date(2026, 1, 1), ubicacion=lugares["obras"])
    crear_concierto(artista="fito ", fecha=hoy, ubicacion=lugares["obras"])  # mismo artista normalizado
    crear_concierto(artista="Charly", fecha=None, ubicacion=lugares["opera"])

    resumen = repo.resumen(None, None, hoy)

    assert resumen["total"] == 3
    assert resumen["vigentes"] == 2  # el de hoy y el sin fecha
    assert resumen["pasados"] == 1
    assert resumen["sin_fecha"] == 1
    assert resumen["lugares"] == 2
    assert resumen["artistas"] == 2
    assert resumen["primera_fecha"] == date(2026, 1, 1)
    assert resumen["ultima_fecha"] == hoy


def test_el_filtro_de_fechas_es_inclusivo_y_excluye_los_sin_fecha(hoy, crear_concierto):
    crear_concierto(fecha=ENERO)
    crear_concierto(fecha=MARZO)
    crear_concierto(fecha=None)

    assert repo.resumen(None, None, hoy)["total"] == 3  # sin filtro: todos
    assert repo.resumen(ENERO, MARZO, hoy)["total"] == 2  # los dos extremos entran
    assert repo.resumen(ENERO, None, hoy)["total"] == 2
    assert repo.resumen(None, ENERO, hoy)["total"] == 1


def test_ranking_de_lugares(lugares, crear_concierto):
    for _ in range(3):
        crear_concierto(ubicacion=lugares["obras"])
    crear_concierto(ubicacion=lugares["opera"])
    crear_concierto(ubicacion=lugares["gran_rex"])
    crear_concierto(ubicacion=None)  # sin lugar: no entra en el ranking

    ranking = repo.lugares_mas_activos(None, None, limite=2)

    # Empate en 1 entre Gran Rex y Ópera: desempata el nombre
    assert [(f["nombre"], f["cantidad"]) for f in ranking] == [("Estadio Obras", 3), ("Teatro Gran Rex", 1)]


def test_ranking_de_artistas_agrupa_variantes_de_escritura(lugares, crear_concierto):
    crear_concierto(artista="Sofía Ríos", ubicacion=lugares["obras"])
    crear_concierto(artista="Sofía Ríos", ubicacion=lugares["opera"])
    crear_concierto(artista="Sofia Rios", ubicacion=lugares["obras"])
    crear_concierto(artista="Mora", ubicacion=lugares["obras"])

    ranking = [dict(f) for f in repo.artistas_que_mas_se_repiten(None, None, limite=10)]

    assert ranking == [
        # Se muestra la escritura más frecuente; 3 conciertos en 2 lugares distintos
        {"artista": "Sofía Ríos", "cantidad": 3, "lugares": 2},
        {"artista": "Mora", "cantidad": 1, "lugares": 1},
    ]


def test_densidad_agrupa_lugares_cercanos_segun_la_celda(lugares, crear_concierto):
    crear_concierto(ubicacion=lugares["gran_rex"])
    crear_concierto(ubicacion=lugares["opera"])
    crear_concierto(ubicacion=lugares["obras"])

    celda_grande = repo.densidad(None, None, celda_grados=0.01)  # ≈ 1 km: los dos teatros suman juntos
    celda_chica = repo.densidad(None, None, celda_grados=0.001)  # ≈ 100 m: quedan separados

    assert sorted(f["cantidad"] for f in celda_grande) == [1, 2]
    assert sorted(f["cantidad"] for f in celda_chica) == [1, 1, 1]
    assert celda_grande[0]["lat"] == pytest.approx(-34.60)
    assert celda_grande[0]["lng"] == pytest.approx(-58.38)


def test_distancias_desde_el_obelisco(lugares, crear_concierto):
    crear_concierto(ubicacion=lugares["gran_rex"])
    crear_concierto(ubicacion=lugares["obras"])
    crear_concierto(ubicacion=lugares["obras"])
    crear_concierto(ubicacion=lugares["la_plata"])

    rangos = repo.distribucion_de_distancias(None, None, -34.6037, -58.3816, [0, 5, 10, 20, 40])

    assert [(r["desde_km"], r["hasta_km"], r["cantidad"]) for r in rangos] == [
        (0, 5, 1),
        (5, 10, 2),
        (10, 20, 0),  # los rangos vacíos también aparecen
        (20, 40, 0),
        (40, None, 1),  # el último rango no tiene tope
    ]
