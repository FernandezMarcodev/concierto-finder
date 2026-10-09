import logging
import threading
import time
from datetime import datetime

from bs4 import BeautifulSoup
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape

from app.extensions import db
from app.models.concierto import LARGO_TEXTO, Concierto
from app.models.ubicacion import Ubicacion
from app.repositories.concierto_repository import existe_concierto
from app.repositories.ubicacion_repository import buscar_ubicacion_por_nombre
from app.services.geocoding_service import dentro_de_amba, obtener_coordenadas
from app.services.http import TIMEOUT_SEGUNDOS, nueva_sesion

logger = logging.getLogger(__name__)

URL_SITIO = "https://www.agendade.com.ar"
URL_AGENDA = f"{URL_SITIO}/agenda?deb54158_page="
PAGINAS = range(1, 6)  # Paginación: páginas 1 a 5
PAUSA_ENTRE_EVENTOS = 1  # segundos, para no saturar el sitio

# Candado para que nunca corran dos ingestas a la vez (por ejemplo, la inicial al arrancar
# y la del workflow de GitHub). Si dos corrieran juntas podrían guardar el mismo concierto dos veces.
_candado_ingesta = threading.Lock()


# ---------- Descarga y parseo ----------


def _obtener_html(sesion, url):
    respuesta = sesion.get(url, timeout=TIMEOUT_SEGUNDOS)
    respuesta.raise_for_status()
    return BeautifulSoup(respuesta.content, "html.parser")


def _urls_de_eventos(soup) -> list[str] | None:
    """URLs de los eventos listados en una página de la agenda. None si la página no tiene lista."""
    lista = soup.find("div", {"fs-cmsload-element": "list", "fs-cmsfilter-element": "list"})
    if not lista:
        return None

    urls = []
    for item in lista.find_all("div", {"role": "listitem"}):
        link = item.find("a", class_="link-block-11")
        href = link.get("href") if link else None
        if href:
            urls.append(f"{URL_SITIO}{href}" if href.startswith("/") else href)
    return urls


def _parsear_evento(soup) -> dict | None:
    info_div = soup.find("div", class_="div-block-192")
    if not info_div:
        return None

    boton_compra = soup.find("a", class_="boton-comprar-entradas w-button")
    nombre_evento = info_div.get("data-event-title", "")
    artista = ""
    ubicacion = info_div.get("data-event-location", "")
    fecha = ""
    hora = ""

    for bloque in info_div.find_all("div", class_="div-block-243"):
        titulo = bloque.find("div", class_="titulo-chico")
        valor = bloque.find("div", class_="titulo-intermedio")
        if not (titulo and valor):
            continue

        titulo_texto = titulo.get_text(strip=True).upper()
        valor_texto = valor.get_text(strip=True)
        if titulo_texto in ("ARTISTA", "SHOW"):
            artista = artista or valor_texto
        elif titulo_texto == "VENUE":
            ubicacion = valor_texto
        elif titulo_texto == "UBICACIÓN":
            ubicacion = f"{ubicacion}, {valor_texto}" if ubicacion else valor_texto
        elif titulo_texto == "FECHA":
            fecha = valor_texto
        elif titulo_texto == "HORARIO":
            hora = valor_texto

    return {
        "nombre_evento": nombre_evento,
        "artista": artista or nombre_evento,
        "url_evento": boton_compra.get("href") if boton_compra else None,
        "ubicacion": ubicacion,
        "fecha": fecha,
        "hora": hora,
    }


def _parsear_fecha(texto):
    """'DD/MM/YY' (o 'DD/MM/YYYY') -> date. None si no se puede interpretar."""
    for formato in ("%d/%m/%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto.strip(), formato).date()
        except (ValueError, AttributeError):
            continue
    return None


def _parsear_hora(texto):
    """'HH:MM' o 'HH:MM:SS' -> time. None si no se puede interpretar."""
    for formato in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(texto.strip(), formato).time()
        except (ValueError, AttributeError):
            continue
    return None


def _recortar(texto):
    """Recorta el texto al largo de la columna (LARGO_TEXTO) para que el INSERT no falle."""
    if not texto:
        return texto
    return texto[:LARGO_TEXTO]


# ---------- Persistencia ----------


def _obtener_o_crear_ubicacion(nombre, descartadas):
    """
    Devuelve la Ubicacion para `nombre`, creándola con Nominatim si no existe.
    Devuelve None si no se encuentra o queda fuera de AMBA. `descartadas`
    guarda esos nombres para no repetir la geocodificación en la misma corrida.
    """
    if nombre in descartadas:
        return None

    ubicacion = buscar_ubicacion_por_nombre(nombre)
    if ubicacion:
        if ubicacion.coordenadas is not None:
            punto = to_shape(ubicacion.coordenadas)
            if not dentro_de_amba(punto.y, punto.x):
                logger.info("'%s' está fuera de AMBA", nombre)
                descartadas.add(nombre)
                return None
        return ubicacion

    lat, lon = obtener_coordenadas(nombre)
    if not (lat and lon):
        logger.info("No se encontró ubicación para '%s'", nombre)
        descartadas.add(nombre)
        return None
    # Solo se guarda lo que cae dentro de la región servida (AMBA)
    if not dentro_de_amba(lat, lon):
        logger.info("'%s' está fuera de AMBA", nombre)
        descartadas.add(nombre)
        return None

    ubicacion = Ubicacion(
        nombre=nombre,
        capacidad_total=0,
        coordenadas=WKTElement(f"POINT({lon} {lat})", srid=4326),  # primero longitud, luego latitud
        url_maps=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
    )
    db.session.add(ubicacion)
    db.session.commit()
    return ubicacion


def _guardar_concierto(evento, descartadas):
    """Guarda el evento si su lugar está en AMBA y no estaba cargado. Devuelve True si se insertó."""
    ubicacion = _obtener_o_crear_ubicacion(evento["ubicacion"], descartadas)
    if ubicacion is None:
        logger.info("No se agrega el concierto '%s'", evento["nombre_evento"])
        return False

    nombre = _recortar(evento["nombre_evento"])
    artista = _recortar(evento["artista"])
    fecha = _parsear_fecha(evento["fecha"])

    if existe_concierto(nombre, artista, fecha, ubicacion.id):
        return False

    db.session.add(
        Concierto(
            nombre=nombre,
            artista=artista,
            url_evento=evento["url_evento"],
            ubicacion=ubicacion.id,
            fecha=fecha,
            hora=_parsear_hora(evento["hora"]),
        )
    )
    db.session.commit()
    return True


# ---------- Orquestación ----------


def hay_ingesta_en_curso():
    return _candado_ingesta.locked()


def ingestar_agendade() -> list[dict] | None:
    """
    Recorre la agenda, guarda los conciertos nuevos de AMBA y devuelve todos los eventos leídos.
    Si ya hay otra ingesta corriendo no hace nada y devuelve None.
    """
    # acquire(blocking=False) toma el candado si está libre y, si no, devuelve False sin esperar.
    if not _candado_ingesta.acquire(blocking=False):
        logger.warning("Ya hay una ingesta en curso: se ignora el nuevo pedido")
        return None
    try:
        return _recorrer_agenda()
    finally:
        _candado_ingesta.release()


def _recorrer_agenda():
    sesion = nueva_sesion()
    conciertos = []
    descartadas = set()
    insertados = 0

    for pagina in PAGINAS:
        url_pagina = f"{URL_AGENDA}{pagina}"
        logger.info("Procesando página %s", url_pagina)
        try:
            urls = _urls_de_eventos(_obtener_html(sesion, url_pagina))
        except Exception:
            logger.exception("Error al obtener la página %s", url_pagina)
            break
        if urls is None:
            break

        for url_evento in urls:
            time.sleep(PAUSA_ENTRE_EVENTOS)
            try:
                evento = _parsear_evento(_obtener_html(sesion, url_evento))
                if evento is None:
                    continue
                conciertos.append(evento)
                if _guardar_concierto(evento, descartadas):
                    insertados += 1
            except Exception:
                logger.exception("Error procesando %s", url_evento)
                db.session.rollback()

    logger.info("Conciertos leídos: %d, nuevos guardados: %d", len(conciertos), insertados)
    return conciertos
