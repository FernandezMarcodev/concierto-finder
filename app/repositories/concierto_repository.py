from sqlalchemy import func, or_, text
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.concierto import Concierto
from app.models.ubicacion import Ubicacion


def _consulta_vigentes(hoy):
    """
    Conciertos vigentes con su ubicación, ordenados por fecha y hora (los sin fecha van al final).

    Los conciertos pasados se conservan en la base (historial para las métricas), pero el
    listado público muestra solo los vigentes: fecha de hoy en adelante, o sin fecha (RN-02).
    `hoy` se recibe como parámetro (y no se calcula acá) para que el resultado no dependa del reloj.
    """
    # joinedload trae la ubicación en la misma consulta (un JOIN). Sin esto, al serializar
    # cada concierto se haría una consulta extra por concierto (el problema "N+1").
    return (
        db.session.query(Concierto)
        .options(joinedload(Concierto.ubicacion_ref))
        .filter(or_(Concierto.fecha >= hoy, Concierto.fecha.is_(None)))
        .order_by(Concierto.fecha.asc().nulls_last(), Concierto.hora.asc().nulls_last(), Concierto.id)
    )


def obtener_conciertos(hoy):
    return _consulta_vigentes(hoy).all()


def obtener_conciertos_cerca(lat, lng, metros, hoy):
    """Conciertos vigentes cuyo lugar está a `metros` o menos del punto (lat, lng)."""
    punto_usuario = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)  # PostGIS usa (lng, lat)
    return (
        _consulta_vigentes(hoy)
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
