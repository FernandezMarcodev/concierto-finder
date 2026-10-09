# API — Concierto Finder

API REST en JSON. Base en producción: `https://concierto-finder.onrender.com`. En local: `http://localhost:8000`.

- CORS habilitado para cualquier origen.
- Sin autenticación, salvo la ingesta (token).
- Coordenadas siempre como `[lng, lat]` (WGS84).

## Objetos

### Concierto

```json
{
  "id": 42,
  "nombre": "Gira 2026",
  "artista": "Fito Páez",
  "url_evento": "https://www.ticketera.com/evento/...",
  "ubicacion": 7,
  "fecha": "2026-10-05",
  "hora": "21:00:00",
  "ubicacion_detalle": { "...": "Ubicación (ver abajo) o null" }
}
```

| Campo | Tipo | Notas |
|---|---|---|
| `fecha` | `string \| null` | ISO `YYYY-MM-DD`. Interpretarla como fecha local (no con `new Date(fecha)`, que usa UTC). |
| `hora` | `string \| null` | ISO `HH:MM:SS`. |
| `url_evento` | `string \| null` | URL de compra de entradas. |
| `ubicacion` | `int \| null` | id de la ubicación. |
| `ubicacion_detalle` | `object \| null` | Ubicación embebida. |

> Las versiones anteriores de la API enviaban los nulos de `fecha`, `hora` y
> `ubicacion_detalle` como el texto `"None"` o como un objeto con todos los campos en `null`.

### Ubicación

```json
{
  "id": 7,
  "nombre": "Estadio Obras",
  "capacidad_total": 0,
  "coordenadas": [-58.4472, -34.5452],
  "url_maps": "https://www.google.com/maps/search/?api=1&query=-34.5452,-58.4472"
}
```

`coordenadas` puede ser `null`. `capacidad_total` hoy siempre vale 0.

## Endpoints

### `GET /`

Verificación de vida (la usan el healthcheck de Docker y el keep alive).
Responde `200` con `{"estado": "ok"}`.

### `GET /conciertos`

Todos los conciertos guardados (los pasados se borran a diario), ordenados por fecha y hora
ascendentes, con los nulos al final.

```
200 OK
Cache-Control: public, max-age=300

{ "conciertos": [ Concierto, ... ] }
```

### `GET /conciertos_cerca?lat=&lng=&km=`

Conciertos cuyo lugar está a `km` kilómetros o menos del punto dado (distancia geodésica, `ST_DWithin` sobre `Geography`).

| Parámetro | Tipo | Requerido |
|---|---|---|
| `lat` | float | sí |
| `lng` | float | sí |
| `km` | float > 0 | sí |

```
GET /conciertos_cerca?lat=-34.6183&lng=-58.4339&km=10

200 OK → { "conciertos": [ Concierto, ... ] }   (mismo orden y caché que /conciertos)
400    → { "error": "Parámetros inválidos" }
```

### `GET /ubicaciones`

Todos los lugares registrados, ordenados por nombre.

```
200 OK → { "ubicaciones": [ Ubicación, ... ] }
```

### `GET | POST /ingestar_agendade`

Ejecuta la ingesta desde agendade.com.ar (tarda varios minutos: 1 s por evento más la
geocodificación). **Requiere token**, enviado de una de estas dos formas:

- Header `Authorization: Bearer <SCRAPER_TOKEN>` (preferido).
- Parámetro `?token=<SCRAPER_TOKEN>` (para crons que solo permiten configurar una URL).

```bash
curl -X POST -H "Authorization: Bearer $SCRAPER_TOKEN" \
     https://concierto-finder.onrender.com/ingestar_agendade
```

| Código | Cuerpo |
|---|---|
| `200` | Lista de **eventos leídos** (no solo los guardados): `[{"nombre_evento", "artista", "url_evento", "ubicacion", "fecha", "hora"}]`, con fecha y hora en el formato de la fuente (`DD/MM/AA`, `HH:MM`). |
| `401` | `{"error": "No autorizado"}`: token ausente o incorrecto. |
| `409` | `{"error": "Ya hay una ingesta en curso. ..."}`: nunca corren dos ingestas a la vez (por ejemplo, la inicial tras un deploy y la del workflow). |
| `503` | `{"error": "Endpoint deshabilitado: falta configurar SCRAPER_TOKEN"}` |

## Errores generales

| Código | Cuándo | Cuerpo |
|---|---|---|
| `400` | Parámetros inválidos | `{"error": "Parámetros inválidos"}` |
| `503` | Pool de conexiones a la base agotado (espera de 30 s) | `{"error": "Servidor ocupado, intenta nuevamente en unos segundos."}` |
| `500` | Error no controlado | Página de error por defecto de Flask (el detalle queda en los logs). |
