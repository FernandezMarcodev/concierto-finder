# Contrato frontend–backend

El contrato es el acuerdo entre el frontend (`web/`) y el backend (`app/`) sobre qué rutas existen,
qué parámetros aceptan y qué forma tienen sus respuestas. Tiene dos partes:

| Parte | Archivo | Para quién |
|---|---|---|
| Especificación formal | [`openapi.json`](openapi.json) (OpenAPI 3.1) | Herramientas y tests. Se puede ver navegable pegándolo en [editor.swagger.io](https://editor.swagger.io). |
| Referencia con ejemplos | [API.md](API.md) | Personas: cada endpoint con ejemplos de respuesta. |

Este documento explica las reglas del contrato y cómo se verifica.

## 1. Qué consume el frontend

El frontend solo usa estas rutas. El resto existe para operación o para otros clientes.

| Ruta | Quién la usa | Para qué | Requisitos |
|---|---|---|---|
| `GET /conciertos` | `servicios/conciertoServicio.js` → `paginas/Inicio.jsx` | Cartelera: lista, mapa y filtros (los filtros se aplican en el navegador) | RF-01 a RF-16 |
| `GET /api/metricas/resumen` | `servicios/metricasServicio.js` → `paginas/Metricas.jsx` | Indicadores | RF-29 |
| `GET /api/metricas/conciertos_por_mes` | ídem | Gráfico por mes | RF-30 |
| `GET /api/metricas/lugares?limite=10` | ídem | Ranking de lugares | RF-31 |
| `GET /api/metricas/artistas?limite=10` | ídem | Ranking de artistas | RF-31 |
| `GET /api/metricas/densidad` | ídem | Mapa de calor | RF-33 |
| `GET /api/metricas/dia_horario` | ídem | Grilla día × horario | RF-32 |
| `GET /api/metricas/proximos_dias?dias=14` | ídem | Próximos 14 días | RF-32 |
| `GET /api/metricas/calidad` | ídem | Calidad de los datos | RF-35 |
| `GET /api/metricas/ingesta?dias=30` | ídem | Conciertos nuevos por día | RF-35 |
| `GET /api/metricas/anticipacion` | ídem | Anticipación | RF-32 |

En `openapi.json`, cada operación tiene la marca `x-consumida-por-el-frontend` (`true` o `false`).

| Ruta que el frontend no usa | Quién la usa |
|---|---|
| `GET /` | Healthcheck de Docker y keep alive |
| `GET\|POST /ingestar_agendade` | Workflow de GitHub Actions (con token) |
| `GET /conciertos_cerca`, `GET /ubicaciones` | Otros clientes (RF-27) |
| `GET /api/metricas/distancias` | Otros clientes. La página dejó de mostrarla. |

## 2. Reglas que el contrato garantiza

| # | Regla | Por qué importa en el frontend |
|---|---|---|
| C-1 | Las coordenadas van siempre en orden **`[lng, lat]`** (como PostGIS). | `coordenadas[1]` es la latitud y `coordenadas[0]` la longitud. Invertirlas pone el marcador en otro continente. |
| C-2 | `fecha` es `AAAA-MM-DD` y `hora` es `HH:MM:SS`, o `null`. Son fechas de Argentina. | No usar `new Date("AAAA-MM-DD")`, que la interpreta en UTC y muestra el día anterior. |
| C-3 | Los campos opcionales llegan como `null`, nunca omitidos ni como el texto `"None"`. | El frontend puede chequear `=== null`. Por compatibilidad con versiones viejas, todavía tolera `"None"`. |
| C-4 | `ubicacion_detalle` es un objeto Ubicación completo o `null`. | Un concierto sin lugar se muestra en la lista, pero no en el mapa. |
| C-5 | Las métricas filtrables devuelven el `filtro` aplicado (`desde`, `hasta`). | El frontend puede comprobar a qué período corresponde la respuesta. |
| C-6 | Los errores son `{"error": "mensaje"}` con código 400, 401, 409 o 503. | El servicio lanza una excepción ante cualquier código de error y la página muestra su estado de error. |
| C-7 | Las respuestas de conciertos y métricas llevan `Cache-Control: public, max-age=300`. | Un dato nuevo puede tardar hasta 5 minutos en verse. |
| C-8 | Los objetos no tienen campos fuera de los documentados (`additionalProperties: false`). | Un campo nuevo obliga a actualizar el contrato a propósito. |

## 3. Cómo se cambia el contrato

- **Cambios compatibles** (agregar una ruta, un parámetro opcional o un campo nuevo): se actualiza
  `openapi.json` y `API.md` en el mismo PR que el código.
- **Cambios incompatibles** (renombrar o sacar un campo, cambiar un tipo, hacer obligatorio un
  parámetro): el backend, el frontend y el contrato se cambian en el mismo PR. Como los dos se
  despliegan juntos desde `main`, no hace falta versionar la URL (`/v2/...`). Si algún día hubiera
  clientes externos, habría que hacerlo.
- La versión del contrato (`info.version`) sigue SemVer: el número del medio sube con los cambios
  compatibles y el primero con los incompatibles.

## 4. Cómo se verifica

`tests/test_contrato_api.py` corre en CI en cada PR. Comprueba tres cosas:

1. **Cada respuesta real cumple su esquema.** Se cargan conciertos que ejercitan los casos borde (sin
   lugar, sin fecha, sin hora, pasados), se llama a cada ruta y se valida la respuesta contra
   `openapi.json`: tipos, campos obligatorios, nulos, formatos de fecha y campos de más.
2. **Los errores tienen la forma del contrato**: `400` con `{"error": ...}`.
3. **Las rutas documentadas son exactamente las que existen.** Si se agrega una ruta sin
   documentarla, o se documenta una que no existe, el test falla.

Un cuarto test comprueba que el validador detecta un contrato roto: sin él, un validador que no
valida nada haría pasar todo.

Lo que **no** se verifica automáticamente es que el frontend use los campos como dice el contrato,
porque el frontend no tiene tests. Eso se cubre con las reglas C-1 a C-4, con la revisión de cada PR
y con los casos de aceptación ([casos-de-prueba.md](casos-de-prueba.md)).
