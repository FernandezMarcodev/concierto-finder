# Glosario y Léxico Extendido del Lenguaje (LEL)

El **LEL** (Leite) registra el vocabulario del dominio tal como lo usan las personas que lo
habitan, antes de pensar en la solución. Cada símbolo tiene:

- **Clasificación:** *sujeto* (quien actúa), *objeto* (con lo que se actúa), *verbo* (una acción) o
  *estado* (una situación en la que puede estar algo).
- **Noción:** qué es; su denotación.
- **Impacto:** qué consecuencias tiene o qué se hace con él; su connotación.

Las palabras en **negrita** dentro de una noción o un impacto son otros símbolos del LEL (principio
de circularidad). Al final hay un glosario técnico con los términos de la implementación.

## 1. Sujetos

### Visitante
- **Clasificación:** sujeto.
- **Noción:** persona que entra a la **cartelera** para ver qué **conciertos** hay. Es anónima: no se
  registra ni inicia sesión.
- **Impacto:**
  - Busca por **artista** y **filtra por cercanía**.
  - Abre el link de **entradas** o pide cómo llegar a un **lugar**.
  - Consulta las **métricas**.

### Operador
- **Clasificación:** sujeto.
- **Noción:** persona que despliega y mantiene el sistema.
- **Impacto:**
  - Configura el **token de ingesta**.
  - Puede disparar una **ingesta** a mano.
  - Agrega **lugares conocidos** cuando el log informa un **descarte**.

### Fuente
- **Sinónimo:** agendade.com.ar.
- **Clasificación:** sujeto (externo).
- **Noción:** sitio web que publica la agenda de **eventos** musicales de Argentina. Es el único
  origen de los datos.
- **Impacto:**
  - La **ingesta** lee sus primeras 5 páginas.
  - Si cambia su HTML o bloquea los pedidos, no entran **conciertos** nuevos.

### Geocodificador
- **Sinónimo:** Nominatim.
- **Clasificación:** sujeto (externo).
- **Noción:** servicio de OpenStreetMap que convierte el nombre de un **lugar** en coordenadas.
- **Impacto:**
  - Se lo consulta cuando el **lugar** no está registrado ni es un **lugar conocido**.
  - Si no encuentra el nombre, el **concierto** queda **descartado**.

## 2. Objetos

### Evento
- **Clasificación:** objeto.
- **Noción:** publicación de la **fuente** sobre un show: título, **artista**, **lugar**, fecha, hora y
  link de **entradas**. Puede ser de cualquier parte del país.
- **Impacto:** la **ingesta** lo lee y, si su **lugar** está en el **AMBA**, lo convierte en un
  **concierto**.

### Concierto
- **Clasificación:** objeto.
- **Noción:** show de un **artista** en un **lugar** del **AMBA**, en una fecha y hora. Es un
  **evento** que superó la **ingesta**. Se identifica por nombre, **artista**, fecha y **lugar**.
- **Impacto:**
  - Mientras está **vigente**, aparece en la **cartelera**.
  - Cuando pasa a **pasado**, queda en el **historial** y alimenta las **métricas**.

### Artista
- **Clasificación:** objeto.
- **Noción:** quien toca en un **concierto**: un solista, una banda o un ciclo. Puede venir escrito de
  distintas maneras ("Sofía Ríos", "sofia rios").
- **Impacto:**
  - El **visitante** lo busca sin importar tildes ni mayúsculas.
  - Las **métricas** agrupan sus variantes de escritura.

### Lugar
- **Sinónimos:** ubicación, venue, sala.
- **Clasificación:** objeto.
- **Noción:** sitio donde se hace un **concierto** (estadio, teatro, bar, centro cultural), con nombre,
  localidad y coordenadas.
- **Impacto:**
  - Se **geocodifica** una sola vez y se reutiliza.
  - En el mapa es un marcador con la cantidad de **conciertos**.
  - Si está fuera del **AMBA**, sus **eventos** quedan **descartados**.

### Lugar conocido
- **Clasificación:** objeto.
- **Noción:** **lugar** del **AMBA** con coordenadas cargadas a mano y verificadas en OpenStreetMap,
  porque el **geocodificador** no lo encuentra con el nombre que usa la **fuente** ("Estadio Huracán"
  en OSM es "Estadio Tomás Adolfo Ducó").
- **Impacto:** se consulta antes que el **geocodificador** y evita **descartar** **conciertos**
  importantes.

### AMBA
- **Clasificación:** objeto.
- **Noción:** Área Metropolitana de Buenos Aires: la Ciudad y los partidos que la rodean, incluido
  La Plata. En el sistema es un rectángulo de coordenadas (latitud −35,15 a −34,2; longitud −58,95
  a −57,7).
- **Impacto:** define qué **eventos** se convierten en **conciertos**.

### Cartelera
- **Clasificación:** objeto.
- **Noción:** página principal: lista y mapa de los **conciertos** **vigentes**, agrupados por
  **lugar**.
- **Impacto:** es lo que ve el **visitante** al entrar. Se actualiza con cada **ingesta**.

### Radio
- **Clasificación:** objeto.
- **Noción:** distancia máxima, en km y en línea recta, desde la ubicación del **visitante** (de 1 a
  40 km).
- **Impacto:** al **filtrar por cercanía**, la **cartelera** muestra solo los **conciertos** dentro
  del radio.

### Entradas
- **Clasificación:** objeto.
- **Noción:** link a la ticketera que vende el acceso a un **concierto**. Cada **concierto** puede
  venderse en una plataforma distinta.
- **Impacto:** el **visitante** compra fuera del sistema. Si falta, el **concierto** tiene **datos
  incompletos**.

### Historial
- **Clasificación:** objeto.
- **Noción:** conjunto de todos los **conciertos** guardados, **vigentes** y **pasados**.
- **Impacto:** es la base de las **métricas**. Nada se borra al pasar la fecha.

### Métrica
- **Clasificación:** objeto.
- **Noción:** indicador o gráfico calculado sobre el **historial** (por ejemplo, **conciertos** por
  mes, **lugares** más activos, **anticipación**).
- **Impacto:** el **visitante** la filtra por **período**.

### Período
- **Clasificación:** objeto.
- **Noción:** rango de fechas ("desde" y "hasta", inclusivos) sobre el que se calculan las
  **métricas**.
- **Impacto:** con un período, los **conciertos** sin fecha quedan afuera. Si "desde" es posterior a
  "hasta", no se consulta.

### Franja horaria
- **Clasificación:** objeto.
- **Noción:** tramo del día en que empieza un **concierto**: Día (6 a 18), 18 a 20, 20 a 22, 22 a 24 y
  Trasnoche (0 a 6).
- **Impacto:** organiza la grilla de "¿Cuándo hay más conciertos?".

### Anticipación
- **Clasificación:** objeto.
- **Noción:** días entre que la **ingesta** encontró un **concierto** y su fecha.
- **Impacto:** muestra con cuánto tiempo se anuncian los shows. Solo se mide desde que existe la
  fecha de alta (migración 0005).

### Token de ingesta
- **Clasificación:** objeto.
- **Noción:** clave secreta compartida entre el **operador**, el workflow programado y la API.
- **Impacto:** sin el token, nadie puede disparar una **ingesta**.

## 3. Verbos

### Ingestar
- **Sinónimo:** ingesta.
- **Clasificación:** verbo.
- **Noción:** leer los **eventos** de la **fuente**, ubicar su **lugar** y guardar los **conciertos**
  nuevos del **AMBA**. Corre cada 12 h.
- **Impacto:**
  - Crea **conciertos** y **lugares**.
  - **Descarta** **eventos**.
  - **Deduplica**.
  - Si falla, la **cartelera** no se actualiza.

### Geocodificar
- **Clasificación:** verbo.
- **Noción:** obtener las coordenadas de un **lugar** a partir de su nombre. Se busca primero entre
  los **lugares conocidos** y después en el **geocodificador**.
- **Impacto:** el **lugar** queda registrado con su punto, o el **evento** queda **descartado**.

### Deduplicar
- **Clasificación:** verbo.
- **Noción:** evitar que el mismo **concierto** (mismo nombre, **artista**, fecha y **lugar**) se guarde
  dos veces.
- **Impacto:**
  - La **ingesta** no inserta repetidos.
  - Una limpieza diaria borra los que se hayan colado.

### Filtrar por cercanía
- **Clasificación:** verbo.
- **Noción:** mostrar solo los **conciertos** a un **radio** de la ubicación del **visitante**,
  obtenida por el navegador.
- **Impacto:**
  - La ubicación nunca sale del navegador.
  - Si el permiso está bloqueado, se explica cómo habilitarlo.

### Despertar
- **Sinónimo:** keep alive.
- **Clasificación:** verbo.
- **Noción:** mantener la API activa con pedidos periódicos, porque el plan gratuito la duerme tras
  15 min sin tráfico.
- **Impacto:** solo se hace de 9 a 2 h, para no agotar las horas mensuales del plan.

## 4. Estados

### Vigente
- **Clasificación:** estado (de un **concierto**).
- **Noción:** su fecha es hoy (hora argentina) o posterior, o no tiene fecha.
- **Impacto:** aparece en la **cartelera**. Se calcula en cada consulta: no se guarda.

### Pasado
- **Clasificación:** estado (de un **concierto**).
- **Noción:** su fecha ya ocurrió.
- **Impacto:** sale de la **cartelera**, pero queda en el **historial** para las **métricas**.

### Descartado
- **Clasificación:** estado (de un **evento**).
- **Noción:** **evento** que no se guardó, porque su **lugar** no se pudo **geocodificar** o está
  fuera del **AMBA**.
- **Impacto:** el log registra el motivo. Si el **lugar** era del **AMBA**, el **operador** puede
  agregarlo como **lugar conocido**.

### Con datos incompletos
- **Clasificación:** estado (de un **concierto**).
- **Noción:** le falta la fecha, la hora, el link de **entradas** o un **lugar** con coordenadas.
- **Impacto:** cuenta en la métrica de calidad de los datos.

### Suspendido / reprogramado (propuesto)
- **Clasificación:** estado (de un **concierto**).
- **Noción:** la **fuente** canceló el show o le cambió la fecha.
- **Impacto:** hoy el sistema no lo detecta y el **concierto** sigue **vigente** (RF-37, propuesto).

## 5. Glosario técnico

| Término | Definición |
|---|---|
| Alembic | Herramienta de migraciones de esquema para SQLAlchemy: cada cambio de la base es un archivo versionado. |
| API REST | Interfaz HTTP que expone recursos en JSON. La de este sistema está especificada en [contrato-api.md](contrato-api.md). |
| CI | Integración continua: GitHub Actions corre los lints, los tests y el build en cada PR. |
| Cloudflare | Red que protege y acelera sitios web. Su protección contra bots puede bloquear pedidos automáticos (HTTP 403). |
| CORS | Mecanismo del navegador que permite que una web pida datos a otro dominio. La API lo permite para cualquier origen. |
| Geography / SRID 4326 | Tipo de PostGIS y sistema de coordenadas WGS84 (latitud y longitud en grados) que permiten medir distancias sobre la Tierra. |
| Haversine | Fórmula de la distancia en línea recta entre dos puntos de una esfera. La usa el frontend para el **radio**. |
| Ingeniería inversa | Obtener la especificación a partir del código existente. |
| OpenAPI | Estándar para describir una API REST en un archivo legible por personas y herramientas (`openapi.yaml`). |
| PostGIS | Extensión de PostgreSQL para datos geográficos. |
| RLS | Row Level Security: seguridad a nivel de fila de PostgreSQL. |
| Scraping | Leer datos del HTML de un sitio web de forma automática. |
| UAT | User Acceptance Testing: pruebas de aceptación sobre la app publicada. |
| User-Agent | Encabezado HTTP con el que un programa se identifica ante un servidor. |
