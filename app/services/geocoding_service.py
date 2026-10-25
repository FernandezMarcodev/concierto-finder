import logging

from app.services.http import TIMEOUT_SEGUNDOS, nueva_sesion
from app.services.lugares_conocidos import coordenadas_conocidas

logger = logging.getLogger(__name__)

# Región que cubre la aplicación: Buenos Aires y alrededores (AMBA).
# Estos límites son la fuente de verdad para lo que se ingiere en la base y
# deben coincidir con los que aplica el mapa del frontend
# (web/src/constantes.js).
AMBA_MIN_LAT = -35.15
AMBA_MAX_LAT = -34.2
AMBA_MIN_LNG = -58.95
AMBA_MAX_LNG = -57.7

URL_NOMINATIM = "https://nominatim.openstreetmap.org/search"

# La política de uso de Nominatim pide un User-Agent que identifique a la aplicación (el de nueva_sesion).
_sesion = nueva_sesion()


def dentro_de_amba(lat, lon):
    """Devuelve True si las coordenadas caen dentro de la región servida (AMBA)."""
    if lat is None or lon is None:
        return False

    return AMBA_MIN_LAT <= float(lat) <= AMBA_MAX_LAT and AMBA_MIN_LNG <= float(lon) <= AMBA_MAX_LNG


def obtener_coordenadas(nombre_lugar):
    """
    Obtiene (lat, lon) de un lugar. Devuelve (None, None) si no hay resultado.
    Primero mira la tabla de lugares conocidos y, si no está, consulta Nominatim (OpenStreetMap).
    """
    lat, lon = coordenadas_conocidas(nombre_lugar)
    if lat is not None:
        return lat, lon

    # countrycodes=ar: sin esto, "Centro Cultural, San Isidro" puede caer en otro país.
    # No se limita la búsqueda al recuadro de AMBA (bounded=1) porque Nominatim devuelve
    # cualquier coincidencia parcial adentro: "Teatro Mendoza, Mendoza" daba un teatro de la calle Mendoza.
    params = {"q": nombre_lugar, "format": "json", "limit": 1, "countrycodes": "ar"}

    try:
        respuesta = _sesion.get(URL_NOMINATIM, params=params, timeout=TIMEOUT_SEGUNDOS)
        respuesta.raise_for_status()
        resultados = respuesta.json()
    except Exception:
        logger.exception("Error al obtener coordenadas para %r", nombre_lugar)
        return None, None

    if not resultados:
        return None, None

    return resultados[0]["lat"], resultados[0]["lon"]
