# Arquitectura — Concierto Finder

> Documento obtenido por **ingeniería inversa** del código (octubre 2026). Los requisitos que
> esta arquitectura implementa están en [REQUISITOS.md](REQUISITOS.md); el contrato HTTP, en
> [API.md](API.md); el despliegue y la operación, en [OPERACION.md](OPERACION.md).

## 1. Vista general

Aplicación web de dos piezas, más una base geoespacial:

- **Frontend SPA** (React 18 + Vite + Leaflet) que descarga todos los conciertos una vez y
  hace el filtrado, el agrupamiento y el mapa en el navegador.
- **API REST** (Flask 3 + SQLAlchemy 2.0 + GeoAlchemy2, servida con waitress), de solo lectura
  para el público, con un endpoint protegido de ingesta (scraping) y dos tareas en segundo plano.
- **PostgreSQL 16 + PostGIS 3.4** con dos tablas.

### 1.1 Contexto (C4 nivel 1)

```mermaid
flowchart LR
    visitante([Visitante])
    operador([Operador / GitHub Actions])
    sistema[[Concierto Finder]]
    agendade[(agendade.com.ar)]
    nominatim[(Nominatim OSM)]
    tiles[(Tiles OpenStreetMap)]
    gmaps[(Google Maps)]

    visitante -- "consulta conciertos" --> sistema
    operador -- "dispara ingesta (token)" --> sistema
    sistema -- "scraping HTML" --> agendade
    sistema -- "geocodifica lugares" --> nominatim
    visitante -. "tiles del mapa" .-> tiles
    visitante -. "Cómo llegar" .-> gmaps
```

### 1.2 Contenedores (C4 nivel 2)

```mermaid
flowchart LR
    subgraph navegador[Navegador]
        spa[SPA React<br/>web/]
    end
    subgraph web[Contenedor web · nginx :5173<br/>prod: Cloudflare Pages]
        estaticos[dist/ estático]
    end
    subgraph api[Contenedor app · waitress :8000<br/>prod: Render]
        flask[API Flask<br/>app/]
        hilos[Hilos daemon<br/>keep alive · limpieza 24 h]
    end
    db[(PostgreSQL + PostGIS<br/>:5432 · host :55432)]

    estaticos -- "HTML/JS/CSS" --> spa
    spa -- "GET /conciertos (JSON)" --> flask
    flask -- "SQLAlchemy / psycopg2" --> db
    hilos -- "DELETE de duplicados (diario)" --> db
    hilos -. "ping cada 12 min (9 a 2 h)" .-> flask
```

| Contenedor | Tecnología | Producción | Local (`docker compose`) |
|---|---|---|---|
| web | React 18, Vite 7, react-leaflet 4, nginx | Cloudflare Pages (`conciertosfinder.pages.dev`) | servicio `web` en :5173 |
| app | Python 3.12, Flask 3, SQLAlchemy 2.0, GeoAlchemy2, waitress | Render (`concierto-finder.onrender.com`) | servicio `app` en :8000 |
| db | PostgreSQL 16 + PostGIS 3.4 | — | servicio `db`, volumen `pgdata`, host :55432 |

## 2. Backend (`app/`)

### 2.1 Capas

```mermaid
flowchart TD
    routes["routes/ (blueprints)<br/>index · conciertos · ubicaciones · autorizacion"]
    schemas["schemas/<br/>serializadores a dict"]
    services["services/<br/>scraper · geocoding · tareas · http"]
    repos["repositories/<br/>concierto_repository · ubicacion_repository"]
    models["models/<br/>Concierto · Ubicacion"]
    ext["extensions.py<br/>db (SQLAlchemy) · migrate (Flask-Migrate)"]

    routes --> repos
    routes --> schemas
    routes --> services
    services --> repos
    services --> models
    repos --> models
    models --> ext
```

| Módulo | Responsabilidad |
|---|---|
| `__init__.py` | `create_app()`: config, CORS, SQLAlchemy, Flask-Migrate, blueprints, 503 ante `TimeoutError` del pool, `session.remove()` al cerrar cada pedido. |
| `main.py` | Entrypoint de producción: configura `logging`, crea la app y **arranca los hilos de fondo**. |
| `config.py` | Lee `DATABASE_URL` (obligatoria, falla al importar si falta), `SCRAPER_TOKEN` y las opciones del pool. |
| `routes/` | HTTP. `autorizacion.py` define `verificar_token_ingesta()`, que la ruta de ingesta llama antes de empezar. Las rutas no contienen consultas. |
| `repositories/` | **Todas** las consultas: listados de vigentes con `joinedload` y orden por fecha, búsqueda espacial `ST_DWithin`, existencia y borrado masivo de duplicados. Las funciones de listado reciben `hoy` como parámetro. |
| `schemas/` | Serialización manual a dict/JSON (`[lng, lat]`, fechas ISO o `null`). |
| `services/scraper_service.py` | Ingesta: descarga, parseo, resolución de lugar, deduplicación y alta. |
| `services/geocoding_service.py` | Nominatim y la regla de región AMBA (fuente de verdad de los límites). |
| `services/tareas.py` | Hilos `mantener_despierta` (keep alive dentro de una franja horaria, o mientras corre una ingesta), `programar_limpieza_diaria` e `ingesta_inicial` (solo si la base está vacía). |
| `services/http.py` | `requests.Session` compartida y timeout por defecto. |
| `services/fechas.py` | `hoy_argentina()` / `ahora_argentina()`: la fecha y la hora en `America/Argentina/Buenos_Aires` (el servidor corre en UTC). |

### 2.2 Modelo de datos

```mermaid
erDiagram
    UBICACIONES ||--o{ CONCIERTOS : "aloja"
    UBICACIONES {
        int id PK
        varchar50 nombre "NOT NULL"
        int capacidad_total "NOT NULL (siempre 0)"
        geometry coordenadas "POINT SRID 4326, índice GIST"
        varchar100 url_maps
    }
    CONCIERTOS {
        int id PK
        varchar50 nombre "NOT NULL"
        varchar50 artista "NOT NULL"
        text url_evento
        int ubicacion FK "ON DELETE CASCADE, índice"
        date fecha "índice"
        time hora
    }
```

- Coordenadas en **WGS84 (SRID 4326)**, orden `[lng, lat]` en WKT y en el JSON.
- Las búsquedas por distancia castean a `Geography` para medir en metros.
- El esquema se versiona en `migrations/` (Alembic). `0001_esquema_inicial` es idempotente
  (no recrea tablas existentes); `0002_url_evento_text` amplía `url_evento` a `TEXT`;
  `0003_historial_conciertos` agrega índices sobre `conciertos.fecha` y `conciertos.ubicacion`.
- **Historial:** los conciertos pasados se conservan. "Vigente" no se guarda: se calcula en cada
  consulta con `fecha >= hoy OR fecha IS NULL` (ver D-8).

### 2.3 Concurrencia y recursos

- waitress atiende con un pool de hilos (4 por defecto). Una ingesta ocupa uno durante varios minutos.
- SQLAlchemy usa un pool de 3 conexiones + 2 de desborde, con `pool_pre_ping` y reciclado cada 30 min.
- Al importar `app.main` se levantan dos hilos daemon **por proceso**. Con varios workers
  la limpieza correría duplicada (es idempotente, así que no rompe nada).
- `flask --app app ...` (migraciones, shell) usa `create_app()` y **no** arranca los hilos.

## 3. Frontend (`web/src/`)

```mermaid
flowchart TD
    main[main.jsx] --> App[App.jsx] --> Inicio[paginas/Inicio.jsx]
    Inicio --> Encabezado & Filtros & Mapa & TarjetaGrupo & EstadoVacio & Cargando & PieDePagina
    Inicio --> servicio[servicios/conciertoServicio.js]
    Inicio --> hook[hooks/useDebounce.js]
    Inicio --> util[utilidades/<br/>filtros · grupos · geo · texto]
    Mapa --> util
    Filtros --> util
    TarjetaGrupo --> util
    util --> constantes[constantes.js]
```

**Flujo de datos de `Inicio`** (única página, sin router ni librería de estado):

```mermaid
flowchart LR
    api[/GET /conciertos/] --> base[conciertosBase<br/>estado]
    filtros[filtros<br/>estado] --> deb[useDebounce 300 ms]
    base --> f[filtrarConciertos<br/>useMemo]
    deb --> f
    f --> g[agruparPorPunto<br/>useMemo]
    g --> lista[TarjetaGrupo × N]
    g --> mapa[Mapa: marcadores AMBA]
    seleccion[seleccion<br/>estado] --> mapa
    seleccion --> lista
```

- El estado se reduce a lo mínimo (`conciertosBase`, `filtros`, `seleccion`, `cargando`, `error`);
  la lista filtrada y los grupos se **derivan**, no se guardan.
- `Mapa` recibe los grupos ya calculados, usa un único `divIcon` y abre los popups mediante
  refs de `Marker`. Cada clic en "Ver en mapa" crea un objeto `seleccion` nuevo, así vuelve a
  enfocar aunque sea el mismo concierto.
- Estilos: CSS Modules co-ubicados (`<nombre>.module.css`) y variables globales en `index.css`.
- `VITE_API_URL` se fija en el build. Si falta, se usa la API de producción.

## 4. Flujos principales

### 4.1 Carga de la página

```mermaid
sequenceDiagram
    participant N as Navegador
    participant W as Frontend (estático)
    participant A as API
    participant D as PostGIS
    N->>W: GET /
    W-->>N: index.html + assets
    N->>A: GET /conciertos
    A->>D: SELECT conciertos LEFT JOIN ubicaciones<br/>WHERE fecha >= hoy OR fecha IS NULL ORDER BY fecha, hora
    D-->>A: filas
    A-->>N: 200 {conciertos:[...]} (Cache-Control 300 s)
    Note over N: filtra, agrupa y dibuja localmente.<br/>Los filtros no vuelven a llamar a la API.
```

### 4.2 Ingesta

```mermaid
sequenceDiagram
    participant O as GitHub Actions (cada 12 h)
    participant A as API
    participant S as agendade.com.ar
    participant G as Nominatim
    participant D as PostGIS
    O->>A: GET /ingestar_agendade (Bearer token)
    A->>A: verificar_token_ingesta (401/503 si falla)
    loop páginas 1..5 (corta si no hay lista)
        A->>S: GET agenda?page=n
        loop cada evento (pausa de 1 s)
            A->>S: GET evento
            A->>D: ¿lugar por nombre (ILIKE)?
            alt no existe
                A->>G: buscar nombre
                A->>A: ¿dentro de AMBA?
                A->>D: INSERT ubicacion (commit)
            end
            A->>D: ¿existe el concierto?
            A->>D: INSERT concierto (commit)
        end
    end
    A-->>O: 200 [eventos leídos]
```

Los errores de un evento se loguean, se hace rollback y se sigue con el siguiente. Un error al
bajar una página de la agenda corta la corrida.

### 4.3 Limpieza diaria

Hilo `programar_limpieza_diaria`: al arrancar y luego cada 24 h ejecuta, en una transacción, un
`DELETE` de los duplicados (cuando hay otro con menor id y la misma identidad). Los conciertos
pasados **no** se borran: son el historial.

## 5. Decisiones de diseño

| # | Decisión | Motivo | Consecuencia |
|---|---|---|---|
| D-1 | Filtrado en el cliente | Volumen chico. Respuesta instantánea y menos carga sobre una API gratuita que se duerme. | `/conciertos_cerca` queda sin uso; no escala a decenas de miles de eventos. |
| D-2 | PostGIS para coordenadas | Consultas espaciales nativas (`ST_DWithin`). | Requiere la extensión; los datos se guardan en un tipo geográfico real. |
| D-3 | Scraping en vez de API de terceros | La fuente no ofrece API. | Frágil ante cambios de HTML. |
| D-4 | Tareas en hilos del mismo proceso | Sin infraestructura extra (sin Celery ni cron del sistema). | Se duplican por worker; se pierden si el proceso se reinicia antes de las 24 h (la limpieza corre al arrancar). |
| D-5 | Serialización manual | Dos entidades; no justifica marshmallow. | Hay que mantener los serializadores a mano. |
| D-6 | Ingesta protegida con token compartido | Simple y compatible con crons que solo configuran una URL (`?token=`). | El token en la query puede quedar en los logs de proxies; se prefiere el header. |
| D-7 | Migraciones con Alembic y base idempotente | Versionar el esquema sin romper las bases creadas con `create_all()`. | Los cambios de modelo requieren `flask db migrate` y revisar el script. |
| D-8 | Historial con **vigencia derivada de la fecha** (en lugar de una tabla de archivados o una columna `estado`) | La regla de vigencia (RN-02) ya depende solo de la fecha: guardarla aparte duplicaría el dato y obligaría a un job que la mantenga al día. Una tabla de archivados duplicaría el esquema y haría que cada métrica necesite un `UNION`. | Todas las consultas públicas deben filtrar por fecha (está centralizado en `_consulta_vigentes`). La tabla crece sin límite: por eso los índices de la `0003`. |
| D-9 | Tests contra **PostGIS real** (contenedor descartable) en lugar de SQLite o mocks | Las consultas usan PostGIS (`ST_DWithin`, `Geography`) e `IS NOT DISTINCT FROM`: SQLite no las tiene, y un mock no prueba el SQL. El esquema se crea con las migraciones, así también quedan probadas. | Los tests necesitan Docker (o un PostgreSQL con PostGIS). Son algo más lentos que en memoria (≈ 2 s para toda la suite). |

## 6. Deuda técnica y evolución sugerida

- Tests: ya hay tests de repositorios, rutas, tareas, parseo y migraciones contra PostGIS (`tests/`). Faltan el recorrido del scraper con HTML de ejemplo, las utilidades del frontend y correrlos en CI.
- Ampliar `ubicaciones.nombre` (50 caracteres) y matchear lugares por nombre exacto o normalizado en lugar de `ILIKE %x%`.
- Correr la ingesta fuera del pedido HTTP (cola o job programado), para no ocupar un hilo de waitress durante minutos.
- Unificar la ubicación de los límites de AMBA (por ejemplo, exponerlos por la API) para no mantenerlos duplicados.
