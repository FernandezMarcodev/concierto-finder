"""
Coordenadas fijas de lugares de AMBA que Nominatim no encuentra con el nombre que usa la agenda.

Nominatim busca por el nombre que el lugar tiene en OpenStreetMap: "Estadio Huracán" ahí se llama
"Estadio Tomás Adolfo Ducó", y muchas salas no están cargadas. Sin esta tabla esos conciertos
se descartaban, y eran justamente los más grandes (estadios).

Cada coordenada se verificó en OpenStreetMap (por el nombre oficial o por la dirección del lugar).
La clave es "lugar, localidad" tal como la publica la agenda, normalizada con `_clave`.
Para sumar un lugar: copiar el nombre de un log "No se encontró ubicación para '...'".
"""

import unicodedata

# (latitud, longitud)
LUGARES_CONOCIDOS = {
    # Estadios (nombre oficial en OSM entre paréntesis)
    "estadio huracan, caba": (-34.64345, -58.39650),  # Estadio Tomás Adolfo Ducó
    "estadio velez sarsfield, caba": (-34.63534, -58.52068),  # Estadio José Amalfitani
    "estadio ferro carril oeste, caba": (-34.61877, -58.44784),  # Estadio Arq. Ricardo Etcheverri
    "estadio diego a. maradona, caba": (-34.60611, -58.47263),  # Argentinos Juniors
    "estadio unico diego a. maradona, la plata": (-34.91384, -57.98905),
    "estadio atenas, la plata": (-34.92546, -57.94973),  # Club Atenas
    # Microestadio de Argentinos Juniors (Gutenberg 350), la agenda usa los dos nombres
    "estadio malvinas argentinas, caba": (-34.59250, -58.47176),
    "microestadio malvinas argentinas, caba": (-34.59250, -58.47176),
    # Salas
    "mandarine park, caba": (-34.56415, -58.40217),  # Punta Carrasco, Costanera Norte
    "la trasienda, caba": (-34.61311, -58.37058),  # Balcarce 460
    "club museum, caba": (-34.61422, -58.37468),  # Perú 535
    "club temple, caba": (-34.60080, -58.39081),  # Viamonte 1666
    "teatro metro, la plata": (-34.91294, -57.94525),  # Calle 4 n.º 978
}


def _clave(nombre):
    """Minúsculas, sin tildes y sin espacios de más: 'Estadio  Huracán, CABA' -> 'estadio huracan, caba'."""
    sin_tildes = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.lower().split())


def coordenadas_conocidas(nombre_lugar):
    """(lat, lon) si el lugar está en la tabla; (None, None) si no."""
    return LUGARES_CONOCIDOS.get(_clave(nombre_lugar or ""), (None, None))
