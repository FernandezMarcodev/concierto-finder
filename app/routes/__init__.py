from flask import Flask

from app.routes.conciertos import bp as conciertos_bp
from app.routes.index import bp as index_bp
from app.routes.metricas import bp as metricas_bp
from app.routes.ubicaciones import bp as ubicaciones_bp


def registrar_blueprints(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(ubicaciones_bp)
    app.register_blueprint(conciertos_bp)
    app.register_blueprint(metricas_bp)
