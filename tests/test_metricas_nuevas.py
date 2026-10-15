"""Métricas agregadas en la segunda versión: concentración, día y horario, próximos días, calidad,
salud de la ingesta y anticipación (repositorio, validación y endpoints)."""

from datetime import UTC, date, datetime, time, timedelta

import pytest

from app.repositories import metricas_repository as repo
from app.services import metricas_service as servicio
from app.services.fechas import ZONA_HORARIA
from app.services.metricas_service import ParametroInvalido

VIERNES = date(2026, 10, 16)
SABADO = date(2026, 10, 17)


def _en_argentina(dia, hora=time(9, 10)):
    return datetime.combine(dia, hora, tzinfo=ZONA_HORARIA)


# ---------- Repositorio ----------


def test_concentracion_en_los_5_lugares_mas_activos(hoy, crear_ubicacion, crear_concierto):
    principal = crear_ubicacion("Principal")
    for _ in range(3):
        crear_concierto(ubicacion=principal)
    for i in range(5):
        crear_concierto(ubicacion=crear_ubicacion(f"Lugar {i}"))
    crear_concierto(ubicacion=None)  # sin lugar: no entra en la cuenta

    # 8 conciertos con lugar; los 5 lugares más activos suman 3 + 1 + 1 + 1 + 1 = 7
    assert float(repo.resumen(None, None, hoy)["concentracion_top5"]) == 87.5


def test_concentracion_sin_lugares_es_nula(hoy, crear_concierto):
    crear_concierto(ubicacion=None)

    assert repo.resumen(None, None, hoy)["concentracion_top5"] is None


def test_dia_y_horario_devuelve_la_grilla_completa(crear_concierto):
    crear_concierto(fecha=VIERNES, hora=time(21, 0))
    crear_concierto(fecha=VIERNES, hora=time(20, 30))
    crear_concierto(fecha=SABADO, hora=time(1, 0))  # trasnoche del sábado
    crear_concierto(fecha=SABADO, hora=None)  # sin hora: no entra

    celdas = repo.dia_y_horario(None, None)
    por_celda = {(c["dia"], c["franja"]): c["cantidad"] for c in celdas}

    assert len(celdas) == 35  # 7 días por 5 franjas, también las vacías
    assert por_celda[(5, 3)] == 2  # viernes, 20 a 22
    assert por_celda[(6, 5)] == 1  # sábado, trasnoche
    assert sum(por_celda.values()) == 3
    assert celdas[0]["nombre_franja"] == "Día (6 a 18)"


def test_proximos_dias_incluye_los_dias_sin_conciertos(hoy, crear_concierto):
    crear_concierto(fecha=hoy)
    crear_concierto(fecha=hoy + timedelta(days=2))
    crear_concierto(fecha=hoy + timedelta(days=10))  # fuera de la ventana de 7 días
    crear_concierto(fecha=hoy - timedelta(days=1))  # pasado

    dias = repo.proximos_dias(hoy, 7)

    assert [d["fecha"] for d in dias] == [hoy + timedelta(days=i) for i in range(7)]
    assert [d["cantidad"] for d in dias] == [1, 0, 1, 0, 0, 0, 0]


def test_calidad_cuenta_los_datos_faltantes(crear_ubicacion, crear_concierto):
    lugar = crear_ubicacion()
    crear_concierto(hora=time(21, 0), url="https://example.com/a", ubicacion=lugar)  # completo
    crear_concierto(hora=None, url=None, ubicacion=None)
    crear_concierto(fecha=None, hora=time(20, 0), url="", ubicacion=lugar)

    calidad = repo.calidad(None, None)

    assert dict(calidad) == {
        "total": 3,
        "sin_fecha": 1,
        "sin_hora": 1,
        "sin_entradas": 2,  # null y texto vacío
        "sin_ubicacion": 1,
    }


def test_ingesta_por_dia_usa_la_fecha_argentina(hoy, crear_concierto):
    # 22:30 del 14 en Argentina es 01:30 del 15 en UTC: tiene que contar el 14
    crear_concierto(creado_en=_en_argentina(hoy - timedelta(days=1), time(22, 30)))
    crear_concierto(creado_en=datetime(2026, 10, 15, 13, 0, tzinfo=UTC))  # 10:00 del 15 en Argentina
    crear_concierto(creado_en=_en_argentina(hoy))

    filas = repo.ingesta_por_dia(hoy, 7)

    assert len(filas) == 7
    assert filas[-1]["fecha"] == hoy
    assert [f["nuevos"] for f in filas[-2:]] == [1, 2]
    assert filas[0]["desde_que_se_mide"] == hoy - timedelta(days=1)


def test_anticipacion_por_rangos_y_mediana(hoy, crear_concierto):
    crear_concierto(fecha=hoy + timedelta(days=3), creado_en=_en_argentina(hoy))  # 3 días
    crear_concierto(fecha=hoy + timedelta(days=30), creado_en=_en_argentina(hoy))  # 30 días
    crear_concierto(fecha=hoy + timedelta(days=137), creado_en=_en_argentina(hoy))  # 137 días
    crear_concierto(
        fecha=hoy - timedelta(days=5), creado_en=_en_argentina(hoy)
    )  # encontrado después: no cuenta

    filas = repo.anticipacion(None, None)

    assert [(f["desde_dias"], f["hasta_dias"], f["cantidad"]) for f in filas] == [
        (0, 8, 1),
        (8, 31, 1),
        (31, 61, 0),
        (61, 91, 0),
        (91, None, 1),
    ]
    assert filas[0]["mediana"] == 30


# ---------- Validación ----------


@pytest.mark.parametrize("valor", ["3", "61", "muchos"])
def test_dias_invalidos(valor):
    with pytest.raises(ParametroInvalido):
        servicio.leer_dias({"dias": valor}, servicio.PROXIMOS_DIAS_DEFECTO, servicio.PROXIMOS_DIAS_MAXIMO)


def test_dias_por_defecto():
    assert servicio.leer_dias({}, servicio.PROXIMOS_DIAS_DEFECTO, servicio.PROXIMOS_DIAS_MAXIMO) == 14


# ---------- Endpoints ----------


@pytest.fixture
def hoy_fijo(monkeypatch, hoy):
    monkeypatch.setattr("app.services.metricas_service.hoy_argentina", lambda: hoy)


@pytest.mark.parametrize("endpoint", ["dia_horario", "calidad", "anticipacion"])
def test_endpoints_con_filtro(cliente, hoy_fijo, endpoint):
    respuesta = cliente.get(f"/api/metricas/{endpoint}?desde=2026-01-01")

    assert respuesta.status_code == 200
    assert respuesta.get_json()["filtro"] == {"desde": "2026-01-01", "hasta": None}
    assert respuesta.headers["Cache-Control"] == "public, max-age=300"


def test_endpoint_proximos_dias(cliente, hoy_fijo, hoy, crear_concierto):
    crear_concierto(fecha=hoy)

    cuerpo = cliente.get("/api/metricas/proximos_dias?dias=7").get_json()

    assert cuerpo["dias"][0] == {"fecha": "2026-10-15", "cantidad": 1}
    assert len(cuerpo["dias"]) == 7


def test_endpoint_ingesta(cliente, hoy_fijo, hoy, crear_concierto):
    crear_concierto(creado_en=_en_argentina(hoy))

    cuerpo = cliente.get("/api/metricas/ingesta?dias=7").get_json()

    assert cuerpo["desde_que_se_mide"] == "2026-10-15"
    assert cuerpo["dias"][-1] == {"fecha": "2026-10-15", "nuevos": 1}


def test_endpoint_anticipacion_y_resumen(cliente, hoy_fijo, hoy, crear_ubicacion, crear_concierto):
    crear_concierto(fecha=hoy + timedelta(days=10), creado_en=_en_argentina(hoy), ubicacion=crear_ubicacion())

    anticipacion = cliente.get("/api/metricas/anticipacion").get_json()
    resumen = cliente.get("/api/metricas/resumen").get_json()

    assert anticipacion["mediana_dias"] == 10.0
    assert anticipacion["rangos"][1] == {"desde_dias": 8, "hasta_dias": 31, "cantidad": 1}
    assert resumen["concentracion_top5"] == 100.0


def test_proximos_dias_rechaza_dias_invalidos(cliente):
    respuesta = cliente.get("/api/metricas/proximos_dias?dias=500")

    assert respuesta.status_code == 400
    assert respuesta.get_json() == {"error": "'dias' debe estar entre 7 y 60"}
