import logging
import os
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from app.extensions import db
from app.models.concierto import Concierto
from app.repositories.concierto_repository import eliminar_conciertos_duplicados, eliminar_conciertos_pasados
from app.services.scraper_service import hay_ingesta_en_curso, ingestar_agendade

logger = logging.getLogger(__name__)

# Render duerme el servicio gratuito tras 15 min sin tráfico; el ping cada 12 min lo mantiene
# despierto. Solo se pingea dentro de una franja horaria (hora argentina): fuera de ella Render
# lo duerme y no gasta horas. Así las 750 h/mes del plan gratuito alcanzan para el mes entero.
INTERVALO_KEEP_ALIVE = 12 * 60  # 12 minutos
FRANJA_DESDE_DEFECTO = 9  # 9:00
FRANJA_HASTA_DEFECTO = 2  # 2:00 del día siguiente
INTERVALO_LIMPIEZA = 24 * 60 * 60  # 24 horas

# "Hoy" se calcula en hora argentina: el servidor corre en UTC y, entre las 21 y las 0 h,
# date.today() ya devolvería mañana y borraría los conciertos de esa misma noche.
ZONA_HORARIA = ZoneInfo("America/Argentina/Buenos_Aires")


def dentro_de_franja(hora, desde, hasta):
    """
    True si `hora` (0 a 23) está dentro de la franja [desde, hasta).
    La franja puede cruzar la medianoche (por ejemplo, de 9 a 2). Si desde == hasta, es todo el día.
    """
    if desde == hasta:
        return True
    if desde < hasta:
        return desde <= hora < hasta
    return hora >= desde or hora < hasta


def mantener_despierta(url, desde, hasta):
    while True:
        # Mientras corre una ingesta también se pingea, aunque sea fuera de la franja:
        # si no, Render podría dormir la instancia a mitad de camino.
        if dentro_de_franja(datetime.now(ZONA_HORARIA).hour, desde, hasta) or hay_ingesta_en_curso():
            try:
                respuesta = requests.get(url, timeout=30)
                logger.debug("Keep alive: %s", respuesta.status_code)
            except Exception as e:
                logger.warning("Error en el keep alive: %s", e)
        time.sleep(INTERVALO_KEEP_ALIVE)


def _hora_de_entorno(nombre, defecto):
    valor = os.getenv(nombre)
    if valor is None or valor.strip() == "":
        return defecto
    hora = int(valor)
    if not 0 <= hora <= 23:
        raise RuntimeError(f"{nombre} debe ser una hora entre 0 y 23 (recibido: {valor!r}).")
    return hora


def limpiar_conciertos(app):
    """Borra conciertos pasados y duplicados en dos DELETE, sin cargar filas en memoria."""
    with app.app_context():
        try:
            pasados = eliminar_conciertos_pasados(datetime.now(ZONA_HORARIA).date())
            duplicados = eliminar_conciertos_duplicados()
            db.session.commit()
            logger.info("Limpieza: %d conciertos pasados y %d duplicados eliminados", pasados, duplicados)
        except Exception:
            logger.exception("Error en la limpieza de conciertos")
            db.session.rollback()
        finally:
            db.session.remove()


def ingesta_inicial(app):
    """
    Si la base no tiene ningún concierto (primer deploy o base nueva), ejecuta la ingesta.
    Con datos ya cargados no hace nada: de eso se encarga el workflow de GitHub cada 12 h.
    """
    with app.app_context():
        try:
            if Concierto.query.first() is not None:
                return
            logger.info("La base no tiene conciertos: se ejecuta la ingesta inicial")
            ingestar_agendade()
        except Exception:
            logger.exception("Error en la ingesta inicial")
            db.session.rollback()
        finally:
            db.session.remove()


def programar_limpieza_diaria(app):
    logger.info("Iniciando cronjob para eliminar conciertos pasados y duplicados")
    while True:
        limpiar_conciertos(app)
        time.sleep(INTERVALO_LIMPIEZA)


def arrancar_tareas(app):
    """Levanta las tareas en segundo plano: keep alive, limpieza diaria e ingesta inicial."""
    # Sin KEEP_ALIVE_URL se usa RENDER_EXTERNAL_URL, que Render define solo. En local ninguna
    # existe y no se pingea nada. KEEP_ALIVE_URL vacía desactiva el ping también en Render.
    url_keep_alive = os.environ.get("KEEP_ALIVE_URL", os.getenv("RENDER_EXTERNAL_URL", ""))
    if url_keep_alive:
        desde = _hora_de_entorno("KEEP_ALIVE_DESDE", FRANJA_DESDE_DEFECTO)
        hasta = _hora_de_entorno("KEEP_ALIVE_HASTA", FRANJA_HASTA_DEFECTO)
        logger.info("Keep alive a %s entre las %d y las %d h (hora argentina)", url_keep_alive, desde, hasta)
        threading.Thread(target=mantener_despierta, args=(url_keep_alive, desde, hasta), daemon=True).start()
    threading.Thread(target=programar_limpieza_diaria, args=(app,), daemon=True).start()
    threading.Thread(target=ingesta_inicial, args=(app,), daemon=True).start()
