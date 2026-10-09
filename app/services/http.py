import requests

# Sin timeout, una respuesta colgada bloquea el hilo (y la conexión a la base) para siempre.
TIMEOUT_SEGUNDOS = 15

USER_AGENT_NAVEGADOR = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)


def nueva_sesion(user_agent=USER_AGENT_NAVEGADOR):
    """Sesión HTTP que reutiliza conexiones entre pedidos al mismo host."""
    sesion = requests.Session()
    sesion.headers["User-Agent"] = user_agent
    return sesion
