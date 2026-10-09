from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.exc import TimeoutError

from app.config import Config
from app.extensions import db, migrate


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app)

    db.init_app(app)
    # Las migraciones (carpeta migrations/) necesitan los modelos registrados en el metadata.
    from app import models  # noqa: F401

    migrate.init_app(app, db)

    from app.routes import registrar_blueprints

    registrar_blueprints(app)

    @app.errorhandler(TimeoutError)
    def responder_base_ocupada(error):
        db.session.close()
        return jsonify({"error": "Servidor ocupado, intentá de nuevo en unos segundos."}), 503

    @app.teardown_appcontext
    def cerrar_sesion(error=None):
        db.session.remove()

    return app
