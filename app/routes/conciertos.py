from flask import Blueprint, request

from app.repositories.concierto_repository import obtener_conciertos, obtener_conciertos_cerca
from app.routes.autorizacion import verificar_token_ingesta
from app.schemas.concierto_schema import serializar_concierto
from app.services.scraper_service import ingestar_agendade

bp = Blueprint("conciertos", __name__)

# Los datos cambian solo con el scraping y la limpieza diaria: se puede cachear un rato.
CACHE_CONCIERTOS = "public, max-age=300"


def _respuesta_conciertos(conciertos):
    cuerpo = {"conciertos": [serializar_concierto(concierto) for concierto in conciertos]}
    return cuerpo, 200, {"Cache-Control": CACHE_CONCIERTOS}


@bp.route("/conciertos")
def listar_conciertos():
    return _respuesta_conciertos(obtener_conciertos())


# ejemplo desde Parque Rivadavia: /conciertos_cerca?lat=-34.6183&lng=-58.4339&km=10
@bp.route("/conciertos_cerca")
def listar_conciertos_cerca():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    km = request.args.get("km", type=float)

    if lat is None or lng is None or km is None or km <= 0:
        return {"error": "Parámetros inválidos"}, 400

    # Si el pool se agota, el handler de TimeoutError en create_app responde 503.
    return _respuesta_conciertos(obtener_conciertos_cerca(lat, lng, km * 1000))


# Dispara un scraping de varios minutos que escribe en la base: requiere SCRAPER_TOKEN.
# Acepta GET para que lo puedan llamar servicios de cron externos.
@bp.route("/ingestar_agendade", methods=["GET", "POST"])
def ejecutar_ingesta():
    error = verificar_token_ingesta()
    if error:
        return error

    eventos = ingestar_agendade()
    if eventos is None:
        return {"error": "Ya hay una ingesta en curso. Intentá de nuevo cuando termine."}, 409
    return eventos
