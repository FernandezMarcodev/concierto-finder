# Operación — Concierto Finder

Guía para configurar, desplegar y mantener el sistema. Arquitectura en
[ARQUITECTURA.md](ARQUITECTURA.md).

## 1. Variables de entorno

| Variable | Dónde | Obligatoria | Descripción |
|---|---|---|---|
| `DATABASE_URL` | API | **sí** | `postgresql://usuario:pass@host:puerto/base`. Si falta, la app no arranca (`RuntimeError` al importar). En compose se arma sola apuntando a `db:5432`. |
| `SCRAPER_TOKEN` | API | para la ingesta | Token de `/ingestar_agendade`. Vacío = endpoint deshabilitado (503). Generalo con `python -c "import secrets; print(secrets.token_urlsafe(32))"`. |
| `KEEP_ALIVE_URL` | API | no | URL que se pingea cada 12 min (ver §5). Sin definir usa `RENDER_EXTERNAL_URL`, que Render define solo; en local no existe ninguna y no se pingea. Vacía desactiva el ping. |
| `KEEP_ALIVE_DESDE` / `KEEP_ALIVE_HASTA` | API | no | Franja (hora argentina, 0-23) en la que se pingea. Por defecto 9 y 2: de 9:00 a 2:00. Iguales = todo el día. |
| `LOG_LEVEL` | API | no | `DEBUG`, `INFO` (por defecto), `WARNING`... |
| `PORT` | API | no | Puerto con `python -m app.main` (por defecto 8000). La imagen Docker siempre usa 8000. |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | compose | sí (compose) | Credenciales del contenedor PostGIS. |
| `WEB_API_URL` | compose | no | URL de la API que se inyecta como `VITE_API_URL` en el build del frontend (por defecto `http://localhost:8000`). |
| `VITE_API_URL` | build del frontend | no | Sin valor, el frontend usa la API de producción. |

Todas se documentan en `.env.example`. `.env` nunca se versiona.

## 2. Entorno local

### Con Docker (recomendado)

```bash
cp .env.example .env          # completar valores
docker compose up --build
```

Web en http://localhost:5173, API en http://localhost:8000 y PostGIS en `localhost:55432`.
Al arrancar, el contenedor `app` corre `flask --app app db upgrade`, así que **el esquema se
crea solo**. Después de cambiar `WEB_API_URL`: `docker compose build web`.

Para cargar datos, con `SCRAPER_TOKEN` definido en `.env`:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/ingestar_agendade
```

### Sin Docker (PowerShell)

```powershell
$env:DATABASE_URL = "postgresql://usuario:pass@localhost:55432/base"
pip install -r requirements.txt
flask --app app db upgrade        # crea o actualiza el esquema
python -m app.main                # API en :8000 con waitress
```

```bash
cd web && npm install && npm run dev    # crear web/.env.local con VITE_API_URL=http://localhost:8000
```

Sin `web/.env.local`, el servidor de desarrollo lee los datos de **producción**.

## 3. Migraciones de base de datos

El esquema se versiona con Alembic (Flask-Migrate) en `migrations/`.

| Acción | Comando |
|---|---|
| Aplicar pendientes | `flask --app app db upgrade` |
| Crear una migración tras cambiar un modelo | `flask --app app db migrate -m "descripcion"` y **revisar** el archivo generado |
| Ver el SQL sin conectarse | `flask --app app db upgrade --sql` |
| Ver la revisión actual | `flask --app app db current` |
| Revertir la última | `flask --app app db downgrade` |

**Bases creadas antes de las migraciones** (con `db.create_all()`): no hace falta hacer nada.
`0001_esquema_inicial` detecta las tablas existentes y no las toca, y `0002` amplía `url_evento`.
Basta con correr `upgrade`.

## 4. Despliegue en producción

| Pieza | Plataforma | Notas |
|---|---|---|
| API | Render (https://concierto-finder.onrender.com) | Con el `Dockerfile` raíz, las migraciones corren al iniciar. Si el servicio usa un comando de arranque propio, debe ejecutar `flask --app app db upgrade` antes de levantar la app. Configurar `DATABASE_URL`, `SCRAPER_TOKEN` y, opcionalmente, `KEEP_ALIVE_URL` (§5). |
| Frontend | Cloudflare Pages (https://conciertosfinder.pages.dev) | Build `npm run build` en `web/` y salida `dist/`. Definir `VITE_API_URL` si la API no es la de por defecto. |
| Base | PostgreSQL con PostGIS | La migración inicial ejecuta `CREATE EXTENSION IF NOT EXISTS postgis` (requiere permisos). |

### Checklist de un despliegue

1. Definir `SCRAPER_TOKEN` en Render **antes** de desplegar: sin él, la ingesta queda deshabilitada.
2. Crear el secret `SCRAPER_TOKEN` en GitHub con el mismo valor que en Render (§5), para el workflow de ingesta.
3. Desplegar la API y verificar en los logs `Running upgrade ... -> 0002_url_evento_text`.
4. Verificar `GET /` (200) y `GET /conciertos`.
5. Desplegar el frontend.

## 5. Mantener despierta la API (Render gratuito)

Render duerme un servicio gratuito tras **15 min sin tráfico**, y el primer pedido posterior tarda
30 a 60 s en despertarlo. El plan gratuito da **750 h de instancia por mes, compartidas entre todos
los servicios gratuitos de la cuenta**. Si se agotan, Render suspende los servicios hasta el mes
siguiente. Por eso la API **no** se mantiene despierta las 24 h (744 h en un mes de 31 días, sin
margen), sino solo en una franja horaria:

| Pieza | Qué hace |
|---|---|
| Hilo `mantener_despierta` | Mientras la instancia está despierta y la hora argentina cae entre `KEEP_ALIVE_DESDE` y `KEEP_ALIVE_HASTA` (9 a 2 por defecto), hace `GET /` cada 12 min. Fuera de la franja no pingea y Render la duerme. |
| Workflow de GitHub Actions | Un hilo no puede despertar a una instancia dormida (no existe mientras duerme). El workflow `.github/workflows/ingesta.yml` la despierta a las 9:10 y a las 21:10 y, de paso, dispara la ingesta (§6). |

Consumo: unas 17 h por día, **≈ 535 h por mes**, con margen para otro servicio chico. Un visitante
fuera de la franja igual puede usar la página: la API se despierta con su pedido (espera la
primera vez) y vuelve a dormirse 15 min después.

**No uses UptimeRobot ni otro monitor que pingee cada pocos minutos**: mantiene la API despierta
las 24 h y anula la franja.

### Configuración

1. **Render** (Environment). Nada es obligatorio: `RENDER_EXTERNAL_URL` ya apunta al servicio. Para
   dejarlo explícito:
   ```
   KEEP_ALIVE_URL=https://concierto-finder.onrender.com/
   KEEP_ALIVE_DESDE=9
   KEEP_ALIVE_HASTA=2
   ```
   Al arrancar, el log muestra `Keep alive a ... entre las 9 y las 2 h (hora argentina)`.
2. **GitHub** (Settings → Secrets and variables → Actions → New repository secret): crear el
   secret `SCRAPER_TOKEN` con **el mismo valor** que la variable de Render. Sin él, el workflow
   falla con "Falta el secret SCRAPER_TOKEN".

No hace falta cron-job.org ni UptimeRobot.

## 6. Ingesta programada

La ingesta no corre sola dentro de la API: la dispara el workflow **`.github/workflows/ingesta.yml`**
de GitHub Actions.

| Qué | Detalle |
|---|---|
| Cuándo | Cada 12 h: **9:10 y 21:10** (hora argentina). En el cron de GitHub figura en UTC: `10 0,12 * * *`. Las dos horas caen dentro de la franja del keep alive. |
| Paso 1 | `GET /` hasta 10 veces, cada 15 s, hasta que Render despierte la API. |
| Paso 2 | `POST /ingestar_agendade` con el header `Authorization: Bearer <SCRAPER_TOKEN>`. Espera hasta 25 min. |
| Resultado | Verde: terminó y muestra cuántos eventos leyó. Amarillo (warning): pasaron 25 min sin respuesta, pero el servidor sigue trabajando aunque se corte la conexión. Rojo: no despertó, falta el secret, o la API respondió un error (por ejemplo, 401 por un token distinto al de Render). |
| A mano | Pestaña **Actions → Ingesta de conciertos → Run workflow**. |

**Después de un deploy con la base vacía no hace falta esperar al workflow:** la API ejecuta sola la
ingesta inicial al arrancar (§7). Con la base ya cargada, un redeploy no scrapea; los conciertos
nuevos entran en la siguiente corrida del workflow, o antes si lo lanzás a mano.

Nunca corren dos ingestas a la vez: si llega un pedido mientras otra corre, la API responde 409 y el
workflow lo muestra como warning. Mientras corre una ingesta, el keep alive pingea aunque sea fuera
de la franja, para que Render no duerma la instancia a mitad de camino.

Los conciertos **nuevos guardados** figuran en los logs de Render
(`Conciertos leídos: ..., nuevos guardados: ...`). Correr la ingesta dos veces seguidas no duplica
nada: los conciertos que ya existen se saltean.

Detalles de GitHub Actions a tener en cuenta:
- Los workflows programados pueden arrancar con algunos minutos de demora.
- En repos públicos, GitHub **desactiva los workflows programados tras 60 días sin actividad en el
  repo** (sin commits). Si pasa, se reactivan desde la pestaña Actions con un clic.

Para dispararla desde otro lado (por ejemplo, desde tu máquina):

```bash
curl -fsS -X POST -H "Authorization: Bearer $SCRAPER_TOKEN" \
     --max-time 1500 https://concierto-finder.onrender.com/ingestar_agendade
```

Si un servicio de cron solo admite una URL: `https://concierto-finder.onrender.com/ingestar_agendade?token=<token>`.

## 7. Tareas automáticas

| Tarea | Frecuencia | Qué hace |
|---|---|---|
| `mantener_despierta` | 12 min, solo dentro de la franja | `GET KEEP_ALIVE_URL` para evitar que Render duerma el servicio (ver §5). |
| `programar_limpieza_diaria` | al arrancar y cada 24 h | Borra conciertos pasados (según la fecha argentina) y duplicados. |
| `ingesta_inicial` | al arrancar | Si la base **no tiene ningún concierto** (primer deploy o base nueva), ejecuta la ingesta en segundo plano. Con datos ya cargados no hace nada. |

Corren como hilos dentro del proceso de `app.main`. Como Render reinicia el proceso cada vez que
despierta la instancia, la limpieza corre al menos una vez por día.

## 8. Diagnóstico

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| La app no arranca: `Falta la variable de entorno DATABASE_URL` | Variable sin definir | Definirla (ver §1). |
| La ingesta responde `503 Endpoint deshabilitado` | Falta `SCRAPER_TOKEN` | Configurarlo y reiniciar. |
| La ingesta responde `401` | Token incorrecto o mal enviado | Revisar el header `Authorization: Bearer ...`. |
| La API responde `503 Servidor ocupado` | Pool de conexiones agotado | Revisar consultas lentas o la carga; el pool es de 3+2 conexiones. |
| La ingesta lee eventos pero no guarda ninguno | Cambió el HTML de agendade o Nominatim no responde | Revisar los logs (`app.services.scraper_service`) con `LOG_LEVEL=DEBUG`. |
| El frontend local muestra datos de producción | Falta `VITE_API_URL` | Crear `web/.env.local`. |
| `flask db upgrade` falla con `permission denied to create extension` | El usuario no puede crear PostGIS | Crear la extensión como superusuario una vez. |
