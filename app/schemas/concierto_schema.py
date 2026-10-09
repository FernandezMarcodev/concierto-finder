from app.schemas.ubicacion_schema import serializar_ubicacion


def _iso_o_none(valor):
    return valor.isoformat() if valor is not None else None


def serializar_concierto(concierto):
    return {
        "id": concierto.id,
        "nombre": concierto.nombre,
        "artista": concierto.artista,
        "url_evento": concierto.url_evento,
        "ubicacion": concierto.ubicacion,
        "fecha": _iso_o_none(concierto.fecha),  # "YYYY-MM-DD" o null
        "hora": _iso_o_none(concierto.hora),  # "HH:MM:SS" o null
        "ubicacion_detalle": serializar_ubicacion(concierto.ubicacion_ref),
    }
