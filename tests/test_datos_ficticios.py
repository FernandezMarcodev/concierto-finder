"""Generador de datos ficticios y comando `flask sembrar`."""

from datetime import timedelta

from app.services.datos_ficticios import LUGARES, generar_conciertos
from app.services.geocoding_service import dentro_de_amba


def test_misma_semilla_mismos_datos(hoy):
    assert generar_conciertos(hoy, 50, 12, semilla=1) == generar_conciertos(hoy, 50, 12, semilla=1)
    assert generar_conciertos(hoy, 50, 12, semilla=1) != generar_conciertos(hoy, 50, 12, semilla=2)


def test_cantidad_fechas_y_sin_duplicados(hoy):
    conciertos = generar_conciertos(hoy, 300, meses_atras=12, semilla=42)

    assert len(conciertos) == 300
    fechas = [c["fecha"] for c in conciertos if c["fecha"] is not None]
    assert min(fechas) >= hoy - timedelta(days=360)
    assert max(fechas) <= hoy + timedelta(days=90)
    assert any(f < hoy for f in fechas) and any(f >= hoy for f in fechas)  # hay historial y vigentes
    claves = {(c["nombre"], c["artista"], c["fecha"], c["lugar"]) for c in conciertos}
    assert len(claves) == 300


def test_todos_los_lugares_estan_en_amba():
    assert all(dentro_de_amba(lat, lng) for _, lat, lng, _ in LUGARES)


def test_sembrar_guarda_los_conciertos(app, base):
    from app.repositories.concierto_repository import contar_conciertos

    resultado = app.test_cli_runner().invoke(args=["sembrar", "--cantidad", "40"])

    assert resultado.exit_code == 0, resultado.output
    assert contar_conciertos() == 40


def test_sembrar_no_mezcla_con_datos_existentes(app, crear_concierto):
    crear_concierto(nombre="Real")

    resultado = app.test_cli_runner().invoke(args=["sembrar", "--cantidad", "10"])

    assert resultado.exit_code != 0
    assert "--vaciar" in resultado.output


def test_sembrar_con_vaciar_reemplaza_los_datos(app, base, crear_concierto):
    from app.repositories.concierto_repository import contar_conciertos

    crear_concierto(nombre="Real")

    resultado = app.test_cli_runner().invoke(args=["sembrar", "--cantidad", "10", "--vaciar"])

    assert resultado.exit_code == 0, resultado.output
    assert contar_conciertos() == 10


def test_sembrar_se_niega_en_render(app, base, monkeypatch):
    monkeypatch.setenv("RENDER", "true")

    resultado = app.test_cli_runner().invoke(args=["sembrar"])

    assert resultado.exit_code != 0
    assert "producción" in resultado.output
