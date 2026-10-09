# cfinder — Concierto Finder

Cartelera de próximos conciertos en Buenos Aires y alrededores (AMBA): lista y mapa con
filtros por artista y por cercanía, enlaces a entradas y a cómo llegar.

API en Flask + SQLAlchemy + PostGIS y frontend en React + Vite + Leaflet.

- Web: https://conciertosfinder.pages.dev/
- API: https://concierto-finder.onrender.com/

## Documentación

| Documento | Contenido |
|---|---|
| [REQUISITOS.md](docs/REQUISITOS.md) | Alcance, actores, requisitos funcionales y no funcionales, reglas de negocio y limitaciones. |
| [ARQUITECTURA.md](docs/ARQUITECTURA.md) | Vistas C4, capas, modelo de datos, flujos, decisiones y deuda técnica. |
| [API.md](docs/API.md) | Endpoints, formatos y códigos de error. |
| [OPERACION.md](docs/OPERACION.md) | Variables de entorno, entorno local, migraciones, despliegue, ingesta y diagnóstico. |
| [PLAN.md](docs/PLAN.md) | Cómo trabajamos con ramas y PRs, y la hoja de ruta de features, una rama por feature. |

## Estructura

```text
cfinder/
├── app/                    # Backend (paquete Python)
│   ├── __init__.py         # create_app()
│   ├── main.py             # Entrypoint: logging, app y tareas en background
│   ├── config.py           # Configuración leída de variables de entorno
│   ├── extensions.py       # SQLAlchemy y Flask-Migrate
│   ├── models/             # Concierto, Ubicacion
│   ├── repositories/       # Todas las consultas a la base
│   ├── schemas/            # Serialización de las respuestas
│   ├── routes/             # Blueprints y autorización por token
│   └── services/           # Scraper, geocodificación, tareas, cliente HTTP
├── .github/workflows/      # ingesta.yml: dispara la ingesta cada 12 h (GitHub Actions)
├── migrations/             # Migraciones de Alembic
├── docs/                   # Documentación (requisitos, arquitectura, API, operación)
├── web/                    # Frontend (React + Vite + Leaflet)
│   └── src/
│       ├── paginas/        # Inicio (única página)
│       ├── componentes/    # <Nombre>/<Nombre>.jsx + <nombre>.module.css
│       ├── hooks/          # useDebounce, useTema
│       ├── servicios/      # Cliente de la API
│       ├── utilidades/     # filtros, grupos, geo, texto
│       └── constantes.js
├── Dockerfile              # Imagen de la API (aplica migraciones al iniciar)
├── docker-compose.yml      # db (PostGIS) + app + web (nginx)
├── requirements.txt        # Dependencias fijadas (requirements-dev.txt suma Ruff)
├── pyproject.toml          # Configuración de Ruff
└── .env.example
```

## Inicio rápido

```bash
cp .env.example .env      # completar valores (incluido SCRAPER_TOKEN para cargar datos)
docker compose up --build
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| PostgreSQL (PostGIS) | localhost:55432 |

El esquema de la base se crea solo al arrancar. Para cargar conciertos:

```bash
curl -H "Authorization: Bearer <SCRAPER_TOKEN>" http://localhost:8000/ingestar_agendade
```

> El puerto 55432 es el que se publica en el host para herramientas locales; dentro de la red
> de Docker la app usa `db:5432`.

Para correr sin Docker, migraciones y despliegue, ver [OPERACION.md](docs/OPERACION.md).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Verificación de la API |
| GET | `/conciertos` | Lista de conciertos |
| GET | `/conciertos_cerca?lat=&lng=&km=` | Conciertos dentro de un radio en km |
| GET | `/ubicaciones` | Lugares con coordenadas |
| GET/POST | `/ingestar_agendade` | Ingesta desde agendade.com.ar (**requiere token**) |

Detalle en [API.md](docs/API.md).
