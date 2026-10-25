# Relevamiento

> **Estado.** Relevamiento documental (fuentes secundarias y datos del sistema): **completo**, 25/10/2026.
> Entrevistas con usuarios: **pendientes**. La guía está en el anexo y valida lo que los datos no
> alcanzan a responder (H2 y H6).

## 1. Objetivo y alcance

Concierto Finder ya tiene un MVP publicado. Este relevamiento es **de validación**: busca evidencia
de que los requisitos implementados responden a un problema real, y detectar necesidades que el
sistema todavía no cubre.

Preguntas que tiene que responder:

1. ¿La información sobre recitales está dispersa? ¿Cuánto?
2. ¿La cercanía influye al elegir un recital?
3. ¿Qué información necesita una persona para decidir si va?
4. ¿Las suspensiones y reprogramaciones son un problema real?

Fuera de alcance: precios, compra de entradas dentro de la app y recomendaciones personalizadas.

## 2. Método

Se combinaron cuatro técnicas de **fuentes secundarias**. Ninguna requiere entrevistar, y
cruzarlas entre sí (triangulación) reduce el sesgo de cada una por separado.

| Técnica | Fuente | Qué aporta |
|---|---|---|
| T1. Estadísticas oficiales | Encuesta Nacional de Consumos Culturales 2022-2023 (Ministerio de Cultura / SInCA) y Censo 2022 (INDEC) | Cuánta gente va a recitales, quiénes van y dónde vive la población del AMBA. |
| T2. Análisis de datos propios | Los 216 conciertos vigentes publicados y las métricas de la API (25/10/2026) | Dónde se concentran los shows y cuántas plataformas de entradas usan. |
| T3. Benchmark de soluciones existentes | Agendas de medios (Indie Hoy, Rolling Stone, Buenos Aires Secreta) y ticketeras | Cómo se informa hoy la gente y qué le falta a cada fuente. |
| T4. Análisis de casos | Fallos judiciales y notas sobre shows reprogramados o suspendidos | Qué pasa cuando un show cambia, y si el problema existe. |

**Limitación del método.** Las fuentes secundarias dicen *qué pasa*, pero no siempre *qué
piensa* la persona. Por eso las preguntas sobre preferencias (cómo se piensa "cerca") quedan para
las entrevistas.

## 3. Hallazgos

### HA-01 · Las entradas están repartidas en decenas de plataformas (T2)

Los 216 conciertos vigentes venden entradas en **36 dominios distintos**: **32 plataformas de
venta** (Passline y Venti aparecen con dos dominios cada una), más Instagram y un formulario de
Google. Por cantidad de conciertos:

| Plataforma | Conciertos |
|---|---|
| Passline | 53 |
| Movistar Arena | 40 |
| Livepass | 17 |
| Venti | 17 |
| TuEntrada | 15 |
| AllAccess | 15 |
| Las otras 26, más Instagram y Google | 59 |

Quien quiera ver "todo lo que hay" tendría que revisar más de 30 sitios.

### HA-02 · La oferta está en CABA; la población, en el conurbano (T1 + T2)

| | Población (Censo 2022) | Conciertos publicados |
|---|---|---|
| CABA | 3,12 millones (22 %) | 185 (86 %) |
| 24 partidos del conurbano | 10,87 millones (78 %) | 7 (3 %) |
| La Plata | — | 24 (11 %) |

**Cerca de 8 de cada 10 personas del AMBA viven en el conurbano, pero casi 9 de cada 10 shows son
en CABA.** Para la mayoría, ir a un recital implica viajar, así que la distancia pesa en la
decisión. Ejemplo medido en el UAT ([casos-de-prueba.md](casos-de-prueba.md), CP-02): desde Merlo
no hay ningún concierto a 5 km o menos, y a 20 km hay 6.

### HA-03 · Ir a recitales es un consumo masivo, y sobre todo joven (T1)

Según la ENCC 2022-2023, el **29 %** de la población fue a ver música en vivo en el último año.
Entre los jóvenes de 18 a 29 años la cifra sube a **4 de cada 10**. La misma encuesta señala que el
celular es el dispositivo más usado para escuchar música, lo que respalda el diseño adaptado a
teléfonos (RNF-11).

### HA-04 · Las agendas de los medios son notas, no buscadores (T3)

Medios como Indie Hoy, Rolling Stone o Buenos Aires Secreta publican agendas como **notas
editoriales** (los shows del fin de semana, las visitas internacionales, recomendaciones de
lugares). Sirven para descubrir, pero son una selección y no se pueden filtrar por zona ni por
artista. Las ticketeras solo muestran lo que venden ellas.

### HA-05 · Las reprogramaciones existen y generan reclamos (T4)

- Un fallo obligó a Ticketek a indemnizar a dos personas por la reprogramación de un show de
  Madonna. El reclamo incluía que el reintegro de las entradas se demoró.
- Hay notas que explican qué derechos tiene el público cuando un show se suspende o cambia de
  fecha, y anuncios de reprogramaciones con instrucciones de devolución en la ticketera.

Hoy Concierto Finder **no detecta** estos cambios (REQUISITOS §7): un show suspendido sigue
publicado hasta su fecha.

### HA-06 · La fuente de datos es completa en lo que el sistema muestra (T2)

De los 305 conciertos guardados, ninguno está sin fecha, sin hora, sin link de entradas ni sin
lugar en el mapa (métrica de calidad, RN-15). Los datos que el sistema muestra por concierto
(fecha, hora, lugar y entradas) siempre están disponibles.

## 4. Validación de hipótesis

| ID | Hipótesis | Evidencia | Resultado |
|---|---|---|---|
| H1 | La información está dispersa en muchas fuentes. | HA-01, HA-04 | **Confirmada** |
| H2 | La cercanía influye al elegir un recital. | HA-02 (evidencia indirecta: la mayoría tiene que viajar) | **Parcial**: falta preguntar si la distancia cambia la decisión |
| H3 | Lo mínimo para decidir es fecha, hora, lugar y link de entradas. | HA-06 muestra que esos datos siempre están; no prueba que alcancen | **Sin evidencia suficiente**: entrevistas |
| H4 | Buscar por artista tiene que tolerar tildes y mayúsculas. | No relevado con fuentes secundarias | **Pendiente** |
| H5 | Las suspensiones y reprogramaciones son un problema real. | HA-05 | **Confirmada** |
| H6 | "Cerca" se piensa en tiempo de viaje más que en km en línea recta. | No relevado | **Pendiente**: entrevistas |

## 5. Requisitos que surgen

| ID | Requisito | Hallazgo | ¿Existe? | Prioridad |
|---|---|---|---|---|
| RQ-01 | Reunir en un solo lugar los conciertos de distintas plataformas de entradas. | HA-01 | Sí (RF-01, RF-19) | Alta |
| RQ-02 | Filtrar por distancia a la ubicación del usuario. | HA-02 | Sí (RF-11 a RF-13) | Alta |
| RQ-03 | Buscar y filtrar, no solo listar (por artista y por zona). | HA-04 | Sí (RF-09, RF-12) | Alta |
| RQ-04 | Funcionar bien en el teléfono. | HA-03 | Sí (RNF-11) | Alta |
| RQ-05 | **Detectar conciertos suspendidos o reprogramados** y avisarlo en la cartelera. | HA-05 | **No (nuevo)** | Alta |
| RQ-06 | Mostrar el tiempo de viaje además de la distancia. | — (depende de H6) | No | A definir después de las entrevistas |

RQ-05 ya tiene una propuesta de solución: guardar la URL del evento en la fuente y un estado del
concierto (ver REQUISITOS §7). Se sumaría a [REQUISITOS.md](REQUISITOS.md) con su número cuando
se planifique.

## 6. Conclusiones

1. El problema principal, la dispersión de la información, está respaldado por datos: 32
   plataformas de entradas para 216 shows.
2. La búsqueda por cercanía está justificada por la geografía: la oferta está en CABA y la mayoría
   de la población vive en el conurbano.
3. Aparece una necesidad que el sistema no cubre: enterarse de suspensiones y reprogramaciones
   (RQ-05).
4. Para H2, H3, H4 y H6 hacen falta entrevistas (anexo).

## 7. Fuentes

- Encuesta Nacional de Consumos Culturales 2022-2023, primeros resultados:
  [argentina.gob.ar](https://www.argentina.gob.ar/noticias/se-presentaron-los-primeros-resultados-de-la-encuesta-nacional-de-consumos-culturales);
  cobertura de prensa con los porcentajes citados: [Infobae](https://www.infobae.com/cultura/2023/05/23/consumos-culturales-en-argentina-la-musica-y-la-tv-siguen-siendo-masivas-pero-las-redes-sociales-lideran-el-podio/)
  y [elDiarioAR](https://www.eldiarioar.com/cultura/consumos-culturales-argentina-resisten-television-libros-musica-crecen-plataformas-digitales_1_10228123.html).
- Censo 2022 (INDEC), resultados provisionales por jurisdicción:
  [Chequeado](https://chequeado.com/el-explicador/censo-2022-como-evoluciono-la-poblacion-de-la-ciudad-y-la-provincia-de-buenos-aires/).
- Agendas de medios: [Indie Hoy](https://indiehoy.com/recitales/agenda-recitales-fin-de-semana-buenos-aires-30-31-agosto-1-septiembre/?amp=1),
  [Rolling Stone](https://es.rollingstone.com/etiqueta/agenda/),
  [Buenos Aires Secreta](https://bairessecreta.com/lugares-shows-musica-vivo-buenos-aires/).
- Reprogramaciones: [fallo contra Ticketek (iProfesional)](https://www.iprofesional.com/legales/155528-ticketek-debera-indemnizar-a-dos-personas-por-reprogramacion-de-show-de-madonna),
  [derechos del público (Derecho en Zapatillas)](https://www.derechoenzapatillas.com/2017/el-derecho-del-asistente-al-recital/),
  [qué pasa si un show se suspende (LM Neuquén)](https://www.lmneuquen.com/que-pasa-si-compraste-la-entrada-un-show-que-se-suspendio-n697986).
- Datos propios: `GET /conciertos` y `GET /api/metricas/{resumen,calidad}` de la API publicada, 25/10/2026.

---

## Anexo · Guía para las entrevistas (siguiente paso)

**Para qué.** Validar lo que los datos no responden: H2, H3, H4 y H6.

**Participantes.** 4 o 5 personas que hayan ido a al menos un recital en el AMBA en los últimos 6
meses, de CABA y del conurbano. Cada una se identifica como E1, E2… (sin nombres). Antes de
empezar se pide permiso para tomar notas. La app se muestra recién al final, para no condicionar
las respuestas.

1. ¿A cuántos recitales fuiste en el último año? ¿Dónde fueron?
2. Contame cómo te enteraste del último recital al que fuiste.
3. ¿Dónde buscás qué recitales hay? ¿Qué te molesta de esas fuentes?
4. ¿Alguna vez te enteraste tarde de un show que te hubiera gustado ver?
5. ¿Qué tan lejos estás dispuesto/a a viajar para un recital? ¿Alguna vez no fuiste por la distancia? *(H2)*
6. Cuando pensás en "cerca", ¿lo pensás en kilómetros, en tiempo de viaje o en barrios? *(H6)*
7. Antes de decidir ir, ¿qué datos necesitás ver? ¿Cuál es el más importante? *(H3)*
8. ¿Te pasó que un show se suspendiera o cambiara de fecha? ¿Cómo te enteraste? *(H5)*
9. Prueba de la app: "Buscá un recital cerca de tu casa para este mes." Observar sin ayudar y
   anotar dónde duda. *(H4)*

| Entrevista | Perfil (zona, frecuencia) | Cercanía | Datos que necesita | Suspensiones | Prueba de la app | Cita textual |
|---|---|---|---|---|---|---|
| E1 | | | | | | |
| E2 | | | | | | |
| E3 | | | | | | |
| E4 | | | | | | |
| E5 | | | | | | |
