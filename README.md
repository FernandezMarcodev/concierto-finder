# ConciertosFinder

[![CI](https://github.com/FernandezMarcodev/concierto-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/FernandezMarcodev/concierto-finder/actions/workflows/ci.yml)

Cartelera de próximos conciertos en Buenos Aires y alrededores (AMBA), con una página de métricas
sobre el historial de conciertos.

- **Conciertos:** lista y mapa, filtros por artista y por cercanía, enlaces a las entradas y a cómo llegar.
- **Métricas:** próximos 14 días, días y horarios con más conciertos, anticipación de los anuncios,
  conciertos por mes, lugares y artistas que más se repiten, mapa de calor y calidad de los datos,
  con filtro por período.

API en Flask + SQLAlchemy + PostGIS y frontend en React + Vite + Leaflet.

- Web: https://conciertosfinder.pages.dev/ · Métricas: https://conciertosfinder.pages.dev/metricas
- API: https://concierto-finder.onrender.com/

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, Flask 3, SQLAlchemy 2.0, GeoAlchemy2, Alembic (Flask-Migrate), waitress |
| Base de datos | PostgreSQL 16 + PostGIS 3.4 |
| Frontend | React 18, Vite 7, react-router, react-leaflet + leaflet.heat, Recharts |
| Calidad | pytest (contra PostGIS real), Ruff, ESLint, Prettier, GitHub Actions |
| Despliegue | Render (API, Docker), Cloudflare Pages (web), GitHub Actions (ingesta cada 12 h) |

## Decisiones técnicas destacadas

- **Historial sin columna de estado.** Los conciertos pasados se conservan para las métricas. Que
  un concierto sea "vigente" se deriva de su fecha en cada consulta, sin un estado que haya que
  mantener sincronizado (D-8).
- **Métricas calculadas en la base.** Cada métrica es una sola consulta SQL/PostGIS (`GROUP BY`,
  `generate_series`, `ST_SnapToGrid`, `ST_Distance` sobre `Geography`) y a la API solo llegan
  resultados agregados (D-10).
- **Tests contra PostGIS real**, no SQLite ni mocks, con el esquema creado por las migraciones.
  Corren en cada PR con GitHub Actions (D-9).
- **Capas:** rutas → servicios → repositorios → modelos. Todo el SQL vive en los repositorios.

El detalle de cada decisión, con sus alternativas, está en [ARQUITECTURA.md](docs/ARQUITECTURA.md) §5.

## Documentación

| Documento | Contenido |
|---|---|
| [REQUISITOS.md](docs/REQUISITOS.md) | Alcance, actores, requisitos funcionales y no funcionales, reglas de negocio y limitaciones. |
| [ARQUITECTURA.md](docs/ARQUITECTURA.md) | Vistas C4, capas, modelo de datos, flujos, decisiones y deuda técnica. |
| [API.md](docs/API.md) | Endpoints, formatos y códigos de error. |
| [OPERACION.md](docs/OPERACION.md) | Variables de entorno, entorno local, migraciones, despliegue, ingesta, tests y CI. |
| [PLAN.md](docs/PLAN.md) | Cómo trabajamos con ramas y PRs, y la hoja de ruta de features, una rama por feature. |
| [Análisis funcional](docs/analisis-funcional.md) | Relevamiento documental, proceso de ingesta en BPMN, DER y casos de prueba de aceptación ejecutados sobre la app publicada. |

## Estructura

```text
ConciertosFinder/
├── app/                        # Backend (paquete Python)
│   ├── __init__.py             # create_app()
│   ├── main.py                 # Entrypoint: logging, app y tareas en background
│   ├── cli.py                  # flask sembrar: datos ficticios para desarrollo
│   ├── config.py               # Configuración leída de variables de entorno
│   ├── extensions.py           # SQLAlchemy y Flask-Migrate
│   ├── models/                 # Concierto, Ubicacion
│   ├── repositories/           # Todas las consultas (conciertos, ubicaciones, métricas)
│   ├── schemas/                # Serialización de las respuestas
│   ├── routes/                 # Blueprints (conciertos, ubicaciones, /api/metricas) y token de ingesta
│   └── services/               # Scraper, geocodificación, tareas, métricas, fechas, datos ficticios
├── tests/                      # pytest contra PostGIS: repositorios, rutas, métricas, migraciones
├── migrations/                 # Migraciones de Alembic
├── docs/                       # Requisitos, arquitectura, API, operación, plan y análisis funcional
├── web/                        # Frontend (React + Vite + Leaflet)
│   └── src/
│       ├── paginas/            # Inicio (conciertos) y Metricas
│       ├── componentes/        # <Nombre>/<Nombre>.jsx + <nombre>.module.css
│       ├── hooks/              # useDebounce, useTema, useTemaActual, useDemorado
│       ├── servicios/          # Clientes de la API (conciertos y métricas)
│       ├── utilidades/         # filtros, grupos, geo, texto, fechas, períodos, contraste
│       └── constantes.js
├── .github/workflows/          # ci.yml (lints, tests y build) e ingesta.yml (ingesta cada 12 h)
├── Dockerfile                  # Imagen de la API (aplica migraciones al iniciar)
├── Dockerfile.test             # Imagen para correr los tests
├── docker-compose.yml          # db (PostGIS) + app + web (nginx)
├── docker-compose.test.yml     # PostGIS descartable + pytest
├── requirements.txt            # Dependencias fijadas (requirements-dev.txt suma Ruff y pytest)
├── pyproject.toml              # Configuración de Ruff y pytest
└── .env.example
```

## Inicio rápido

```bash
cp .env.example .env                                            # completar valores
docker compose up --build
docker compose run --rm app flask --app app sembrar --vaciar    # 400 conciertos ficticios (opcional)
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 (métricas en `/metricas`) |
| API | http://localhost:8000 |
| PostgreSQL (PostGIS) | localhost:55432 |

El esquema de la base se crea solo al arrancar. `sembrar` carga conciertos inventados en lugares
reales, con un año de historial, para ver las métricas sin esperar datos reales. **Borra los
conciertos que haya.** Para cargar los conciertos reales, con `SCRAPER_TOKEN` definido en `.env`:

```bash
curl -H "Authorization: Bearer <SCRAPER_TOKEN>" http://localhost:8000/ingestar_agendade
```

> El puerto 55432 es el que se publica en el host para herramientas locales; dentro de la red
> de Docker la app usa `db:5432`.

Para correr sin Docker, migraciones y despliegue, ver [OPERACION.md](docs/OPERACION.md).

## Tests y calidad

```bash
docker compose -f docker-compose.test.yml run --rm tests        # pytest contra un PostGIS descartable
ruff check app migrations tests && ruff format --check app migrations tests
cd web && npm run lint && npm run format:check && npm run build
```

Los tests no necesitan `.env` y no tocan la base de desarrollo. El workflow
[`ci.yml`](.github/workflows/ci.yml) corre lo mismo en cada PR y en cada push a `main`. Detalle en
[OPERACION.md](docs/OPERACION.md) §9 y §10.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Verificación de la API |
| GET | `/conciertos` | Conciertos vigentes |
| GET | `/conciertos_cerca?lat=&lng=&km=` | Conciertos vigentes dentro de un radio en km |
| GET | `/ubicaciones` | Lugares con coordenadas |
| GET/POST | `/ingestar_agendade` | Ingesta desde agendade.com.ar (**requiere token**) |
| GET | `/api/metricas/resumen` | Totales: conciertos, vigentes, pasados, lugares y artistas |
| GET | `/api/metricas/conciertos_por_mes` | Conciertos por mes (estacionalidad) |
| GET | `/api/metricas/lugares` | Ranking de lugares |
| GET | `/api/metricas/artistas` | Ranking de artistas |
| GET | `/api/metricas/densidad` | Puntos para el mapa de calor |
| GET | `/api/metricas/distancias` | Conciertos por rango de distancia a un punto |
| GET | `/api/metricas/dia_horario` | Conciertos por día de la semana y franja horaria |
| GET | `/api/metricas/proximos_dias` | Conciertos de cada uno de los próximos días |
| GET | `/api/metricas/calidad` | Datos faltantes (fecha, hora, entradas, lugar) |
| GET | `/api/metricas/ingesta` | Conciertos nuevos por día de ingesta |
| GET | `/api/metricas/anticipacion` | Anticipación de los anuncios (rangos y mediana) |

Los de métricas aceptan `?desde=AAAA-MM-DD&hasta=AAAA-MM-DD`, salvo `proximos_dias` e `ingesta`
(`?dias=`). Detalle en [API.md](docs/API.md).
