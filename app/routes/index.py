from flask import Blueprint

bp = Blueprint("index", __name__)


# Verificación de vida: la usan el healthcheck de Docker y el keep alive.
@bp.route("/")
def estado():
    return {"estado": "ok"}
