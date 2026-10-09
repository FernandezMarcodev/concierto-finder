from geoalchemy2.shape import to_shape


def serializar_ubicacion(ubicacion):
    if ubicacion is None:
        return None

    coordenadas = None
    if ubicacion.coordenadas is not None:
        punto = to_shape(ubicacion.coordenadas)
        coordenadas = [punto.x, punto.y]  # [lng, lat]

    return {
        "id": ubicacion.id,
        "nombre": ubicacion.nombre,
        "capacidad_total": ubicacion.capacidad_total,
        "coordenadas": coordenadas,
        "url_maps": ubicacion.url_maps,
    }
