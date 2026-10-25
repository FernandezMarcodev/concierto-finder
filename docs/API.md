# API — Concierto Finder

API REST en JSON. Base en producción: `https://concierto-finder.onrender.com`. En local: `http://localhost:8000`.

La especificación formal está en [`openapi.json`](openapi.json) (OpenAPI 3.1), y las reglas del contrato con el frontend en
[contrato-api.md](contrato-api.md). Este documento es la referencia con ejemplos.

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

Los conciertos **vigentes**: fecha de hoy (hora argentina) en adelante, o sin fecha. Los pasados
se conservan en la base como historial, pero no se devuelven. Ordenados por fecha y hora
ascendentes, con los nulos al final.

```
200 OK
Cache-Control: public, max-age=300

{ "conciertos": [ Concierto, ... ] }
```

### `GET /conciertos_cerca?lat=&lng=&km=`

Conciertos **vigentes** cuyo lugar está a `km` kilómetros o menos del punto dado (distancia geodésica, `ST_DWithin` sobre `Geography`).

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

## Métricas: `GET /api/metricas/...`

Endpoints de solo lectura sobre **todo el historial** (vigentes y pasados). Se calculan en
PostgreSQL/PostGIS: la API nunca devuelve las filas de conciertos, solo los resultados agregados.
Reglas de negocio en [REQUISITOS.md](REQUISITOS.md) (RN-08 a RN-15).

**Filtro común**, opcional: `?desde=AAAA-MM-DD&hasta=AAAA-MM-DD` (inclusivos). Lo aceptan todos salvo
`proximos_dias` e `ingesta`, que miran desde hoy y se configuran con `?dias=`.

- Sin filtro cuentan todos los conciertos, incluidos los sin fecha.
- Con filtro, solo los que tienen fecha dentro del rango.
- El rango no puede superar los 10 años.

Todas se pueden cachear 5 minutos, y las que aceptan el filtro devuelven el filtro aplicado:

```
200 OK
Cache-Control: public, max-age=300

{ "filtro": { "desde": "2026-01-01", "hasta": null }, ...datos propios del endpoint }
```

### `GET /api/metricas/resumen`

```json
{ "filtro": {...}, "total": 400, "vigentes": 86, "pasados": 314, "sin_fecha": 5,
  "lugares": 14, "artistas": 18, "primera_fecha": "2025-10-18", "ultima_fecha": "2027-01-09",
  "concentracion_top5": 62.4 }
```

`vigentes` y `pasados` se calculan con la fecha de hoy en Argentina (RN-02). `artistas` cuenta los
artistas distintos ya normalizados (RN-11). `concentracion_top5` es el porcentaje de los conciertos
con lugar que se reparte entre los 5 lugares más activos (`null` si no hay conciertos con lugar).

### `GET /api/metricas/conciertos_por_mes`

```json
{ "filtro": {...}, "meses": [ { "mes": "2026-01", "cantidad": 13 }, { "mes": "2026-02", "cantidad": 0 } ] }
```

Incluye los meses sin conciertos (con `0`), desde `desde` hasta `hasta`. Sin filtro, va del primer
al último mes con datos. Los conciertos sin fecha no se cuentan.

### `GET /api/metricas/lugares?limite=10`

```json
{ "filtro": {...}, "lugares": [ { "id": 3, "nombre": "Estadio Luna Park", "cantidad": 58 } ] }
```

Ranking de lugares por cantidad de conciertos. Los empates se ordenan por nombre. `limite`: de 1 a
50 (por defecto, 10).

### `GET /api/metricas/artistas?limite=10`

```json
{ "filtro": {...}, "artistas": [ { "artista": "Sofía Ríos", "cantidad": 36, "lugares": 13 } ] }
```

Agrupa las variantes de escritura de un mismo artista (RN-11) y muestra la más frecuente. `lugares`
es la cantidad de lugares distintos donde tocó.

### `GET /api/metricas/densidad?celda=0.005`

```json
{ "filtro": {...}, "celda": 0.005, "puntos": [ [-58.38, -34.6035, 71], [-58.4365, -34.5865, 52] ] }
```

Datos para el mapa de calor: cada punto es `[lng, lat, cantidad]`. Los lugares se acomodan en una
grilla de `celda` grados (`ST_SnapToGrid`), así los lugares muy cercanos suman juntos. `celda`: de
0,001 a 0,1 (por defecto 0,005 ≈ 500 m).

### `GET /api/metricas/distancias?lat=&lng=&rangos=0,5,10,20,40`

> La página web ya no muestra esta métrica (se reemplazó por día y horario, próximos días y
> anticipación), pero el endpoint sigue disponible.

```json
{ "filtro": {...}, "punto": [-58.3816, -34.6037],
  "rangos": [ { "desde_km": 0, "hasta_km": 5, "cantidad": 174 }, { "desde_km": 40, "hasta_km": null, "cantidad": 10 } ] }
```

- **`punto`:** sin `lat` y `lng` se usa el Obelisco. Si se envían, van los dos juntos.
- **Rangos:** son semiabiertos `[desde, hasta)`. El último no tiene tope (`hasta_km: null`).
- **`rangos`:** hasta 10 límites, crecientes y empezando en 0.
- **Distancia:** se mide en km, geodésica y en línea recta.

### `GET /api/metricas/dia_horario`

```json
{ "filtro": {...}, "celdas": [ { "dia": 5, "franja": 3, "nombre_franja": "20 a 22", "cantidad": 41 }, ... ] }
```

La grilla completa de 7 días por 5 franjas horarias (35 celdas, las vacías con `0`). `dia` sigue la
norma ISO: 1 = lunes ... 7 = domingo. Las franjas son: `Día (6 a 18)`, `18 a 20`, `20 a 22`,
`22 a 24` y `Trasnoche (0 a 6)` (RN-13). Solo cuentan los conciertos con fecha y hora.

### `GET /api/metricas/proximos_dias?dias=14`

```json
{ "dias": [ { "fecha": "2026-10-15", "cantidad": 4 }, { "fecha": "2026-10-16", "cantidad": 9 }, ... ] }
```

Los conciertos de cada uno de los próximos `dias` días desde hoy (hora argentina), incluidos los
días sin conciertos. **No usa el filtro de fechas** porque siempre mira hacia adelante. `dias`: de 7 a
60 (por defecto, 14).

### `GET /api/metricas/calidad`

```json
{ "filtro": {...}, "total": 200, "sin_fecha": 0, "sin_hora": 12, "sin_entradas": 3, "sin_ubicacion": 0 }
```

Cuántos conciertos no tienen fecha, hora, link de entradas (nulo o vacío) o lugar ubicado en el mapa.

### `GET /api/metricas/ingesta?dias=30`

```json
{ "desde_que_se_mide": "2026-10-15", "dias": [ { "fecha": "2026-10-14", "nuevos": 0 }, { "fecha": "2026-10-15", "nuevos": 12 } ] }
```

Conciertos nuevos que encontró la ingesta en cada uno de los últimos `dias` días, según
`creado_en` y en hora argentina. **No usa el filtro de fechas.** `dias`: de 7 a 90 (por defecto, 30).
`desde_que_se_mide` es el primer `creado_en` registrado (`null` si todavía no hay ninguno).

### `GET /api/metricas/anticipacion`

```json
{ "filtro": {...}, "mediana_dias": 34.0,
  "rangos": [ { "desde_dias": 0, "hasta_dias": 8, "cantidad": 5 }, ..., { "desde_dias": 91, "hasta_dias": null, "cantidad": 2 } ] }
```

Con cuántos días de anticipación se anuncian los conciertos: fecha del concierto menos fecha en que
lo encontró la ingesta (RN-14). Rangos `[0, 8)`, `[8, 31)`, `[31, 61)`, `[61, 91)` y `91 o más`.
`mediana_dias` es `null` si no hay datos.

### Errores

| Código | Cuándo | Cuerpo (ejemplo) |
|---|---|---|
| `400` | Fecha mal escrita, `desde` > `hasta`, rango de más de 10 años, `limite`/`celda`/`rangos`/`dias`/punto fuera de los valores permitidos | `{"error": "'limite' debe estar entre 1 y 50"}` |

## Errores generales

| Código | Cuándo | Cuerpo |
|---|---|---|
| `400` | Parámetros inválidos | `{"error": "Parámetros inválidos"}` |
| `404` | Ruta inexistente | Página de error por defecto de Flask. |
| `503` | Pool de conexiones a la base agotado (espera de 30 s) | `{"error": "Servidor ocupado, intentá de nuevo en unos segundos."}` |
| `500` | Error no controlado | Página de error por defecto de Flask (el detalle queda en los logs). |
