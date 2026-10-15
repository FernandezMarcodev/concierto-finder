"""
Endpoints de métricas, de solo lectura: /api/metricas/...
Todos aceptan ?desde=AAAA-MM-DD&hasta=AAAA-MM-DD (opcionales) y devuelven el filtro aplicado.
"""

from flask import Blueprint, request

from app.schemas import metricas_schema as esquema
from app.services import metricas_service as servicio
from app.services.metricas_service import ParametroInvalido

bp = Blueprint("metricas", __name__, url_prefix="/api/metricas")

# Las métricas cambian solo con la ingesta (cada 12 h): se pueden cachear igual que /conciertos.
CACHE_METRICAS = "public, max-age=300"


@bp.errorhandler(ParametroInvalido)
def responder_parametro_invalido(error):
    return {"error": str(error)}, 400


def _respuesta(filtro, **datos):
    return {"filtro": filtro.a_dict(), **datos}, 200, {"Cache-Control": CACHE_METRICAS}


@bp.route("/resumen")
def resumen():
    filtro = servicio.leer_filtro(request.args)
    return _respuesta(filtro, **esquema.serializar_resumen(servicio.obtener_resumen(filtro)))


@bp.route("/conciertos_por_mes")
def conciertos_por_mes():
    filtro = servicio.leer_filtro(request.args)
    meses = servicio.obtener_conciertos_por_mes(filtro)
    return _respuesta(filtro, meses=[esquema.serializar_mes(m) for m in meses])


@bp.route("/lugares")
def lugares():
    filtro = servicio.leer_filtro(request.args)
    filas = servicio.obtener_lugares(filtro, servicio.leer_limite(request.args))
    return _respuesta(filtro, lugares=[esquema.serializar_lugar(f) for f in filas])


@bp.route("/artistas")
def artistas():
    filtro = servicio.leer_filtro(request.args)
    filas = servicio.obtener_artistas(filtro, servicio.leer_limite(request.args))
    return _respuesta(filtro, artistas=[esquema.serializar_artista(f) for f in filas])


@bp.route("/densidad")
def densidad():
    filtro = servicio.leer_filtro(request.args)
    celda = servicio.leer_celda(request.args)
    puntos = servicio.obtener_densidad(filtro, celda)
    return _respuesta(filtro, celda=celda, puntos=[esquema.serializar_punto_densidad(p) for p in puntos])


@bp.route("/distancias")
def distancias():
    filtro = servicio.leer_filtro(request.args)
    lat, lng = servicio.leer_punto(request.args)
    limites = servicio.leer_rangos(request.args)
    rangos = servicio.obtener_distancias(filtro, lat, lng, limites)
    return _respuesta(filtro, punto=[lng, lat], rangos=[esquema.serializar_rango(r) for r in rangos])


@bp.route("/dia_horario")
def dia_horario():
    filtro = servicio.leer_filtro(request.args)
    celdas = servicio.obtener_dia_y_horario(filtro)
    return _respuesta(filtro, celdas=[esquema.serializar_celda_dia_horario(c) for c in celdas])


@bp.route("/calidad")
def calidad():
    filtro = servicio.leer_filtro(request.args)
    return _respuesta(filtro, **esquema.serializar_calidad(servicio.obtener_calidad(filtro)))


@bp.route("/anticipacion")
def anticipacion():
    filtro = servicio.leer_filtro(request.args)
    return _respuesta(filtro, **esquema.serializar_anticipacion(servicio.obtener_anticipacion(filtro)))


# Estas dos miran desde hoy (hacia adelante o hacia atrás) y no usan el filtro de fechas: se
# configuran con ?dias=.
@bp.route("/proximos_dias")
def proximos_dias():
    dias = servicio.leer_dias(request.args, servicio.PROXIMOS_DIAS_DEFECTO, servicio.PROXIMOS_DIAS_MAXIMO)
    filas = servicio.obtener_proximos_dias(dias)
    return {"dias": [esquema.serializar_dia(f) for f in filas]}, 200, {"Cache-Control": CACHE_METRICAS}


@bp.route("/ingesta")
def ingesta():
    dias = servicio.leer_dias(request.args, servicio.INGESTA_DIAS_DEFECTO, servicio.INGESTA_DIAS_MAXIMO)
    return esquema.serializar_ingesta(servicio.obtener_ingesta(dias)), 200, {"Cache-Control": CACHE_METRICAS}
