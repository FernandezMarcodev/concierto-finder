"""Contrato frontend-backend: las respuestas reales cumplen docs/openapi.json, y las rutas documentadas
son exactamente las que existen. Si alguien cambia un campo sin actualizar el contrato, este test falla."""

import json
import re
from datetime import time, timedelta
from pathlib import Path

import pytest

CONTRATO = json.loads((Path(__file__).parent.parent / "docs" / "openapi.json").read_text(encoding="utf-8"))
ESQUEMAS = CONTRATO["components"]["schemas"]
TIPOS = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


def errores(valor, esquema, ruta="$"):
    """Validador mínimo de JSON Schema: cubre lo que usa el contrato. Devuelve la lista de errores."""
    if "$ref" in esquema:
        return errores(valor, ESQUEMAS[esquema["$ref"].split("/")[-1]], ruta)
    if "oneOf" in esquema:
        validos = [e for e in esquema["oneOf"] if not errores(valor, e, ruta)]
        return [] if len(validos) == 1 else [f"{ruta}: {valor!r} no cumple exactamente una opción de oneOf"]

    tipo = esquema.get("type")
    if tipo == "integer" and not (isinstance(valor, int) and not isinstance(valor, bool)):
        return [f"{ruta}: se esperaba un entero y llegó {valor!r}"]
    if tipo == "number" and not (isinstance(valor, int | float) and not isinstance(valor, bool)):
        return [f"{ruta}: se esperaba un número y llegó {valor!r}"]
    if tipo in TIPOS and not isinstance(valor, TIPOS[tipo]):
        return [f"{ruta}: se esperaba {tipo} y llegó {valor!r}"]

    encontrados = []
    if "const" in esquema and valor != esquema["const"]:
        encontrados.append(f"{ruta}: se esperaba {esquema['const']!r}")
    if "pattern" in esquema and not re.search(esquema["pattern"], valor):
        encontrados.append(f"{ruta}: {valor!r} no cumple el patrón {esquema['pattern']}")
    if esquema.get("format") == "date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
        encontrados.append(f"{ruta}: {valor!r} no es una fecha AAAA-MM-DD")
    if "minimum" in esquema and valor < esquema["minimum"]:
        encontrados.append(f"{ruta}: {valor} es menor que {esquema['minimum']}")
    if "maximum" in esquema and valor > esquema["maximum"]:
        encontrados.append(f"{ruta}: {valor} es mayor que {esquema['maximum']}")

    if tipo == "object":
        faltan = set(esquema.get("required", [])) - set(valor)
        sobran = (
            set(valor) - set(esquema.get("properties", {}))
            if esquema.get("additionalProperties") is False
            else set()
        )
        encontrados += [f"{ruta}: falta el campo {campo!r}" for campo in sorted(faltan)]
        encontrados += [f"{ruta}: campo no documentado {campo!r}" for campo in sorted(sobran)]
        for campo, subesquema in esquema.get("properties", {}).items():
            if campo in valor:
                encontrados += errores(valor[campo], subesquema, f"{ruta}.{campo}")
    if tipo == "array":
        if len(valor) < esquema.get("minItems", 0) or len(valor) > esquema.get("maxItems", len(valor)):
            encontrados.append(f"{ruta}: largo {len(valor)} fuera de lo permitido")
        for i, elemento in enumerate(valor):
            encontrados += errores(elemento, esquema.get("items", {}), f"{ruta}[{i}]")
    return encontrados


def esquema_de(ruta, codigo):
    return CONTRATO["paths"][ruta]["get"]["responses"][codigo]["content"]["application/json"]["schema"]


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch, hoy):
    monkeypatch.setattr("app.routes.conciertos.hoy_argentina", lambda: hoy)


@pytest.fixture
def datos(hoy, crear_ubicacion, crear_concierto):
    """Datos que ejercitan los nulos: un concierto completo y otro sin lugar, fecha, hora ni entradas."""
    obras = crear_ubicacion()
    crear_concierto(
        nombre="Gira",
        artista="Fito",
        fecha=hoy + timedelta(days=3),
        hora=time(21),
        ubicacion=obras,
        url="https://example.com/entradas",
    )
    crear_concierto(nombre="Pasado", fecha=hoy - timedelta(days=40), hora=time(20), ubicacion=obras)
    crear_concierto(nombre="Sin datos", fecha=None)


RUTAS_GET = [
    "/",
    "/conciertos",
    "/conciertos_cerca?lat=-34.6037&lng=-58.3816&km=20",
    "/ubicaciones",
    "/api/metricas/resumen",
    "/api/metricas/conciertos_por_mes",
    "/api/metricas/lugares",
    "/api/metricas/artistas",
    "/api/metricas/densidad",
    "/api/metricas/distancias",
    "/api/metricas/dia_horario",
    "/api/metricas/proximos_dias",
    "/api/metricas/calidad",
    "/api/metricas/ingesta",
    "/api/metricas/anticipacion",
    "/api/metricas/resumen?desde=2026-01-01&hasta=2026-12-31",
]


@pytest.mark.parametrize("url", RUTAS_GET)
def test_la_respuesta_cumple_el_contrato(cliente, datos, url):
    respuesta = cliente.get(url)

    assert respuesta.status_code == 200
    assert errores(respuesta.get_json(), esquema_de(url.split("?")[0], "200")) == []


@pytest.mark.parametrize("url", ["/conciertos_cerca?lat=x", "/api/metricas/lugares?limite=0"])
def test_los_errores_cumplen_el_contrato(cliente, url):
    respuesta = cliente.get(url)

    assert respuesta.status_code == 400
    assert errores(respuesta.get_json(), esquema_de(url.split("?")[0], "400")) == []


def test_el_contrato_documenta_exactamente_las_rutas_que_existen(app):
    reales = {
        re.sub(r"<[^>]+>", "", regla.rule) for regla in app.url_map.iter_rules() if regla.endpoint != "static"
    }

    assert reales == set(CONTRATO["paths"])


def test_el_validador_detecta_un_contrato_roto():
    # Sin esto, un validador que no valida nada haría pasar todos los tests de arriba
    concierto = {
        "id": 1,
        "nombre": "x",
        "artista": "y",
        "url_evento": None,
        "ubicacion": None,
        "fecha": "15/10/2026",
        "hora": None,
        "ubicacion_detalle": None,
        "extra": 1,
    }

    encontrados = errores(concierto, {"$ref": "#/components/schemas/Concierto"})

    assert any("fecha" in e for e in encontrados)
    assert any("extra" in e for e in encontrados)
