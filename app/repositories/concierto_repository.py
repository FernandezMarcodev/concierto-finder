from sqlalchemy import func, text
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.concierto import Concierto
from app.models.ubicacion import Ubicacion


def _consulta_con_ubicacion():
    """Conciertos con su ubicación, ordenados por fecha y hora (los que no tienen fecha van al final)."""
    # joinedload trae la ubicación en la misma consulta (un JOIN). Sin esto, al serializar
    # cada concierto se haría una consulta extra por concierto (el problema "N+1").
    return (
        db.session.query(Concierto)
        .options(joinedload(Concierto.ubicacion_ref))
        .order_by(Concierto.fecha.asc().nulls_last(), Concierto.hora.asc().nulls_last(), Concierto.id)
    )


def obtener_conciertos():
    return _consulta_con_ubicacion().all()


def obtener_conciertos_cerca(lat, lng, metros):
    """Conciertos cuyo lugar está a `metros` o menos del punto (lat, lng)."""
    punto_usuario = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)  # PostGIS usa (lng, lat)
    return (
        _consulta_con_ubicacion()
        .join(Ubicacion, Concierto.ubicacion == Ubicacion.id)
        # Se pasa a Geography para que la distancia se mida en metros y no en grados
        .filter(func.ST_DWithin(func.Geography(Ubicacion.coordenadas), func.Geography(punto_usuario), metros))
        .all()
    )


def existe_concierto(nombre, artista, fecha, ubicacion_id):
    """True si ya hay un concierto con el mismo nombre, artista, fecha y lugar."""
    concierto = Concierto.query.filter(
        Concierto.nombre == nombre,
        Concierto.artista == artista,
        # IS NOT DISTINCT FROM es un "==" que además considera iguales dos NULL
        # (con "==" una fecha nula nunca sería igual a otra fecha nula).
        Concierto.fecha.is_not_distinct_from(fecha),
        Concierto.ubicacion.is_not_distinct_from(ubicacion_id),
    ).first()
    return concierto is not None


def eliminar_conciertos_pasados(hoy):
    """Borra los conciertos con fecha anterior a `hoy`. Devuelve cuántos borró."""
    return Concierto.query.filter(Concierto.fecha < hoy).delete(synchronize_session=False)


# Para cada par de conciertos iguales (a y b), borra el de id más grande y deja el más viejo.
SQL_ELIMINAR_DUPLICADOS = text("""
    DELETE FROM conciertos AS a
    USING conciertos AS b
    WHERE a.id > b.id
      AND a.nombre = b.nombre
      AND a.artista = b.artista
      AND a.fecha IS NOT DISTINCT FROM b.fecha
      AND a.ubicacion IS NOT DISTINCT FROM b.ubicacion
""")


def eliminar_conciertos_duplicados():
    """Borra los conciertos repetidos (mismo nombre, artista, fecha y lugar). Devuelve cuántos borró."""
    return db.session.execute(SQL_ELIMINAR_DUPLICADOS).rowcount
