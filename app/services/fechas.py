from datetime import date, datetime
from zoneinfo import ZoneInfo

# "Hoy" se calcula en hora argentina: el servidor corre en UTC y, entre las 21 y las 0 h,
# date.today() ya devolvería mañana y ocultaría los conciertos de esa misma noche.
ZONA_HORARIA = ZoneInfo("America/Argentina/Buenos_Aires")


def ahora_argentina() -> datetime:
    return datetime.now(ZONA_HORARIA)


def hoy_argentina() -> date:
    return ahora_argentina().date()
