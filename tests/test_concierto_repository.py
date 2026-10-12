"""Consultas de conciertos contra PostGIS: vigencia, orden, búsqueda espacial y duplicados."""

from datetime import time, timedelta

from sqlalchemy import text

from app.repositories.concierto_repository import (
    eliminar_conciertos_duplicados,
    existe_concierto,
    obtener_conciertos,
    obtener_conciertos_cerca,
)


def _nombres(conciertos):
    return [c.nombre for c in conciertos]


def test_listado_excluye_pasados_pero_los_conserva_en_la_base(base, hoy, crear_concierto):
    crear_concierto(nombre="Ayer", fecha=hoy - timedelta(days=1))
    crear_concierto(nombre="Hoy", fecha=hoy)

    assert _nombres(obtener_conciertos(hoy)) == ["Hoy"]
    # El pasado sigue guardado: es el historial
    assert base.execute(text("SELECT count(*) FROM conciertos")).scalar() == 2


def test_sin_fecha_es_vigente_y_va_al_final(hoy, crear_concierto):
    crear_concierto(nombre="SinFecha", fecha=None)
    crear_concierto(nombre="Manana", fecha=hoy + timedelta(days=1))

    assert _nombres(obtener_conciertos(hoy)) == ["Manana", "SinFecha"]


def test_orden_por_fecha_y_despues_por_hora(hoy, crear_concierto):
    crear_concierto(nombre="Pasado mañana", fecha=hoy + timedelta(days=2))
    crear_concierto(nombre="Hoy 23 h", fecha=hoy, hora=time(23, 0))
    crear_concierto(nombre="Hoy 20 h", fecha=hoy, hora=time(20, 0))

    assert _nombres(obtener_conciertos(hoy)) == ["Hoy 20 h", "Hoy 23 h", "Pasado mañana"]


def test_la_vigencia_depende_del_parametro_hoy(hoy, crear_concierto):
    crear_concierto(nombre="Hoy", fecha=hoy)

    assert _nombres(obtener_conciertos(hoy + timedelta(days=1))) == []


def test_trae_la_ubicacion_en_la_misma_consulta(hoy, crear_ubicacion, crear_concierto, base):
    """joinedload: leer concierto.ubicacion_ref no debe disparar otra consulta (problema N+1)."""
    from sqlalchemy import event

    from app.extensions import db

    for i in range(3):
        crear_concierto(nombre=f"Show {i}", ubicacion=crear_ubicacion(nombre=f"Lugar {i}"))
    base.expire_all()  # que nada quede en memoria de cuando se crearon

    consultas = []

    def contar(*args):
        consultas.append(args)

    event.listen(db.engine, "before_cursor_execute", contar)
    try:
        nombres_lugares = [c.ubicacion_ref.nombre for c in obtener_conciertos(hoy)]
    finally:
        event.remove(db.engine, "before_cursor_execute", contar)

    assert sorted(nombres_lugares) == ["Lugar 0", "Lugar 1", "Lugar 2"]
    assert len(consultas) == 1


def test_cerca_filtra_por_distancia(hoy, crear_ubicacion, crear_concierto):
    obras = crear_ubicacion(nombre="Estadio Obras", lat=-34.5452, lng=-58.4472)
    la_plata = crear_ubicacion(nombre="Estadio La Plata", lat=-34.9139, lng=-57.9893)  # ≈ 58 km
    crear_concierto(nombre="En Obras", ubicacion=obras)
    crear_concierto(nombre="En La Plata", ubicacion=la_plata)

    # Desde el Obelisco (≈ 8 km de Obras)
    assert _nombres(obtener_conciertos_cerca(-34.6037, -58.3816, 10_000, hoy)) == ["En Obras"]
    assert len(obtener_conciertos_cerca(-34.6037, -58.3816, 5_000, hoy)) == 0
    assert len(obtener_conciertos_cerca(-34.6037, -58.3816, 70_000, hoy)) == 2


def test_cerca_tambien_excluye_pasados(hoy, crear_ubicacion, crear_concierto):
    obras = crear_ubicacion()
    crear_concierto(nombre="Ayer", fecha=hoy - timedelta(days=1), ubicacion=obras)

    assert obtener_conciertos_cerca(-34.5452, -58.4472, 1_000, hoy) == []


def test_existe_concierto_considera_iguales_las_fechas_nulas(crear_ubicacion, crear_concierto):
    obras = crear_ubicacion()
    crear_concierto(nombre="Gira", artista="Fito", fecha=None, ubicacion=obras)

    assert existe_concierto("Gira", "Fito", None, obras.id)
    assert not existe_concierto("Gira", "Otro", None, obras.id)


def test_eliminar_duplicados_conserva_el_de_menor_id(base, hoy, crear_ubicacion, crear_concierto):
    obras = crear_ubicacion()
    original = crear_concierto(nombre="Gira", artista="Fito", ubicacion=obras)
    crear_concierto(nombre="Gira", artista="Fito", ubicacion=obras)
    crear_concierto(nombre="Gira", artista="Fito", fecha=hoy + timedelta(days=1), ubicacion=obras)

    assert eliminar_conciertos_duplicados() == 1
    base.commit()

    ids = base.execute(text("SELECT id FROM conciertos ORDER BY id")).scalars().all()
    assert ids[0] == original.id
    assert len(ids) == 2
