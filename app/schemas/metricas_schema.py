"""Serialización de las métricas a dict/JSON. Coordenadas en orden [lng, lat], como en el resto de la API."""


def _iso_o_none(valor):
    return valor.isoformat() if valor is not None else None


def _numero_o_none(valor):
    # round() de PostgreSQL devuelve Decimal, que JSON no sabe serializar
    return float(valor) if valor is not None else None


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
        # Porcentaje de los conciertos con lugar que se reparte entre los 5 lugares más activos
        "concentracion_top5": _numero_o_none(fila["concentracion_top5"]),
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


def serializar_celda_dia_horario(fila):
    return {
        "dia": fila["dia"],  # 1 = lunes ... 7 = domingo (ISO)
        "franja": fila["franja"],
        "nombre_franja": fila["nombre_franja"],
        "cantidad": fila["cantidad"],
    }


def serializar_dia(fila):
    return {"fecha": fila["fecha"].isoformat(), "cantidad": fila["cantidad"]}


def serializar_calidad(fila):
    return {
        "total": fila["total"],
        "sin_fecha": fila["sin_fecha"],
        "sin_hora": fila["sin_hora"],
        "sin_entradas": fila["sin_entradas"],
        "sin_ubicacion": fila["sin_ubicacion"],
    }


def serializar_ingesta(filas):
    return {
        "desde_que_se_mide": _iso_o_none(filas[0]["desde_que_se_mide"]) if filas else None,
        "dias": [{"fecha": f["fecha"].isoformat(), "nuevos": f["nuevos"]} for f in filas],
    }


def serializar_anticipacion(filas):
    return {
        "mediana_dias": _numero_o_none(filas[0]["mediana"]) if filas else None,
        "rangos": [
            {"desde_dias": f["desde_dias"], "hasta_dias": f["hasta_dias"], "cantidad": f["cantidad"]}
            for f in filas
        ],
    }
