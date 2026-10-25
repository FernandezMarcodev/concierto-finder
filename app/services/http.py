import requests

# Sin timeout, una respuesta colgada bloquea el hilo (y la conexión a la base) para siempre.
TIMEOUT_SEGUNDOS = 15

# Todos los pedidos se identifican como Concierto Finder, con un link al repo, en vez de hacerse
# pasar por un navegador: así el sitio sabe quién lo consulta y puede habilitarlo o contactarnos.
# Nominatim lo exige en su política de uso.
USER_AGENT = "ConciertoFinder/1.0 (+https://github.com/FernandezMarcodev/concierto-finder)"


def nueva_sesion(user_agent=USER_AGENT):
    """Sesión HTTP que reutiliza conexiones entre pedidos al mismo host."""
    sesion = requests.Session()
    sesion.headers["User-Agent"] = user_agent
    return sesion
