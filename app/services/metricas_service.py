"""
Reglas de las métricas: lee y valida los parámetros del pedido, aplica los valores por defecto y
llama al repositorio. Las rutas no validan nada y el repositorio no conoce el pedido HTTP: cada
capa tiene una sola responsabilidad.
"""

from dataclasses import dataclass
from datetime import date

from app.repositories import metricas_repository
from app.services.fechas import hoy_argentina

# Obelisco: punto de referencia por defecto para las distancias (el mismo centro que usa el mapa, RN-07)
LAT_OBELISCO = -34.6037
LNG_OBELISCO = -58.3816
RANGOS_KM_DEFECTO = [0, 5, 10, 20, 40]
MAX_RANGOS = 10

LIMITE_DEFECTO = 10
LIMITE_MAXIMO = 50

CELDA_DEFECTO = 0.005  # grados ≈ 500 m en Buenos Aires
CELDA_MINIMA = 0.001  # ≈ 100 m
CELDA_MAXIMA = 0.1  # ≈ 10 km

# Ventanas de días: próximos días (hacia adelante) e ingesta (hacia atrás)
PROXIMOS_DIAS_DEFECTO = 14
PROXIMOS_DIAS_MAXIMO = 60
INGESTA_DIAS_DEFECTO = 30
INGESTA_DIAS_MAXIMO = 90

# Evita pedidos absurdos (por ejemplo, del año 1 al 9999) que generarían miles de meses vacíos.
RANGO_MAXIMO_DIAS = 10 * 366


class ParametroInvalido(ValueError):
    """Un parámetro del pedido no es válido. La ruta lo convierte en una respuesta 400."""


@dataclass(frozen=True)
class FiltroFechas:
    desde: date | None = None
    hasta: date | None = None

    def a_dict(self):
        return {
            "desde": self.desde.isoformat() if self.desde else None,
            "hasta": self.hasta.isoformat() if self.hasta else None,
        }


# ---------- Lectura y validación de parámetros ----------


def _leer_fecha(args, nombre):
    valor = args.get(nombre)
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ParametroInvalido(f"'{nombre}' debe ser una fecha AAAA-MM-DD") from None


def leer_filtro(args) -> FiltroFechas:
    desde = _leer_fecha(args, "desde")
    hasta = _leer_fecha(args, "hasta")
    if desde and hasta:
        if desde > hasta:
            raise ParametroInvalido("'desde' no puede ser posterior a 'hasta'")
        if (hasta - desde).days > RANGO_MAXIMO_DIAS:
            raise ParametroInvalido("El rango de fechas no puede superar los 10 años")
    return FiltroFechas(desde, hasta)


def _leer_numero(args, nombre, tipo, defecto, minimo, maximo):
    valor = args.get(nombre)
    if valor is None or valor == "":
        return defecto
    try:
        numero = tipo(valor)
    except ValueError:
        raise ParametroInvalido(f"'{nombre}' debe ser un número") from None
    if not minimo <= numero <= maximo:
        raise ParametroInvalido(f"'{nombre}' debe estar entre {minimo} y {maximo}")
    return numero


def leer_limite(args):
    return _leer_numero(args, "limite", int, LIMITE_DEFECTO, 1, LIMITE_MAXIMO)


def leer_celda(args):
    return _leer_numero(args, "celda", float, CELDA_DEFECTO, CELDA_MINIMA, CELDA_MAXIMA)


def leer_dias(args, defecto, maximo):
    return _leer_numero(args, "dias", int, defecto, 7, maximo)


def leer_punto(args):
    """(lat, lng) del pedido; si no vienen, el Obelisco. Se piden los dos o ninguno."""
    if args.get("lat") is None and args.get("lng") is None:
        return LAT_OBELISCO, LNG_OBELISCO
    lat = _leer_numero(args, "lat", float, None, -90, 90)
    lng = _leer_numero(args, "lng", float, None, -180, 180)
    if lat is None or lng is None:
        raise ParametroInvalido("'lat' y 'lng' se envían juntos")
    return lat, lng


def leer_rangos(args):
    """
    Límites de los rangos de distancia, por ejemplo "0,5,10,20,40". Tienen que empezar en 0
    (para no dejar conciertos afuera) y ser crecientes.
    """
    valor = args.get("rangos")
    if not valor:
        return RANGOS_KM_DEFECTO
    try:
        limites = [float(parte) for parte in valor.split(",")]
    except ValueError:
        raise ParametroInvalido("'rangos' debe ser una lista de números separados por coma") from None
    if len(limites) > MAX_RANGOS:
        raise ParametroInvalido(f"'rangos' admite como máximo {MAX_RANGOS} límites")
    if limites[0] != 0:
        raise ParametroInvalido("'rangos' debe empezar en 0")
    if any(a >= b for a, b in zip(limites, limites[1:], strict=False)):
        raise ParametroInvalido("'rangos' debe ser estrictamente creciente")
    return limites


# ---------- Métricas ----------


def obtener_resumen(filtro: FiltroFechas):
    return metricas_repository.resumen(filtro.desde, filtro.hasta, hoy_argentina())


def obtener_conciertos_por_mes(filtro: FiltroFechas):
    return metricas_repository.conciertos_por_mes(filtro.desde, filtro.hasta)


def obtener_lugares(filtro: FiltroFechas, limite):
    return metricas_repository.lugares_mas_activos(filtro.desde, filtro.hasta, limite)


def obtener_artistas(filtro: FiltroFechas, limite):
    return metricas_repository.artistas_que_mas_se_repiten(filtro.desde, filtro.hasta, limite)


def obtener_densidad(filtro: FiltroFechas, celda):
    return metricas_repository.densidad(filtro.desde, filtro.hasta, celda)


def obtener_distancias(filtro: FiltroFechas, lat, lng, limites_km):
    return metricas_repository.distribucion_de_distancias(filtro.desde, filtro.hasta, lat, lng, limites_km)


def obtener_dia_y_horario(filtro: FiltroFechas):
    return metricas_repository.dia_y_horario(filtro.desde, filtro.hasta)


def obtener_proximos_dias(dias):
    """Hacia adelante desde hoy (hora argentina): no usa el filtro de fechas."""
    return metricas_repository.proximos_dias(hoy_argentina(), dias)


def obtener_calidad(filtro: FiltroFechas):
    return metricas_repository.calidad(filtro.desde, filtro.hasta)


def obtener_ingesta(dias):
    """Hacia atrás desde hoy (hora argentina): no usa el filtro de fechas."""
    return metricas_repository.ingesta_por_dia(hoy_argentina(), dias)


def obtener_anticipacion(filtro: FiltroFechas):
    return metricas_repository.anticipacion(filtro.desde, filtro.hasta)
