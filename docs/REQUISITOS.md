# Especificación de requisitos — Concierto Finder

> Documento obtenido por **ingeniería inversa** del código (octubre 2026). Describe lo que
> el sistema hace hoy ("as-built"), no un diseño aspiracional. Las limitaciones conocidas
> están listadas al final. Ver también [ARQUITECTURA.md](ARQUITECTURA.md), [API.md](API.md)
> y [OPERACION.md](OPERACION.md).

## 1. Propósito y alcance

Concierto Finder es una cartelera web de **próximos conciertos en Buenos Aires y alrededores
(AMBA)**. Junta los eventos publicados en agendade.com.ar, los ubica en un mapa y permite
filtrarlos por artista y por cercanía a la ubicación del usuario, con acceso directo a la
compra de entradas y a cómo llegar.

**Dentro del alcance:** listado y mapa de conciertos de AMBA, filtros, ingesta automática
desde una única fuente, limpieza de datos vencidos.

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
| RF-04 | Cada fila muestra artista, nombre del evento (si difiere del artista), fecha (`d/m/aaaa`) y hora (`HH:MM`, si se conoce). Sin fecha se muestra "Fecha a confirmar". |
| RF-05 | Cada fila ofrece **Entradas** (abre la URL de compra en otra pestaña; solo si existe), **Ver en mapa** y **Cómo llegar** (indicaciones de Google Maps; ambas solo si el lugar tiene coordenadas). |
| RF-06 | **Ver en mapa** centra el mapa en el lugar (zoom 15), abre el popup del marcador, resalta el concierto y desplaza la página hasta el mapa. |
| RF-07 | El mapa muestra **un marcador por lugar**. El popup lista el o los conciertos del lugar con fecha, hora y enlace a entradas. |
| RF-08 | El encabezado muestra la cantidad de conciertos que cumplen los filtros. |
| RF-09 | **Buscador por artista**: filtra por coincidencia parcial, sin distinguir mayúsculas ni acentos ("paez" encuentra "Páez"). |
| RF-10 | El buscador sugiere hasta 8 artistas existentes mientras se escribe. Enter elige la primera sugerencia, Escape o un clic fuera cierra la lista, y un botón limpia la búsqueda. Si no hay coincidencias se indica "Sin resultados". |
| RF-11 | **Filtro por cercanía**: el visitante puede activar su ubicación (geolocalización del navegador) y desactivarla con el mismo botón. |
| RF-12 | Con la ubicación activa, se muestran solo los conciertos a una distancia ≤ radio elegido (distancia en línea recta). Los conciertos sin coordenadas no se excluyen. |
| RF-13 | El radio se elige con un slider de 1 a 40 km (inicial 5 km) o con atajos de 5, 20 y 40 km. El mapa dibuja la posición del usuario y el círculo del radio, y se encuadra en él. |
| RF-14 | Los filtros de artista y radio se combinan (Y lógico) y se aplican 300 ms después del último cambio. |
| RF-15 | Si no hay resultados se muestra un estado vacío con un mensaje para ajustar la búsqueda. |
| RF-16 | Si la API falla, se muestra un estado de error con el botón **Reintentar** (recarga la página). Mientras carga se muestra un indicador. |

### 3.2 Ingesta y mantenimiento de datos (operador / sistema)

| ID | Requisito |
|---|---|
| RF-19 | La ingesta se ejecuta automáticamente cada 12 h (9:10 y 21:10, hora argentina) mediante un workflow de GitHub Actions, que antes despierta la API. |
| RF-19 bis | Al arrancar, si la base no tiene conciertos, la API ejecuta la ingesta sola en segundo plano. Nunca corren dos ingestas a la vez (un pedido concurrente recibe 409). |
| RF-20 | La ingesta se dispara con `GET` o `POST /ingestar_agendade` y exige el token `SCRAPER_TOKEN`. Sin token configurado, el endpoint queda deshabilitado (503). |
| RF-21 | La ingesta recorre las páginas 1 a 5 de la agenda y, de cada evento, extrae título, artista (campo "ARTISTA" o "SHOW"; si falta, el título), lugar ("VENUE" + "UBICACIÓN"), fecha, hora y URL de compra. |
| RF-22 | El lugar se busca entre los ya registrados por nombre (coincidencia parcial, sin distinguir mayúsculas). Si no existe, se geocodifica con Nominatim y se registra con su punto y un enlace de Google Maps. |
| RF-23 | Solo se guardan conciertos cuyo lugar cae **dentro de AMBA** (ver RN-01). Los lugares no encontrados o fuera de AMBA se descartan, sin volver a consultarlos en la misma corrida. |
| RF-24 | No se insertan conciertos ya existentes (mismo nombre, artista, fecha y lugar). |
| RF-25 | La respuesta de la ingesta devuelve todos los eventos leídos (incluidos los descartados). |
| RF-26 | Cada 24 h el sistema borra los conciertos con fecha anterior a hoy y los duplicados (conserva el de menor id). |
| RF-27 | El backend expone `/ubicaciones` (lugares con coordenadas) y `/conciertos_cerca` (búsqueda espacial en el servidor). El frontend actual no los usa. |

## 4. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | **Región AMBA**: latitud −35,15 a −34,2 y longitud −58,95 a −57,7. Fuente de verdad en `app/services/geocoding_service.py`, replicada en `web/src/constantes.js`. |
| RN-02 | Un concierto es "vigente" si su fecha es hoy (en hora de Argentina) o posterior, o si no tiene fecha (los conciertos sin fecha no se borran). |
| RN-03 | Identidad de un concierto para deduplicar: (nombre, artista, fecha, lugar), con nulos considerados iguales. |
| RN-04 | La fecha de la fuente viene como `DD/MM/AA` o `DD/MM/AAAA` y la hora como `HH:MM` o `HH:MM:SS`. Si no se puede interpretar, queda nula. |
| RN-05 | Nombre y artista se recortan a 50 caracteres (largo de la columna). |
| RN-06 | La navegación del mapa está limitada a Argentina; solo se dibujan marcadores dentro de AMBA. |
| RN-07 | El centro inicial del mapa es el Obelisco (−34,6037; −58,3816), con zoom 11. |

## 5. Requisitos no funcionales

| ID | Categoría | Requisito |
|---|---|---|
| RNF-01 | Rendimiento | `/conciertos` resuelve en una sola consulta SQL (JOIN), ordenada en la base. |
| RNF-02 | Rendimiento | El filtrado es local en el navegador: los filtros no generan pedidos al servidor. |
| RNF-03 | Rendimiento | Las respuestas de conciertos se pueden cachear 5 minutos (`Cache-Control: public, max-age=300`). Los assets del frontend tienen hash y se cachean 1 año. |
| RNF-04 | Capacidad | Pool de conexiones a la base de 3 + 2 de desborde y 30 s de espera. Si se agota, la API responde 503. |
| RNF-05 | Disponibilidad | En Render (plan gratuito), la API se mantiene despierta de 9:00 a 2:00 (hora argentina, configurable): se pingea a sí misma cada 12 min y el workflow de GitHub Actions la despierta a las 9:10. Consume ≈ 535 h de las 750 h mensuales del plan. Fuera de la franja, el primer pedido espera 30 a 60 s. |
| RNF-06 | Robustez | Todo pedido HTTP saliente tiene timeout (15 s scraping/geocodificación, 30 s keep alive). Un evento con error no corta la ingesta. |
| RNF-07 | Cortesía con terceros | 1 s de pausa entre eventos scrapeados. User-Agent identificable para Nominatim. |
| RNF-08 | Seguridad | Las credenciales solo se leen del entorno (`DATABASE_URL`, `SCRAPER_TOKEN`), nunca del código. El token se compara en tiempo constante. |
| RNF-09 | Seguridad | La API pública es de solo lectura; la única escritura (ingesta) requiere token. CORS abierto a cualquier origen. |
| RNF-10 | Mantenibilidad | El esquema de la base se versiona con migraciones de Alembic y se aplica al arrancar el contenedor. |
| RNF-11 | Usabilidad | Interfaz en español, responsiva, con estados de carga, vacío y error. Fechas en formato `es-AR` y hora local. |
| RNF-12 | Portabilidad | El stack completo levanta con `docker compose up --build`. |
| RNF-13 | Convención | Código, identificadores, comentarios y textos de la interfaz en español. |

## 6. Restricciones y supuestos

- Una sola fuente de datos; el scraper depende de las clases CSS de agendade.com.ar
  (`link-block-11`, `div-block-192`, `div-block-243`, etc.). Un rediseño del sitio rompe la ingesta.
- La geocodificación usa el servicio público de Nominatim (máximo 1 pedido por segundo, sin SLA).
- PostgreSQL con la extensión PostGIS es obligatorio.
- La URL de la API queda fija en el build del frontend (`VITE_API_URL`).
- Se supone un volumen chico (cientos de conciertos): el frontend descarga la lista completa.

## 7. Limitaciones conocidas

| Limitación | Impacto |
|---|---|
| La búsqueda de lugar por nombre parcial (`ILIKE %nombre%`) puede asociar un evento al lugar equivocado si un nombre contiene a otro. | Marcador en el lugar incorrecto. |
| `ubicaciones.nombre` admite 50 caracteres; un lugar con nombre más largo hace fallar el alta y se pierde ese evento. | Pérdida de algunos eventos. |
| `capacidad_total` siempre se guarda en 0 (la fuente no la informa). | Campo sin uso real. |
| La ingesta corre dentro del pedido HTTP (varios minutos). | Si el cliente o un proxy corta por timeout, la ingesta igual continúa en el servidor, pero no se ve el resultado. |
| No hay tests automatizados. | Las regresiones se detectan a mano. |
