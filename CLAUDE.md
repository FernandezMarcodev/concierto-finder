# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Concierto Finder: a listing of upcoming concerts in Buenos Aires and the surrounding area (AMBA). Flask + SQLAlchemy/GeoAlchemy2 + PostGIS backend in `app/`, React 18 + Vite + Leaflet frontend in `web/`. Code, identifiers (functions, variables, model classes in singular: `Concierto`, `Ubicacion`), comments and UI text are in Spanish; UI copy uses rioplatense voseo ("Escribí", "Intentá"). Keep that convention. Brand name: "Concierto Finder".

## Commands

Full stack (needs `.env` copied from `.env.example`):
```bash
docker compose up --build        # web :5173 (nginx), api :8000, PostGIS on host :55432
docker compose build web         # required after changing WEB_API_URL (baked in at build time)
```

Backend without Docker (PowerShell):
```powershell
$env:DATABASE_URL = "postgresql://user:pass@localhost:55432/db"
pip install -r requirements.txt
flask --app app db upgrade       # apply migrations (the Docker image does this on start)
python -m app.main               # serves with waitress on $PORT (default 8000)
```

Migrations: `flask --app app db migrate -m "..."` after changing a model, then review the generated file in `migrations/versions/`. `flask --app app db upgrade --sql` renders SQL without a database.

Frontend (`web/`): `npm run dev`, `npm run build`, `npm run lint` (ESLint 9 flat config).

Formatting and linting (run before committing):
```bash
ruff check app migrations tests && ruff format app migrations tests   # backend (pip install -r requirements-dev.txt); config in pyproject.toml
cd web && npm run lint && npm run format                   # frontend: ESLint + Prettier
```

Fake data for local dev: `docker compose run --rm app flask --app app sembrar --vaciar` (`app/cli.py` → `services/datos_ficticios.py`; refuses on Render or when the table has data unless `--vaciar`, which TRUNCATEs everything; ticket URLs use example.com).

Tests (backend only, pytest against a real PostGIS, see `docs/OPERACION.md` §9):
```bash
docker compose -f docker-compose.test.yml run --rm tests            # all tests, no .env needed
docker compose -f docker-compose.test.yml run --rm tests pytest -k vigentes -v
```
`tests/conftest.py` refuses to run unless `TEST_DATABASE_URL` points to a database whose name ends in `_test` (tests TRUNCATE the tables). The schema comes from the Alembic migrations, `test_migraciones.py` fails if a model changes without a migration, and the `hoy` fixture fixes "today" to 2026-10-15 (repositories take `hoy` as a parameter; routes are monkeypatched).

Python dependencies are pinned in `requirements.txt`; line endings are LF (`.gitattributes`).

Project docs (Spanish, reverse-engineered from the code) live in `docs/`: `REQUISITOS.md`, `ARQUITECTURA.md`, `API.md`, `OPERACION.md`. Update them when behavior changes. `docs/PLAN.md` is the feature roadmap and Git workflow: one branch per feature (`feat/`, `fix/`, `chore/`, `docs/`, `refactor/` + Spanish kebab-case), PR to `main`, squash merge; never commit features directly to `main`. Only one open branch with migrations at a time.

## Architecture notes

- **`DATABASE_URL` is read at import time.** `app/config.py` raises `RuntimeError` when `Config` is defined, so importing `app` at all (including `create_app`) fails without that variable set.
- **Migrations:** Alembic via Flask-Migrate in `migrations/`. `0001_esquema_inicial` skips tables that already exist (databases created earlier with `create_all()`), so `upgrade` works on fresh and existing databases. `create_app()` imports `app.models` so the metadata is complete. Use `flask --app app` (not `app.main`) for CLI commands: it does not start the background threads. Tables: `ubicaciones` (PostGIS `POINT`, SRID 4326) and `conciertos` (FK to `ubicaciones` with cascade delete; `url_evento` is `TEXT`).
- **Importing `app.main` starts background threads** (`app/services/tareas.py`): `mantener_despierta` pings `KEEP_ALIVE_URL` (falls back to `RENDER_EXTERNAL_URL`, so it only runs on Render; empty disables it) every 12 min but only inside the `KEEP_ALIVE_DESDE`..`KEEP_ALIVE_HASTA` window (Argentina time, default 9 to 2) so the Render free tier (750 h/month shared per account) lasts the whole month; the GitHub Actions workflow `.github/workflows/ingesta.yml` wakes the instance and triggers ingestion every 12 h (9:10 and 21:10 Argentina time, cron in UTC) using the repo secret `SCRAPER_TOKEN` (see `docs/OPERACION.md` §5-6). Keep its schedule inside the keep-alive window. On startup, `ingesta_inicial` runs the ingestion in a background thread only if the `conciertos` table is empty (first deploy). A `threading.Lock` in `scraper_service` ensures a single ingestion at a time (the route answers 409 otherwise), and the keep-alive also pings while an ingestion is running. Never point UptimeRobot-style monitors at it: they keep it awake 24 h. `programar_limpieza_diaria` deletes duplicate concerts every 24 h with one bulk `DELETE` (keeps the lowest id). Past concerts are **kept as history** (for metrics): "vigente" is derived from `fecha` (`fecha >= hoy OR fecha IS NULL`, Argentina date from `services/fechas.py`) inside `_consulta_vigentes` in `concierto_repository`, which every public listing must use.
- **Logging:** use `logging.getLogger(__name__)`, not `print`. `app/main.py` configures it; the level comes from `LOG_LEVEL`.
- **Layering:** routes (blueprints registered in `app/routes/__init__.py`) → repositories (all queries; concert listings use `joinedload` to avoid N+1 and are ordered by date/time) → models. `services/` holds the scraper, geocoding, background tasks and the shared HTTP session (`services/http.py`, always pass `timeout=`). `schemas/` holds hand-written dict serializers, not marshmallow.
- **Ingestion** happens only through `GET`/`POST /ingestar_agendade`, protected by `SCRAPER_TOKEN` (`Authorization: Bearer` header or `?token=`; checked by `verificar_token_ingesta()` in `app/routes/autorizacion.py`, called at the top of the route). Without the env var the endpoint returns 503. It scrapes 5 pages of agendade.com.ar, matches venues by `ilike` name, otherwise geocodes them with Nominatim, and stores only venues inside AMBA (rejected venue names are cached for the run). Concerts already present (same name, artist, date and venue) are skipped. Dates are parsed with `strptime` (`DD/MM/YY` or `DD/MM/YYYY`); concert name/artist are truncated to the column length.
- **AMBA bounds are duplicated** in `app/services/geocoding_service.py` (the source of truth) and `web/src/constantes.js`. Change both together.
- **Coordinate order:** PostGIS/WKT and the serialized `coordenadas` array are `[lng, lat]`. The frontend reads `coordenadas[1]` as lat and `coordenadas[0]` as lng.
- **Serialization:** `fecha` (`YYYY-MM-DD`) and `hora` (`HH:MM:SS`) are ISO strings or `null`; `ubicacion_detalle` is `null` when there is no venue. Older backends sent `"None"`, which `fechaLegible`/`horaLegible` in `web/src/utilidades/texto.js` still tolerate. Never format dates with `new Date("YYYY-MM-DD")`: it parses as UTC and shows the previous day in Argentina.
- **DB pool is small** (3 + 2 overflow). A `TimeoutError` handler in `create_app` returns 503 when it is exhausted. Concert listings send `Cache-Control: max-age=300`.

### Frontend

- Single page: `web/src/paginas/Inicio.jsx` loads all concerts once from `/conciertos` and does **all filtering client-side** (`utilidades/filtros.js`): artist text (accent-insensitive via `normalizarTexto`) and radius around the user's location (Haversine in `utilidades/geo.js`). The filtered list is derived with `useMemo` from debounced filters (`hooks/useDebounce.js`, 300 ms), not stored in state. Shared constants live in `web/src/constantes.js`.
- Concerts are grouped per exact coordinate (`utilidades/grupos.js`) once in `Inicio`; the same groups feed the `Mapa` markers and the `TarjetaGrupo` cards. "Ver en mapa" sets a new `seleccion` object, and `Mapa` opens the marker's popup through `Marker` refs (react-leaflet v4 has no `whenCreated`).
- The service throws on HTTP errors so the page can show its error state.
- API base URL comes from `VITE_API_URL`. If it is unset, it falls back to the production API (`https://concierto-finder.onrender.com`; the frontend is `https://conciertosfinder.pages.dev`), so a local dev server without `.env.local` reads production data.
- Components live in `web/src/componentes/<Nombre>/<Nombre>.jsx` with a co-located CSS module `<nombre>.module.css`.
- **Theming:** light/dark via `data-tema="claro" | "oscuro"` on `<html>`. Color tokens for both themes live in `web/src/index.css`; components use `var(--...)` for anything theme-dependent. An inline script in `index.html` applies the saved or system theme before first paint, and `hooks/useTema.js` (toggle in `Encabezado`) keeps it in sync (localStorage key `tema`). Dark-only effects use `:global(:root[data-tema="oscuro"])` (e.g. the map tile filter). The logo PNG is black; `--logo-filtro` inverts it in dark mode.
