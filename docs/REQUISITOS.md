# Especificación de requisitos de software (SRS) — Concierto Finder

| Dato | Valor |
|---|---|
| Norma | Estructura y atributos según **ISO/IEC/IEEE 29148:2018** (especificación de requisitos de software) |
| Versión | 2.0 · 25/10/2026 |
| Origen | Ingeniería inversa del código ("as-built"), validada con un relevamiento documental ([relevamiento.md](relevamiento.md)) |
| Documentos relacionados | [Glosario y LEL](glosario-lel.md) · [Trazabilidad](trazabilidad.md) · [Contrato de la API](contrato-api.md) · [Estado del arte](estado-del-arte.md) · [Arquitectura](ARQUITECTURA.md) · [Casos de prueba](casos-de-prueba.md) |

## 1. Introducción

### 1.1 Propósito

Este documento especifica qué debe hacer Concierto Finder y con qué calidad. Está dirigido a quien
desarrolle, pruebe o mantenga el sistema, y a quien evalúe el proyecto. Cada requisito tiene un
identificador estable, que se usa en la [matriz de trazabilidad](trazabilidad.md), en los tests y en
los casos de prueba de aceptación.

### 1.2 Alcance

Concierto Finder es una cartelera web de **próximos conciertos en Buenos Aires y alrededores
(AMBA)**. Junta los eventos publicados en agendade.com.ar, los ubica en un mapa y permite
filtrarlos por artista y por cercanía a la ubicación del usuario, con acceso directo a la compra de
entradas y a cómo llegar. Una página de **métricas** muestra cómo se distribuyen los conciertos en el
tiempo y en el espacio, a partir del historial acumulado.

- **Dentro del alcance:** listado y mapa de conciertos de AMBA, filtros, ingesta automática desde una
  única fuente, limpieza de duplicados, historial de conciertos pasados y métricas sobre ese historial.
- **Fuera del alcance:** cuentas de usuario, venta de entradas (se redirige al vendedor), eventos
  fuera de AMBA, carga manual de eventos y notificaciones.

### 1.3 Definiciones, siglas y abreviaturas

Los términos del dominio (concierto vigente, lugar, ingesta, radio, etc.) están definidos en el
[Glosario y LEL](glosario-lel.md). Abreviaturas usadas en este documento:

| Sigla | Significado |
|---|---|
| RF | Requisito funcional |
| RN | Regla de negocio (restricción del dominio que los RF deben respetar) |
| RNF | Requisito no funcional |
| AMBA | Área Metropolitana de Buenos Aires (región definida en RN-01) |
| UAT | Prueba de aceptación de usuario ([casos-de-prueba.md](casos-de-prueba.md)) |

### 1.4 Referencias

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*.
- I. Sommerville, *Ingeniería de software*, cap. 4 (clasificación de los requisitos no funcionales).
- J. C. S. P. Leite, *Léxico Extendido del Lenguaje* (LEL), base del [glosario](glosario-lel.md).

### 1.5 Atributos de cada requisito

Cada requisito se redacta como "El sistema deberá…" y tiene estos atributos (29148, §5.2.8):

| Atributo | Valores |
|---|---|
| **Prioridad** | **E** = esencial (sin él, el producto no cumple su propósito) · **D** = deseable · **O** = opcional |
| **Verificación** | **P** = prueba automatizada (pytest) · **A** = prueba de aceptación (UAT) · **D** = demostración · **I** = inspección (revisión de código o configuración) · **N** = análisis |
| **Estado** | Implementado, salvo que se indique *Propuesto* |
| **Fuente** | **COD** = ingeniería inversa del código · **REL** = relevamiento (hallazgo HA-xx) · **D-x** = decisión de [ARQUITECTURA.md](ARQUITECTURA.md) · **OPS** = incidente de operación |

El detalle de fuente → diseño → código → prueba de cada requisito está en [trazabilidad.md](trazabilidad.md).

## 2. Descripción general

### 2.1 Perspectiva del producto

Es un sistema independiente con tres partes: un **frontend** web (React, en Cloudflare Pages), una
**API** (Flask, en Render) y una **base de datos** PostgreSQL + PostGIS (Supabase). Se apoya en
servicios externos: agendade.com.ar (fuente de eventos), Nominatim (geocodificación), OpenStreetMap
(mapa base), Google Maps (cómo llegar) y GitHub Actions (ingesta programada). Las vistas C4 están
en [ARQUITECTURA.md](ARQUITECTURA.md).

### 2.2 Funciones del producto

1. Consultar los conciertos vigentes en lista y mapa (RF-01 a RF-08).
2. Filtrar por artista y por cercanía (RF-09 a RF-16).
3. Incorporar conciertos desde la fuente de forma automática (RF-19 a RF-27).
4. Analizar el historial de conciertos con métricas (RF-28 a RF-36).

### 2.3 Actores y características de los usuarios

| Actor | Descripción |
|---|---|
| **Visitante** | Persona que entra al sitio público. Anónima, sin registro ni conocimientos técnicos. Usa sobre todo el teléfono (relevamiento, HA-03). |
| **Operador** | Quien despliega el sistema y configura el token `SCRAPER_TOKEN`. Puede disparar la ingesta a mano. |
| **GitHub Actions** | Ejecuta el workflow programado que despierta la API y dispara la ingesta cada 12 h. |
| **agendade.com.ar** | Sistema externo, fuente de los eventos (scraping de HTML). |
| **Nominatim (OpenStreetMap)** | Sistema externo de geocodificación de nombres de lugares. |
| **OpenStreetMap tiles** | Sistema externo que provee el mapa base. |
| **Google Maps** | Sistema externo al que se enlaza para "Cómo llegar". |

### 2.4 Restricciones

- Una sola fuente de datos. El scraper depende de las clases CSS de agendade.com.ar
  (`link-block-11`, `div-block-192`, `div-block-243`, etc.): un rediseño del sitio rompe la ingesta.
- La geocodificación usa el servicio público de Nominatim (máximo 1 pedido por segundo, sin SLA).
  Nominatim busca por el nombre que el lugar tiene en OpenStreetMap, así que muchas salas y estadios
  no aparecen con el nombre de la agenda ("Estadio Huracán" es "Estadio Tomás Adolfo Ducó"): esos
  lugares se cargan a mano en la tabla de lugares conocidos, con coordenadas verificadas en OSM.
- PostgreSQL con la extensión PostGIS es obligatorio.
- Todo corre en planes gratuitos (Render, Supabase, Cloudflare Pages, GitHub Actions), con sus límites
  de horas, tamaño y disponibilidad.
- La URL de la API queda fija en el build del frontend (`VITE_API_URL`).

### 2.5 Supuestos y dependencias

- El volumen es chico (cientos de conciertos): el frontend puede descargar la lista completa.
- agendade.com.ar permite el rastreo general (`robots.txt`: `Allow: /`). Desde el 22/10/2026 responde
  403 a los pedidos que salen de Render (ver §6).
- El navegador del visitante ofrece geolocalización (si no, el filtro por cercanía no está disponible).

## 3. Requisitos específicos

### 3.1 Interfaces externas

| ID | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|
| IE-01 | **Interfaz de usuario.** El sistema deberá ofrecer una interfaz web en español, con dos páginas: Conciertos (`/`) y Métricas (`/metricas`), accesibles desde el encabezado. | E | D | COD |
| IE-02 | **Interfaz de software (API).** El sistema deberá exponer una API REST en JSON, de solo lectura salvo la ingesta, según el [contrato de la API](contrato-api.md) (`openapi.yaml`). | E | P | COD |
| IE-03 | **Fuente de eventos.** El sistema deberá leer los eventos del HTML público de agendade.com.ar. | E | P | COD |
| IE-04 | **Geocodificación.** El sistema deberá obtener las coordenadas de los lugares desconocidos con la API de búsqueda de Nominatim, respetando su política de uso (User-Agent propio, RNF-07). | E | P | COD |
| IE-05 | **Mapa base y navegación.** El sistema deberá usar los mapas de OpenStreetMap y enlazar a Google Maps para las indicaciones de cómo llegar. | E | I | COD |
| IE-06 | **Comunicaciones.** Toda comunicación entre el navegador, la API y los servicios externos deberá usar HTTPS. | E | I | COD |

### 3.2 Requisitos funcionales

#### 3.2.1 Consulta de conciertos (visitante)

| ID | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|
| RF-01 | El sistema deberá mostrar todos los conciertos vigentes al cargar la página, en una lista y en un mapa. | E | P, A | COD |
| RF-02 | El sistema deberá agrupar la lista **por lugar** (coordenada exacta): una tarjeta por lugar con la cantidad de conciertos y una fila por concierto. | D | D | COD |
| RF-03 | El sistema deberá ordenar los conciertos de cada lugar por fecha y hora ascendentes, con los que no tienen fecha al final. | D | P | COD |
| RF-04 | Cada fila deberá mostrar: la fecha en un bloque tipo entrada (día de la semana, número y mes; "A confirmar" si no hay fecha); el artista; el nombre del evento, si difiere del artista; y la hora (`HH:MM h`; "Horario a confirmar" si no se conoce). Los conciertos de hoy y de mañana deberán llevar la etiqueta **Hoy** o **Mañana**. | E | D | COD |
| RF-05 | Cada fila deberá ofrecer, en este orden: **Entradas** (abre la URL de compra en otra pestaña, solo si existe), **Ver en mapa** y **Cómo llegar** (indicaciones de Google Maps; estas dos, solo si el lugar tiene coordenadas). En el teléfono, **Entradas** deberá ocupar todo el ancho y las otras dos acciones ir debajo, mitad y mitad. | E | D | COD |
| RF-06 | **Ver en mapa** deberá centrar el mapa en el lugar (zoom 15), abrir el popup del marcador, resaltar el concierto y desplazar la página hasta el mapa. | D | D | COD |
| RF-07 | El mapa deberá mostrar **un marcador por lugar**, con la cantidad de conciertos del lugar (también cuando es 1). El popup deberá listar los conciertos del lugar con fecha, hora y enlace a las entradas. En el tema claro, el mapa base deberá verse en gris suave para que se destaquen los datos. | E | D | COD |
| RF-08 | Una portada deberá mostrar, según los filtros aplicados, la cantidad de conciertos, de lugares y de conciertos de hoy (esta última, solo si hay). | O | D | COD |

#### 3.2.2 Filtros (visitante)

| ID | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|
| RF-09 | El sistema deberá permitir buscar por **artista**, por coincidencia parcial, sin distinguir mayúsculas ni acentos ("paez" encuentra "Páez"). | E | A | COD, REL HA-04 |
| RF-10 | Mientras se escribe, el buscador deberá sugerir hasta 8 artistas existentes. Enter elige la primera sugerencia; Escape o un clic afuera cierran la lista; un botón limpia la búsqueda. Si no hay coincidencias, deberá indicar "Sin resultados". | D | D | COD |
| RF-11 | El sistema deberá permitir activar y desactivar el **filtro por cercanía** con un mismo botón, usando la geolocalización del navegador. Si el permiso está bloqueado, deberá explicar cómo habilitarlo y seguir mostrando la lista sin filtrar. | E | A | COD, REL HA-02 |
| RF-12 | Con la ubicación activa, el sistema deberá mostrar solo los conciertos a una distancia en línea recta menor o igual al radio elegido. Los conciertos sin coordenadas no se excluyen. | E | A | COD, REL HA-02 |
| RF-13 | El radio deberá elegirse con un slider de 1 a 40 km (inicial 5 km) o con atajos de 5, 20 y 40 km. El mapa deberá dibujar la posición del usuario y el círculo del radio, y encuadrarse en él. | E | A | COD |
| RF-14 | Los filtros de artista y de radio deberán combinarse (Y lógico) y aplicarse 300 ms después del último cambio. | D | A | COD |
| RF-15 | Si no hay resultados, el sistema deberá mostrar un estado vacío con un mensaje que invite a ajustar la búsqueda. | E | A | COD |
| RF-16 | Si la API falla, el sistema deberá mostrar un estado de error con el botón **Reintentar**. Mientras carga, deberá mostrar tarjetas de carga con la forma de la lista y, si tarda más de 4 s, avisar que el servidor se está despertando (RNF-05). La página de métricas deberá dar el mismo aviso. | E | D | COD |

#### 3.2.3 Ingesta y mantenimiento de datos (operador / sistema)

Los números RF-17 y RF-18 no se usan: quedaron libres en una versión anterior y no se reasignan.

| ID | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|
| RF-19 | El sistema deberá ejecutar la ingesta automáticamente cada 12 h (9:10 y 21:10, hora argentina) con un workflow de GitHub Actions, que primero despierta la API. | E | I | COD |
| RF-19 bis | Al arrancar, si la base no tiene conciertos, la API deberá ejecutar la ingesta en segundo plano. Nunca deberán correr dos ingestas a la vez: un pedido concurrente recibe 409. | E | I | COD |
| RF-20 | La ingesta deberá dispararse con `GET` o `POST /ingestar_agendade` y exigir el token `SCRAPER_TOKEN`. Sin token configurado, el endpoint deberá quedar deshabilitado (503). | E | P | COD |
| RF-21 | La ingesta deberá recorrer las páginas 1 a 5 de la agenda y extraer de cada evento: título, artista (campo "ARTISTA" o "SHOW"; si falta, el título), lugar ("VENUE" + "UBICACIÓN"), fecha, hora y URL de compra. | E | P | COD |
| RF-22 | El lugar deberá buscarse entre los ya registrados por nombre (coincidencia parcial, sin distinguir mayúsculas). Si no existe, sus coordenadas deberán buscarse primero en la tabla de lugares conocidos y después en Nominatim, limitado a Argentina. El lugar se registra con su punto y un enlace a Google Maps. | E | P | COD, OPS |
| RF-23 | El sistema deberá guardar solo los conciertos cuyo lugar cae dentro de AMBA (RN-01). Los lugares no encontrados o fuera de AMBA se descartan sin volver a consultarlos en la misma corrida, y el motivo queda en el log. | E | P | COD |
| RF-24 | El sistema no deberá insertar conciertos que ya existen (RN-03). | E | P | COD |
| RF-25 | La respuesta de la ingesta deberá devolver todos los eventos leídos, incluidos los descartados. | D | I | COD |
| RF-26 | Cada 24 h, el sistema deberá borrar los conciertos duplicados, conservando el de menor id. | D | P | COD |
| RF-26 bis | El sistema **no** deberá borrar los conciertos pasados: quedan en la base como historial, que es la base de las métricas. Los listados públicos devuelven solo los vigentes (RN-02). | E | P | D-8 |
| RF-27 | El backend deberá exponer `/ubicaciones` (lugares con coordenadas) y `/conciertos_cerca` (búsqueda espacial en el servidor). El frontend actual no los usa. | O | P | COD |
| RF-37 | **Propuesto.** El sistema deberá detectar los conciertos suspendidos o reprogramados en la fuente, marcarlos con un estado (vigente, suspendido o reprogramado) y no mostrar los suspendidos como vigentes. | E | — | REL HA-05 |

#### 3.2.4 Métricas (visitante)

| ID | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|
| RF-28 | El sistema deberá ofrecer una página **Métricas** (`/metricas`) con indicadores y gráficos calculados sobre todo el historial (vigentes y pasados). | D | A | COD |
| RF-29 | Deberá mostrar indicadores de: total de conciertos, vigentes, pasados, lugares distintos, artistas distintos y **concentración** (porcentaje de conciertos en los 5 lugares más activos). Con menos de 4 meses de historial, un aviso deberá explicar desde cuándo se guarda. | D | P, A | COD |
| RF-30 | Deberá mostrar **conciertos por mes** en un gráfico de área que incluya los meses sin conciertos y marque el mes actual con una línea vertical y una leyenda fuera del dibujo. | D | P | COD |
| RF-31 | Deberá mostrar los rankings de los 10 **lugares más activos** y los 10 **artistas que más tocan**, en barras horizontales con la posición y el valor, cada ranking con su color. | D | P | COD |
| RF-32 | Deberá mostrar: **próximos 14 días** (columnas por día, fin de semana en otro color, con leyenda); **¿cuándo hay más conciertos?** (grilla de día de la semana por franja horaria, RN-13); y **anticipación** (histograma de días entre el anuncio y la fecha, RN-14, con la mediana). | D | P | COD |
| RF-33 | Deberá mostrar un **mapa de calor** de los lugares, con una escala de un solo color que empiece transparente, un punto por lugar y una leyenda de "menos" a "más conciertos". | D | P | COD |
| RF-34 | Un filtro de período (Todo, Últimos 12 meses, Últimos 3 meses, Próximos o fechas a medida) deberá actualizar todas las métricas. Si "desde" es posterior a "hasta", deberá avisarlo y no consultar. "Próximos 14 días" y "Conciertos nuevos por día" no dependen del período. | D | P, A | COD |
| RF-35 | Deberá mostrar una sección **Calidad de los datos**: porcentaje de conciertos con fecha, hora, link de entradas y lugar en el mapa (RN-15), y los conciertos nuevos por día de los últimos 30 días. | D | P | COD |
| RF-36 | Las métricas deberán exponerse también como API REST de solo lectura bajo `/api/metricas/...` ([contrato](contrato-api.md)). | O | P | D-10 |

### 3.3 Reglas de negocio

| ID | Regla | Verif. | Fuente |
|---|---|---|---|
| RN-01 | **Región AMBA**: latitud −35,15 a −34,2 y longitud −58,95 a −57,7. La fuente de verdad está en `app/services/geocoding_service.py` y se replica en `web/src/constantes.js`. | P | COD |
| RN-02 | Un concierto es **vigente** si su fecha es hoy (hora de Argentina) o posterior, o si no tiene fecha. La vigencia se deriva de la fecha en cada consulta: no hay columna de estado. | P, A | D-8 |
| RN-03 | La identidad de un concierto, para deduplicar, es (nombre, artista, fecha, lugar), con los nulos considerados iguales. | P | COD |
| RN-04 | La fecha de la fuente viene como `DD/MM/AA` o `DD/MM/AAAA`, y la hora como `HH:MM` o `HH:MM:SS`. Si no se puede interpretar, queda nula. | P | COD |
| RN-05 | Nombre y artista se recortan a 50 caracteres (largo de la columna). | P | COD |
| RN-06 | La navegación del mapa está limitada a Argentina, y solo se dibujan marcadores dentro de AMBA. | I | COD |
| RN-07 | El centro inicial del mapa es el Obelisco (−34,6037; −58,3816), con zoom 11. | I | COD |
| RN-08 | El filtro de las métricas (`desde` y `hasta`) se aplica sobre la fecha del concierto e incluye los dos extremos. Sin filtro cuentan todos los conciertos; con filtro, los que no tienen fecha quedan afuera. | P | COD |
| RN-09 | Las métricas por lugar, el mapa de calor y las distancias excluyen los conciertos sin lugar o sin coordenadas. | P | COD |
| RN-10 | Las distancias de las métricas son geodésicas y en línea recta, en km, desde el Obelisco por defecto. Los rangos son semiabiertos `[desde, hasta)` y el último no tiene tope. | P | COD |
| RN-11 | Dos nombres son el **mismo artista** si coinciden sin distinguir mayúsculas, acentos ni espacios en los extremos. En los rankings se muestra la escritura más frecuente. | P | COD |
| RN-12 | **Cobertura:** las métricas solo reflejan lo publicado en agendade.com.ar (primeras 5 páginas) dentro de AMBA, desde que se conserva el historial. | I | COD |
| RN-13 | Las **franjas horarias** son: Día (6 a 18), 18 a 20, 20 a 22, 22 a 24 y Trasnoche (0 a 6). | P | COD |
| RN-14 | **Anticipación** = fecha del concierto − fecha en que la ingesta lo encontró (`creado_en`, hora argentina). Solo cuentan los conciertos con fecha, encontrados desde la migración 0005 y antes de su fecha. | P | COD |
| RN-15 | Un concierto tiene **datos incompletos** si le falta la fecha, la hora, el link de entradas (nulo o vacío) o un lugar con coordenadas. | P | COD |

### 3.4 Requisitos no funcionales (clasificación de Sommerville)

Se clasifican en los tres grupos de Sommerville: requisitos **del producto** (cómo se comporta el
software), **de la organización** (políticas y procedimientos del desarrollo y la operación) y
**externos** (factores ajenos al sistema y a su proceso de desarrollo).

#### 3.4.1 Requisitos del producto

| ID | Subtipo | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|---|
| RNF-11 | Usabilidad | La interfaz deberá estar en español, ser responsiva y tener estados de carga, vacío y error. Deberá mostrar las fechas en formato `es-AR` y la hora local, sin scroll horizontal desde 320 px de ancho. | E | D, A | COD, REL HA-03 |
| RNF-19 | Usabilidad (accesibilidad) | Cada gráfico deberá tener sus datos en una tabla para lectores de pantalla, y el texto sobre colores deberá elegirse por contraste WCAG. Los colores de los gráficos deberán validarse en los dos temas (claro y oscuro). | D | I | D-14 |
| RNF-01 | Eficiencia: rendimiento | `/conciertos` deberá resolverse en una sola consulta SQL (con JOIN), filtrada y ordenada en la base. Las columnas `conciertos.fecha` y `conciertos.ubicacion` deberán tener índice. | E | P | COD |
| RNF-02 | Eficiencia: rendimiento | Los filtros deberán aplicarse en el navegador, sin pedidos al servidor. | E | I | D-1 |
| RNF-03 | Eficiencia: rendimiento | Las respuestas de conciertos y de métricas deberán poder cachearse 5 minutos (`Cache-Control: public, max-age=300`). Los assets del frontend, 1 año (llevan hash). | D | P | COD |
| RNF-15 | Eficiencia: rendimiento | Cada métrica deberá calcularse en la base con una sola consulta y devolver solo resultados agregados. La página de métricas deberá descargarse aparte (code splitting). | D | P, I | D-10, D-11 |
| RNF-04 | Eficiencia: espacio y capacidad | El pool de conexiones a la base deberá ser de 3 + 2 de desborde, con 30 s de espera; si se agota, la API deberá responder 503. | E | I | COD |
| RNF-05 | Confiabilidad: disponibilidad | La API deberá estar despierta de 9:00 a 2:00 (hora argentina, configurable), con un keep alive cada 12 min y el despertar del workflow a las 9:10. Debe consumir menos de las 750 h mensuales del plan gratuito (≈ 535 h). | E | P | COD |
| RNF-06 | Confiabilidad: robustez | Todo pedido HTTP saliente deberá tener timeout (15 s el scraping y la geocodificación, 30 s el keep alive). Un evento con error no deberá cortar la ingesta. | E | P, I | COD |
| RNF-20 | Confiabilidad: observabilidad | Una ingesta que no lee ningún evento deberá terminar en error visible (workflow en rojo) y registrar la causa en el log. | E | P | OPS |
| RNF-08 | Protección (seguridad) | Las credenciales (`DATABASE_URL`, `SCRAPER_TOKEN`) solo deberán leerse del entorno, nunca del código. El token deberá compararse en tiempo constante. | E | P, I | COD |
| RNF-09 | Protección (seguridad) | La API pública deberá ser de solo lectura: la única escritura (la ingesta) exige token. Las tablas deberán tener RLS, y los roles de la API automática de Supabase (`anon`, `authenticated`) no deberán tener permisos. | E | P | D-13 |

#### 3.4.2 Requisitos de la organización

| ID | Subtipo | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|---|
| RNF-12 | Ambiental | El sistema completo deberá levantarse con `docker compose up --build`, y producción deberá funcionar en planes gratuitos (Render, Supabase, Cloudflare Pages). | E | D | COD |
| RNF-10 | Operacional | El esquema de la base deberá versionarse con migraciones de Alembic, que se aplican al arrancar el contenedor. | E | P | COD |
| RNF-13 | De desarrollo | El código, los identificadores, los comentarios y los textos de la interfaz deberán estar en español. | D | I | COD |
| RNF-14 | De desarrollo | El backend deberá tener tests automatizados contra PostgreSQL + PostGIS real. Lints, tests y build del frontend deberán correr en cada PR y en cada push a `main`. Cada cambio deberá entrar por una rama y un PR. | E | I | D-9 |

#### 3.4.3 Requisitos externos

| ID | Subtipo | Requisito | Prior. | Verif. | Fuente |
|---|---|---|---|---|---|
| RNF-07 | Ético | El sistema deberá hacer una pausa de 1 s entre eventos scrapeados y identificarse en todo pedido saliente con un User-Agent propio, con link al repositorio. | E | I | COD, OPS |
| RNF-18 | Ético | El sistema deberá respetar el `robots.txt` de la fuente y **no evadir** sus bloqueos (cambio de IP, proxies o User-Agent de navegador). Ante un bloqueo, se pide acceso a la fuente. | E | I | OPS |
| RNF-16 | Legislativo: privacidad | El sistema no deberá guardar datos personales. La ubicación del visitante solo deberá usarse en su navegador y nunca enviarse al servidor (Ley 25.326 de Protección de Datos Personales). | E | I | COD |
| RNF-17 | Regulatorio: licencias | El sistema deberá atribuir los datos de OpenStreetMap ("© OpenStreetMap", licencia ODbL) y la fuente de los eventos (agendade.com.ar), y enlazar cada evento a su vendedor de entradas. | E | I | COD |

## 4. Verificación

| Método | Dónde | Alcance |
|---|---|---|
| Prueba automatizada (P) | `tests/` (pytest contra PostGIS), en CI en cada PR | Repositorios, rutas, métricas, ingesta, migraciones y seguridad |
| Prueba de aceptación (A) | [casos-de-prueba.md](casos-de-prueba.md) (CP-01 a CP-10) | Búsqueda por cercanía y métricas sobre la app publicada |
| Demostración (D) | Uso de la app publicada en escritorio y teléfono | Comportamiento visual del frontend, que no tiene tests automatizados |
| Inspección (I) | Revisión de código, configuración y workflows | Requisitos de organización, éticos y legales |

La cobertura por requisito está en la [matriz de trazabilidad](trazabilidad.md).

## 5. Restricciones y supuestos

Ver §2.4 y §2.5.

## 6. Historial de versiones

| Versión | Fecha | Cambios |
|---|---|---|
| 1.x | 08/10 a 18/10/2026 | Especificación obtenida por ingeniería inversa del código, actualizada con cada feature. |
| 2.0 | 25/10/2026 | Estructura según ISO/IEC/IEEE 29148: atributos de prioridad, verificación y fuente; requisitos redactados como "deberá"; interfaces externas (IE); no funcionales clasificados según Sommerville; nuevos RNF-16 a RNF-20 y RF-37 (propuesto, del relevamiento). |

## 7. Limitaciones conocidas

| Limitación | Impacto |
|---|---|
| Desde el 22/10/2026, agendade.com.ar responde **403** a los pedidos que salen de Render (protección contra bots de Cloudflare); desde otras conexiones responde normalmente. El `robots.txt` del sitio permite el rastreo general. | La ingesta automática no trae conciertos nuevos hasta que la fuente habilite el acceso: se le pide por su formulario de contacto. No se evade el bloqueo (RNF-18). |
| La búsqueda de lugar por nombre parcial (`ILIKE %nombre%`) puede asociar un evento al lugar equivocado si un nombre contiene a otro. | Marcador en el lugar incorrecto. |
| `ubicaciones.nombre` admite 50 caracteres; un lugar con nombre más largo hace fallar el alta y se pierde ese evento. | Pérdida de algunos eventos. |
| Muchos bares y salas chicas de AMBA (por ejemplo Lucille, La Tangente, Lalalá o CC Richards) no están en OpenStreetMap con ningún nombre, así que Nominatim no los encuentra y sus conciertos se descartan. La tabla de lugares conocidos solo cubre los lugares agregados a mano. | Faltan conciertos de lugares chicos. Se recuperan de a uno: el log dice qué lugar no se encontró, y se agrega a `lugares_conocidos.py` con la coordenada de su dirección (ver `OPERACION.md` §8). |
| `capacidad_total` siempre se guarda en 0 (la fuente no la informa). | Campo sin uso real. |
| La ingesta corre dentro del pedido HTTP (unos 30 minutos). | Si el cliente o un proxy corta por timeout, la ingesta sigue en el servidor, pero no se ve el resultado. |
| El frontend no tiene tests automatizados. | Sus requisitos se verifican por demostración y con los casos de aceptación. |
| Un concierto cancelado o reprogramado queda como vigente hasta su fecha, y después en el historial. Una reprogramación queda como dos conciertos. | Las métricas cuentan de más esos casos. Se resuelve con RF-37 (propuesto). |
