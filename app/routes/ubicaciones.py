from flask import Blueprint

from app.repositories.ubicacion_repository import obtener_ubicaciones
from app.schemas.ubicacion_schema import serializar_ubicacion

bp = Blueprint("ubicaciones", __name__)


@bp.route("/ubicaciones")
def listar_ubicaciones():
    return {"ubicaciones": [serializar_ubicacion(ubicacion) for ubicacion in obtener_ubicaciones()]}
