"""Serialización de las métricas a dict/JSON. Coordenadas en orden [lng, lat], como en el resto de la API."""


def _iso_o_none(valor):
    return valor.isoformat() if valor is not None else None


def serializar_resumen(fila):
    return {
        "total": fila["total"],
        "vigentes": fila["vigentes"],
        "pasados": fila["pasados"],
        "sin_fecha": fila["sin_fecha"],
        "lugares": fila["lugares"],
        "artistas": fila["artistas"],
        "primera_fecha": _iso_o_none(fila["primera_fecha"]),
        "ultima_fecha": _iso_o_none(fila["ultima_fecha"]),
    }


def serializar_mes(fila):
    return {"mes": fila["mes"], "cantidad": fila["cantidad"]}


def serializar_lugar(fila):
    return {"id": fila["id"], "nombre": fila["nombre"], "cantidad": fila["cantidad"]}


def serializar_artista(fila):
    return {"artista": fila["artista"], "cantidad": fila["cantidad"], "lugares": fila["lugares"]}


def serializar_punto_densidad(fila):
    # Lista corta [lng, lat, cantidad] en lugar de un objeto: el mapa de calor recibe cientos de puntos.
    return [round(fila["lng"], 6), round(fila["lat"], 6), fila["cantidad"]]


def serializar_rango(fila):
    return {"desde_km": fila["desde_km"], "hasta_km": fila["hasta_km"], "cantidad": fila["cantidad"]}
