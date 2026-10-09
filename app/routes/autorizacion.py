import hmac

from flask import current_app, request


def _token_recibido():
    """Lee el token del header "Authorization: Bearer <token>" o, si no está, del parámetro ?token=."""
    encabezado = request.headers.get("Authorization", "")
    if encabezado.startswith("Bearer "):
        return encabezado.removeprefix("Bearer ").strip()
    # Algunos servicios de cron solo permiten configurar una URL, sin headers.
    return request.args.get("token", "")


def verificar_token_ingesta():
    """
    Revisa que el pedido traiga el SCRAPER_TOKEN correcto.
    Devuelve None si está todo bien, o la respuesta de error que tiene que devolver la ruta.
    """
    token_esperado = current_app.config.get("SCRAPER_TOKEN")
    if not token_esperado:
        return {"error": "Endpoint deshabilitado: falta configurar SCRAPER_TOKEN"}, 503

    # compare_digest tarda lo mismo acierte o no, así no se puede adivinar el token midiendo tiempos.
    if not hmac.compare_digest(_token_recibido().encode(), token_esperado.encode()):
        return {"error": "No autorizado"}, 401

    return None
