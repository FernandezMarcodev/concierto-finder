# Especificación de requisitos — Concierto Finder

> Documento obtenido por **ingeniería inversa** del código (octubre 2026). Describe lo que
> el sistema hace hoy ("as-built"), no un diseño aspiracional. Las limitaciones conocidas
> están listadas al final. Ver también [ARQUITECTURA.md](ARQUITECTURA.md), [API.md](API.md)
> y [OPERACION.md](OPERACION.md).

## 1. Propósito y alcance

Concierto Finder es una cartelera web de **próximos conciertos en Buenos Aires y alrededores
(AMBA)**. Junta los eventos publicados en agendade.com.ar, los ubica en un mapa y permite
filtrarlos por artista y por cercanía a la ubicación del usuario, con acceso directo a la
compra de entradas y a cómo llegar. Una página de **métricas** muestra cómo se distribuyen los
conciertos en el tiempo y en el espacio, a partir del historial acumulado.

**Dentro del alcance:** listado y mapa de conciertos de AMBA, filtros, ingesta automática
desde una única fuente, limpieza de duplicados, conservación del historial de conciertos pasados y métricas sobre ese historial.

**Fuera del alcance:** cuentas de usuario, venta de entradas (se redirige al vendedor),
eventos fuera de AMBA, carga manual de eventos, notificaciones.

## 2. Actores

| Actor | Descripción |
|---|---|
| **Visitante** | Persona que entra al sitio público. Anónima, sin registro. |
| **Operador** | Quien despliega el sistema y configura el token `SCRAPER_TOKEN`. Puede disparar la ingesta a mano. |
| **GitHub Actions** | Ejecuta el workflow programado que despierta la API y dispara la ingesta cada 12 h. |
| **agendade.com.ar** | Sistema externo, fuente de los eventos (scraping de HTML). |
| **Nominatim (OpenStreetMap)** | Sistema externo de geocodificación de nombres de lugares. |
| **OpenStreetMap tiles** | Sistema externo que provee el mapa base. |
| **Google Maps** | Sistema externo al que se enlaza para "Cómo llegar". |

## 3. Requisitos funcionales

### 3.1 Consulta (visitante)

| ID | Requisito |
|---|---|
| RF-01 | El sistema muestra todos los conciertos vigentes al cargar la página, en una lista y en un mapa. |
| RF-02 | La lista agrupa los conciertos **por lugar** (coordenada exacta): una tarjeta por lugar con la cantidad de conciertos y cada concierto en una fila. |
| RF-03 | Dentro de cada lugar, los conciertos se ordenan por fecha ascendente. |
| RF-04 | Cada fila muestra la fecha en un bloque tipo entrada (día de la semana, número y mes; "A confirmar" si no hay fecha), el artista, el nombre del evento (si difiere del artista) y la hora (`HH:MM h`; "Horario a confirmar" si no se conoce). Los conciertos de hoy y de mañana llevan la etiqueta **Hoy** o **Mañana**. |
| RF-05 | Cada fila ofrece, en este orden, **Entradas** (abre la URL de compra en otra pestaña; solo si existe), **Ver en mapa** y **Cómo llegar** (indicaciones de Google Maps; ambas solo si el lugar tiene coordenadas). En el teléfono, **Entradas** ocupa todo el ancho y las otras dos acciones van debajo, mitad y mitad. |
| RF-06 | **Ver en mapa** centra el mapa en el lugar (zoom 15), abre el popup del marcador, resalta el concierto y desplaza la página hasta el mapa. |
| RF-07 | El mapa muestra **un marcador por lugar**, con la cantidad de conciertos del lugar (también el 1). En el tema claro el mapa base se muestra en gris suave, para que se destaquen los datos. El popup lista el o los conciertos del lugar con fecha, hora y enlace a entradas. |
| RF-08 | Una portada con el logo muestra, según los filtros aplicados, la cantidad de conciertos, de lugares y de conciertos de hoy (este último, solo si hay). |
| RF-09 | **Buscador por artista**: filtra por coincidencia parcial, sin distinguir mayúsculas ni acentos ("paez" encuentra "Páez"). |
| RF-10 | El buscador sugiere hasta 8 artistas existentes mientras se escribe. Enter elige la primera sugerencia, Escape o un clic fuera cierra la lista, y un botón limpia la búsqueda. Si no hay coincidencias se indica "Sin resultados". |
| RF-11 | **Filtro por cercanía**: el visitante puede activar su ubicación (geolocalización del navegador) y desactivarla con el mismo botón. |
| RF-12 | Con la ubicación activa, se muestran solo los conciertos a una distancia ≤ radio elegido (distancia en línea recta). Los conciertos sin coordenadas no se excluyen. |
| RF-13 | El radio se elige con un slider de 1 a 40 km (inicial 5 km) o con atajos de 5, 20 y 40 km. El mapa dibuja la posición del usuario y el círculo del radio, y se encuadra en él. |
| RF-14 | Los filtros de artista y radio se combinan (Y lógico) y se aplican 300 ms después del último cambio. |
| RF-15 | Si no hay resultados se muestra un estado vacío con un mensaje para ajustar la búsqueda. |
| RF-16 | Si la API falla, se muestra un estado de error con el botón **Reintentar** (recarga la página). Mientras carga se muestran tarjetas de carga con la forma de la lista; si tarda más de 4 s, se avisa que el servidor se está despertando (la primera carga puede tardar hasta un minuto, RNF-05). La página de métricas da el mismo aviso. |

### 3.2 Ingesta y mantenimiento de datos (operador / sistema)

Los números RF-17 y RF-18 no se usan (quedaron libres en una versión anterior y no se reasignan).

| ID | Requisito |
|---|---|
| RF-19 | La ingesta se ejecuta automáticamente cada 12 h (9:10 y 21:10, hora argentina) mediante un workflow de GitHub Actions, que antes despierta la API. |
| RF-19 bis | Al arrancar, si la base no tiene conciertos, la API ejecuta la ingesta sola en segundo plano. Nunca corren dos ingestas a la vez (un pedido concurrente recibe 409). |
| RF-20 | La ingesta se dispara con `GET` o `POST /ingestar_agendade` y exige el token `SCRAPER_TOKEN`. Sin token configurado, el endpoint queda deshabilitado (503). |
| RF-21 | La ingesta recorre las páginas 1 a 5 de la agenda y, de cada evento, extrae título, artista (campo "ARTISTA" o "SHOW"; si falta, el título), lugar ("VENUE" + "UBICACIÓN"), fecha, hora y URL de compra. |
| RF-22 | El lugar se busca entre los ya registrados por nombre (coincidencia parcial, sin distinguir mayúsculas). Si no existe, se buscan sus coordenadas primero en la tabla de lugares conocidos (`services/lugares_conocidos.py`) y después en Nominatim, limitado a Argentina, y se registra con su punto y un enlace de Google Maps. |
| RF-23 | Solo se guardan conciertos cuyo lugar cae **dentro de AMBA** (ver RN-01). Los lugares no encontrados o fuera de AMBA se descartan, sin volver a consultarlos en la misma corrida. |
| RF-24 | No se insertan conciertos ya existentes (mismo nombre, artista, fecha y lugar). |
| RF-25 | La respuesta de la ingesta devuelve todos los eventos leídos (incluidos los descartados). |
| RF-26 | Cada 24 h el sistema borra los conciertos duplicados (conserva el de menor id). |
| RF-26 bis | Los conciertos pasados **no se borran**: quedan en la base como historial (base de las métricas). Los listados públicos (`/conciertos`, `/conciertos_cerca`) devuelven solo los vigentes (RN-02). |
| RF-27 | El backend expone `/ubicaciones` (lugares con coordenadas) y `/conciertos_cerca` (búsqueda espacial en el servidor). El frontend actual no los usa. |

### 3.3 Métricas (visitante)

| ID | Requisito |
|---|---|
| RF-28 | Una página **Métricas** (`/metricas`), accesible desde el encabezado, muestra indicadores y gráficos calculados sobre todo el historial (vigentes y pasados). |
| RF-29 | Indicadores con ícono: total de conciertos, vigentes, pasados, lugares distintos, artistas distintos y **concentración** (porcentaje de los conciertos en los 5 lugares más activos). Mientras haya menos de 4 meses de historial, un aviso explica desde cuándo se guarda. |
| RF-30 | **Conciertos por mes**: gráfico de área (línea con área suave) que incluye los meses sin conciertos y marca el mes actual con una línea vertical. |
| RF-31 | **Lugares más activos** y **artistas que más tocan**: rankings de los 10 primeros, en barras horizontales con la posición y el valor al final de cada barra; cada ranking con su propio color. |
| RF-32 | **Próximos 14 días**: conciertos de cada día desde hoy, en columnas con el valor arriba; los sábados y domingos en otro color, con leyenda. **¿Cuándo hay más conciertos?**: grilla de día de la semana por franja horaria (RN-13), con la cantidad en cada celda y una intensidad de color proporcional. **Anticipación**: histograma de días entre el anuncio y la fecha (RN-14), con la mediana en el texto. |
| RF-33 | **Mapa de calor** sobre el mapa de Leaflet, con una escala de un solo color que empieza transparente, un punto por lugar encima y su leyenda ("menos" a "más conciertos"). |
| RF-34 | Un filtro de período (Todo, Últimos 12 meses, Últimos 3 meses, Próximos, o fechas a medida) actualiza todas las métricas. Si "desde" es posterior a "hasta" se avisa y no se consulta. "Próximos 14 días" y "Conciertos nuevos por día" no dependen del período: siempre miran desde hoy. |
| RF-35 | Cada gráfico incluye sus datos en una tabla que no se ve en pantalla pero que leen los lectores de pantalla (el gráfico solo es un dibujo). La página indica desde qué fecha hay datos y cuántos conciertos no tienen fecha. Una sección **Calidad de los datos** muestra qué porcentaje de los conciertos tiene fecha, hora, link de entradas y lugar en el mapa (RN-15), y los conciertos nuevos por día de los últimos 30 días (salud de la ingesta). Las métricas que dependen de `creado_en` avisan desde cuándo se miden. |
| RF-36 | Las métricas también se exponen como API REST de solo lectura bajo `/api/metricas/...` (ver [API.md](API.md)). |

## 4. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | **Región AMBA**: latitud −35,15 a −34,2 y longitud −58,95 a −57,7. Fuente de verdad en `app/services/geocoding_service.py`, replicada en `web/src/constantes.js`. |
| RN-02 | Un concierto es "vigente" si su fecha es hoy (en hora de Argentina) o posterior, o si no tiene fecha. La vigencia **se deriva de la fecha** en cada consulta: no hay una columna de estado ni una tabla de archivados. Un concierto pasado sigue en la base, pero no se muestra. |
| RN-03 | Identidad de un concierto para deduplicar: (nombre, artista, fecha, lugar), con nulos considerados iguales. |
| RN-04 | La fecha de la fuente viene como `DD/MM/AA` o `DD/MM/AAAA` y la hora como `HH:MM` o `HH:MM:SS`. Si no se puede interpretar, queda nula. |
| RN-05 | Nombre y artista se recortan a 50 caracteres (largo de la columna). |
| RN-06 | La navegación del mapa está limitada a Argentina; solo se dibujan marcadores dentro de AMBA. |
| RN-07 | El centro inicial del mapa es el Obelisco (−34,6037; −58,3816), con zoom 11. |
| RN-08 | **Filtro de las métricas**: `desde` y `hasta` se aplican sobre la fecha del concierto (no la de ingesta) e incluyen los dos extremos. Sin filtro cuentan todos los conciertos; con filtro, los que no tienen fecha quedan afuera. Los conciertos sin fecha nunca entran en el gráfico por mes. |
| RN-09 | Las métricas por lugar, el mapa de calor y las distancias excluyen los conciertos sin lugar o sin coordenadas. |
| RN-10 | **Distancias**: geodésicas, en km y en línea recta, desde el Obelisco por defecto. Los rangos son semiabiertos `[desde, hasta)` y el último no tiene tope. Solo se usa en la API (`/api/metricas/distancias`): la página no muestra esta métrica. |
| RN-11 | **Mismo artista**: dos nombres son el mismo artista si coinciden sin distinguir mayúsculas, acentos ni espacios en los extremos ("Sofía Ríos" = "sofia rios"). En los rankings se muestra la escritura más frecuente. |
| RN-12 | **Cobertura**: las métricas solo reflejan lo publicado en agendade.com.ar (primeras 5 páginas) dentro de AMBA, desde que se conserva el historial. No son el total de conciertos de la ciudad. |
| RN-13 | **Franjas horarias** de la grilla día por horario: Día (6 a 18), 18 a 20, 20 a 22, 22 a 24 y Trasnoche (0 a 6). Un concierto a la 1:00 cuenta en la trasnoche del día calendario en que figura en la fuente. |
| RN-14 | **Anticipación**: días entre la fecha en que la ingesta encontró el concierto (`creado_en`, en hora argentina) y la fecha del concierto. Solo cuentan los conciertos encontrados desde la migración 0005 y los que tienen fecha; si se encontró después de su fecha, no cuenta. |
| RN-15 | **Calidad de datos**: un concierto está incompleto si le falta la fecha, la hora, el link de entradas (nulo o vacío) o un lugar con coordenadas. |

## 5. Requisitos no funcionales

| ID | Categoría | Requisito |
|---|---|---|
| RNF-01 | Rendimiento | `/conciertos` resuelve en una sola consulta SQL (JOIN), filtrada y ordenada en la base. `conciertos.fecha` y `conciertos.ubicacion` tienen índice, porque la tabla crece con el historial. |
| RNF-02 | Rendimiento | El filtrado es local en el navegador: los filtros no generan pedidos al servidor. |
| RNF-03 | Rendimiento | Las respuestas de conciertos se pueden cachear 5 minutos (`Cache-Control: public, max-age=300`). Los assets del frontend tienen hash y se cachean 1 año. |
| RNF-04 | Capacidad | Pool de conexiones a la base de 3 + 2 de desborde y 30 s de espera. Si se agota, la API responde 503. |
| RNF-05 | Disponibilidad | En Render (plan gratuito), la API se mantiene despierta de 9:00 a 2:00 (hora argentina, configurable): se pingea a sí misma cada 12 min y el workflow de GitHub Actions la despierta a las 9:10. Consume ≈ 535 h de las 750 h mensuales del plan. Fuera de la franja, el primer pedido espera 30 a 60 s. |
| RNF-06 | Robustez | Todo pedido HTTP saliente tiene timeout (15 s scraping/geocodificación, 30 s keep alive). Un evento con error no corta la ingesta. |
| RNF-07 | Cortesía con terceros | 1 s de pausa entre eventos scrapeados. User-Agent identificable para Nominatim. |
| RNF-08 | Seguridad | Las credenciales solo se leen del entorno (`DATABASE_URL`, `SCRAPER_TOKEN`), nunca del código. El token se compara en tiempo constante. |
| RNF-09 | Seguridad | La API pública es de solo lectura; la única escritura (ingesta) requiere token. CORS abierto a cualquier origen. Las tablas de la base tienen seguridad a nivel de fila (RLS) y los roles de la API automática de Supabase (`anon`, `authenticated`) no tienen permisos: los datos solo se leen y escriben a través de la API de Flask. |
| RNF-10 | Mantenibilidad | El esquema de la base se versiona con migraciones de Alembic y se aplica al arrancar el contenedor. |
| RNF-11 | Usabilidad | Interfaz en español, responsiva, con estados de carga, vacío y error. Fechas en formato `es-AR` y hora local. Sin scroll horizontal desde 320 px de ancho. |
| RNF-12 | Portabilidad | El stack completo levanta con `docker compose up --build`. |
| RNF-13 | Convención | Código, identificadores, comentarios y textos de la interfaz en español. |
| RNF-14 | Calidad | El backend tiene tests automatizados (pytest) que corren contra PostgreSQL + PostGIS real y crean el esquema con las migraciones. Ver [OPERACION.md](OPERACION.md) §9. Los lints, los tests y el build del frontend corren solos en cada PR y en cada push a `main` (GitHub Actions, §10). |
| RNF-15 | Rendimiento | Las métricas se calculan en la base (SQL/PostGIS): cada endpoint hace una sola consulta y devuelve resultados agregados, nunca filas de conciertos. Se cachean 5 minutos. La página de métricas se descarga aparte (code splitting) y no agrega peso a la principal. |

## 6. Restricciones y supuestos

- Una sola fuente de datos; el scraper depende de las clases CSS de agendade.com.ar
  (`link-block-11`, `div-block-192`, `div-block-243`, etc.). Un rediseño del sitio rompe la ingesta.
- La geocodificación usa el servicio público de Nominatim (máximo 1 pedido por segundo, sin SLA).
  Nominatim busca por el nombre que el lugar tiene en OpenStreetMap, así que muchas salas y estadios
  no aparecen con el nombre de la agenda ("Estadio Huracán" es "Estadio Tomás Adolfo Ducó"): esos
  lugares se cargan a mano en la tabla de lugares conocidos, con coordenadas verificadas en OSM.
- PostgreSQL con la extensión PostGIS es obligatorio.
- La URL de la API queda fija en el build del frontend (`VITE_API_URL`).
- Se supone un volumen chico (cientos de conciertos): el frontend descarga la lista completa.

## 7. Limitaciones conocidas

| Limitación | Impacto |
|---|---|
| La búsqueda de lugar por nombre parcial (`ILIKE %nombre%`) puede asociar un evento al lugar equivocado si un nombre contiene a otro. | Marcador en el lugar incorrecto. |
| `ubicaciones.nombre` admite 50 caracteres; un lugar con nombre más largo hace fallar el alta y se pierde ese evento. | Pérdida de algunos eventos. |
| Muchos bares y salas chicas de AMBA (por ejemplo Lucille, La Tangente, Lalalá o CC Richards) no están cargados en OpenStreetMap con ningún nombre, así que Nominatim no los encuentra y sus conciertos se descartan. La tabla de lugares conocidos solo cubre los lugares agregados a mano. | Faltan conciertos de lugares chicos. Se pueden recuperar de a uno: el log dice qué lugar no se encontró, y se agrega a `lugares_conocidos.py` con la coordenada de su dirección (ver `OPERACION.md` §8). |
| `capacidad_total` siempre se guarda en 0 (la fuente no la informa). | Campo sin uso real. |
| La ingesta corre dentro del pedido HTTP (varios minutos). | Si el cliente o un proxy corta por timeout, la ingesta igual continúa en el servidor, pero no se ve el resultado. |
| El frontend no tiene tests automatizados, y el scraper solo tiene tests de sus funciones de parseo (no del recorrido del HTML de agendade). | Las regresiones del frontend y los cambios de HTML de la fuente se detectan a mano. |
| Un concierto cancelado o reprogramado queda en el historial: la ingesta no registra cuándo vio un concierto por última vez, así que no se distingue de uno que se realizó. Una reprogramación queda como dos conciertos (fecha vieja y fecha nueva). | Las métricas cuentan de más esos casos. Se podría resolver más adelante con una columna `visto_en` que la ingesta actualice cada vez que encuentra el concierto. |
