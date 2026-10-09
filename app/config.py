import os


def variable_requerida(nombre):
    valor = os.getenv(nombre)

    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. "
            f"Copiá .env.example a .env o definila en el entorno antes de iniciar la aplicación."
        )

    return valor


class Config:
    # La conexión a PostgreSQL nunca se escribe en el código: se lee del entorno.
    SQLALCHEMY_DATABASE_URI = variable_requerida("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Token que exige /ingestar_agendade. Sin valor, el endpoint queda deshabilitado.
    SCRAPER_TOKEN = os.getenv("SCRAPER_TOKEN") or None

    # Pool chico a propósito: el plan gratuito de la base limita las conexiones.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 3,  # Máximo 3 conexiones en el pool
        "max_overflow": 2,  # Permite 2 conexiones extra temporales (total: 5)
        "pool_timeout": 30,  # Espera 30 segundos antes de error
        "pool_recycle": 1800,  # Recicla conexiones cada 30 min
        "pool_pre_ping": True,  # Verifica que la conexión esté viva antes de usarla
    }
