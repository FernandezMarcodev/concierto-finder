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
