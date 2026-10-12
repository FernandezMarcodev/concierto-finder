"""
Datos ficticios para desarrollo y demos: conciertos inventados en lugares reales de AMBA.

Sirve para probar la app y las métricas en local sin depender del scraping. Los artistas son
inventados, las coordenadas de los lugares son aproximadas y todas las URLs de entradas apuntan
a example.com (dominio reservado para ejemplos): así un dato ficticio se reconoce a simple vista.

La generación es determinística: con la misma semilla y el mismo "hoy" salen los mismos datos.
"""

import random
from datetime import date, time, timedelta

from geoalchemy2 import WKTElement

from app.extensions import db
from app.models.concierto import LARGO_TEXTO, Concierto
from app.models.ubicacion import Ubicacion

# (nombre, lat, lng, peso). El peso hace que unos lugares tengan más actividad que otros,
# como pasa en la realidad (y le da sentido al ranking de venues).
LUGARES = [
    ("Niceto Club", -34.5866, -58.4363, 10),
    ("La Trastienda", -34.6127, -58.3702, 9),
    ("Teatro Gran Rex", -34.6033, -58.3786, 8),
    ("Estadio Luna Park", -34.6024, -58.3683, 8),
    ("Movistar Arena", -34.5935, -58.4480, 7),
    ("C Complejo Art Media", -34.5895, -58.4475, 6),
    ("Teatro Vorterix", -34.5745, -58.4530, 6),
    ("Estadio Obras", -34.5452, -58.4472, 5),
    ("Teatro Ópera", -34.6036, -58.3789, 5),
    ("Teatro de Flores", -34.6286, -58.4651, 4),
    ("Hipódromo de San Isidro", -34.4800, -58.5310, 2),
    ("Teatro Municipal de Morón", -34.6510, -58.6180, 2),
    ("Teatro Niní Marshall (Tigre)", -34.4210, -58.5800, 2),
    ("Estadio Único de La Plata", -34.9139, -57.9893, 2),
]

# (nombre, peso). Pocos artistas tocan mucho y muchos tocan poco.
# "Sofía Ríos" aparece también sin acentos: sirve para probar la normalización de artistas.
ARTISTAS = [
    ("Los Tranvías", 12),
    ("Mora Quintana", 10),
    ("Cuarteto Arrabal", 9),
    ("Sofía Ríos", 8),
    ("Sofia Rios", 2),
    ("La Fanfarria del Sur", 7),
    ("Bruno Salvatierra", 6),
    ("Nébula Norte", 6),
    ("Las Pibas del Delta", 5),
    ("Tomi Ferreyra", 5),
    ("Banda Bajo Cero", 4),
    ("Julieta Arce Trío", 4),
    ("Malón Eléctrico", 3),
    ("Orquesta Típica Pugliese Joven", 3),
    ("Dúo Paraná", 3),
    ("Camila Etchart", 2),
    ("Los Primos del Oeste", 2),
    ("Fermín Lagos", 2),
    ("Ruido Blanco", 1),
    ("Valentina Ocampo & Los Satélites", 1),
]

NOMBRES_DE_SHOW = [
    "Gira 2026",
    "Presentación del disco",
    "Noche acústica",
    "En vivo",
    "Aniversario",
    "Despedida",
]

# Estacionalidad aproximada: menos shows en enero y febrero (vacaciones), más en primavera.
PESO_POR_MES = {
    1: 0.5,
    2: 0.6,
    3: 1.0,
    4: 1.1,
    5: 1.1,
    6: 0.9,
    7: 0.8,
    8: 0.9,
    9: 1.1,
    10: 1.2,
    11: 1.3,
    12: 1.0,
}
# Lunes = 0 ... domingo = 6. Los viernes y sábados concentran los shows.
PESO_POR_DIA_SEMANA = {0: 0.3, 1: 0.4, 2: 0.6, 3: 1.0, 4: 1.8, 5: 2.0, 6: 0.9}

HORAS = [time(20, 0), time(21, 0), time(21, 0), time(21, 30), time(22, 0), None]  # None: hora sin confirmar
PROPORCION_SIN_FECHA = 0.03


def generar_conciertos(hoy: date, cantidad: int, meses_atras: int, semilla: int, meses_adelante: int = 3):
    """
    Genera `cantidad` conciertos como dicts (no toca la base). Las fechas van desde `meses_atras`
    meses antes de `hoy` hasta `meses_adelante` meses después, con más shows en primavera y
    los fines de semana. Algunos quedan sin fecha o sin hora, como en la fuente real.
    """
    azar = random.Random(semilla)  # generador propio: no altera el azar del resto del programa

    desde = hoy - timedelta(days=30 * meses_atras)
    hasta = hoy + timedelta(days=30 * meses_adelante)
    dias = [desde + timedelta(days=i) for i in range((hasta - desde).days + 1)]
    pesos_dias = [PESO_POR_MES[d.month] * PESO_POR_DIA_SEMANA[d.weekday()] for d in dias]

    conciertos = []
    vistos = set()  # para no generar dos veces el mismo concierto (la limpieza lo borraría)
    while len(conciertos) < cantidad:
        artista = azar.choices([a for a, _ in ARTISTAS], weights=[p for _, p in ARTISTAS])[0]
        lugar = azar.choices(LUGARES, weights=[lugar[3] for lugar in LUGARES])[0]
        fecha = None if azar.random() < PROPORCION_SIN_FECHA else azar.choices(dias, weights=pesos_dias)[0]
        nombre = f"{artista} - {azar.choice(NOMBRES_DE_SHOW)}"[:LARGO_TEXTO]

        clave = (nombre, artista, fecha, lugar[0])
        if clave in vistos:
            continue
        vistos.add(clave)

        conciertos.append(
            {
                "nombre": nombre,
                "artista": artista[:LARGO_TEXTO],
                "fecha": fecha,
                "hora": azar.choice(HORAS),
                "lugar": lugar[0],
                "url_evento": f"https://example.com/entradas/{len(conciertos) + 1}",
            }
        )
    return conciertos


def _crear_ubicaciones():
    """Crea los lugares de LUGARES que falten y devuelve un dict nombre -> Ubicacion."""
    ubicaciones = {}
    for nombre, lat, lng, _ in LUGARES:
        ubicacion = Ubicacion.query.filter_by(nombre=nombre).first()
        if ubicacion is None:
            ubicacion = Ubicacion(
                nombre=nombre,
                capacidad_total=0,
                coordenadas=WKTElement(f"POINT({lng} {lat})", srid=4326),  # primero longitud
                url_maps=f"https://www.google.com/maps/search/?api=1&query={lat},{lng}",
            )
            db.session.add(ubicacion)
        ubicaciones[nombre] = ubicacion
    db.session.flush()  # asigna los ids sin cerrar la transacción
    return ubicaciones


def sembrar(hoy: date, cantidad: int, meses_atras: int, semilla: int) -> int:
    """Guarda los conciertos ficticios en una sola transacción. Devuelve cuántos guardó."""
    ubicaciones = _crear_ubicaciones()
    for datos in generar_conciertos(hoy, cantidad, meses_atras, semilla):
        db.session.add(
            Concierto(
                nombre=datos["nombre"],
                artista=datos["artista"],
                fecha=datos["fecha"],
                hora=datos["hora"],
                url_evento=datos["url_evento"],
                ubicacion=ubicaciones[datos["lugar"]].id,
            )
        )
    db.session.commit()
    return cantidad
