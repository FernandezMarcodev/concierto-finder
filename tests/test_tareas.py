"""Tareas en segundo plano: franja del keep alive, limpieza diaria y fecha argentina."""

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import text

from app.services.fechas import ZONA_HORARIA
from app.services.tareas import dentro_de_franja, limpiar_conciertos


@pytest.mark.parametrize(
    "hora, desde, hasta, esperado",
    [
        # Franja que cruza la medianoche (la de producción: de 9 a 2)
        (9, 9, 2, True),
        (23, 9, 2, True),
        (1, 9, 2, True),
        (2, 9, 2, False),  # el límite superior no se incluye
        (8, 9, 2, False),
        # Franja dentro del mismo día
        (10, 9, 17, True),
        (17, 9, 17, False),
        # desde == hasta: todo el día
        (5, 0, 0, True),
    ],
)
def test_dentro_de_franja(hora, desde, hasta, esperado):
    assert dentro_de_franja(hora, desde, hasta) is esperado


def test_limpieza_borra_duplicados_y_conserva_pasados(app, base, hoy, crear_concierto):
    # limpiar_conciertos no recibe "hoy": usa el reloj real. Por eso el concierto pasado tiene una
    # fecha que es pasada siempre (no relativa a la fecha fija de los tests).
    crear_concierto(nombre="Ayer", fecha=date(2000, 1, 1))
    crear_concierto(nombre="Doble", fecha=hoy)
    crear_concierto(nombre="Doble", fecha=hoy)

    limpiar_conciertos(app)

    nombres = base.execute(text("SELECT nombre FROM conciertos ORDER BY id")).scalars().all()
    assert nombres == ["Ayer", "Doble"]


def test_a_las_22_de_argentina_en_utc_ya_es_el_dia_siguiente():
    """Por qué "hoy" se calcula en hora argentina y no con la fecha del servidor (UTC)."""
    medianoche_utc = datetime(2026, 10, 16, 1, 0, tzinfo=UTC)  # 22:00 del 15 en Argentina

    assert medianoche_utc.date() == date(2026, 10, 16)
    assert medianoche_utc.astimezone(ZONA_HORARIA).date() == date(2026, 10, 15)
