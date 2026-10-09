import logging
import os

from app import create_app
from app.services.tareas import arrancar_tareas

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = create_app()

arrancar_tareas(app)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
