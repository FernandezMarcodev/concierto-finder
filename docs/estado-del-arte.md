# Estado del arte

Análisis de las soluciones que existen hoy para enterarse de recitales en el AMBA, para justificar
qué aporta Concierto Finder y qué le falta. Relevado el 25/10/2026 desde sitios públicos y notas de
prensa. Complementa el [relevamiento](relevamiento.md) (técnica T3).

## 1. Criterios de comparación

Salen de los requisitos esenciales ([REQUISITOS.md](REQUISITOS.md)) y de los hallazgos del relevamiento:

| Criterio | Por qué importa | Origen |
|---|---|---|
| K1. Cobertura local del AMBA, incluidas salas chicas | La oferta está repartida en 32 plataformas de entradas | HA-01 |
| K2. Mapa de los eventos | Ver dónde queda cada show | RF-07 |
| K3. Filtro por distancia a la ubicación del usuario | El 78 % de la población vive en el conurbano y la oferta está en CABA | HA-02, RF-12 |
| K4. Búsqueda por artista | Encontrar un show concreto | RF-09 |
| K5. Métricas de la escena (cuándo, dónde, quién) | Entender la oferta, no solo listarla | RF-28 |
| K6. Alertas o seguimiento de artistas | Enterarse sin entrar a buscar | — (fuera del alcance actual) |
| K7. Sin registro | Consultar sin crear una cuenta | RF-01 |

## 2. Soluciones analizadas

### 2.1 agendade.com.ar (la fuente de Concierto Finder)

Agenda de recitales de todo el país, con buscador ("Encuentra evento o artista") y filtros. Cada
evento enlaza a su ticketera. Es la base de datos más completa entre las relevadas para salas chicas,
porque los propios artistas y productores suman sus shows ("Sumá tu show"). No se observó un mapa ni
un filtro por distancia.

### 2.2 Agendas de medios (Indie Hoy, Rolling Stone, Buenos Aires Secreta)

Publican la agenda como notas editoriales: los shows del fin de semana, las visitas internacionales
y recomendaciones de salas. Sirven para descubrir, pero son una selección hecha por la redacción, se
desactualizan y no se pueden filtrar ni buscar.

### 2.3 Ticketeras (Passline, Ticketek, AllAccess, Movistar Arena, etc.)

Cada una lista solo los eventos que vende. En la cartelera de Concierto Finder hay **32 plataformas
distintas** para 216 shows: ninguna sirve como vista general.

### 2.4 Bandsintown

Plataforma global para seguir artistas y descubrir música en vivo. Tiene página para Buenos Aires,
un mapa de salas, búsqueda de eventos cercanos y recomendaciones según los gustos y la ubicación.
Es gratuita, con un plan pago opcional. Es la solución más parecida en cuanto a cercanía.

### 2.5 Songkick

Servicio global para seguir artistas. Envía una alerta cuando se anuncia una fecha en una ciudad
cercana, y se pueden configurar varias ubicaciones. Está orientado a artistas que salen de gira más
que a la escena local.

## 3. Comparación

| Solución | K1 Local AMBA | K2 Mapa | K3 Distancia | K4 Artista | K5 Métricas | K6 Alertas | K7 Sin registro |
|---|---|---|---|---|---|---|---|
| agendade.com.ar | Sí | No observado | No observado | Sí | No | No observado | Sí |
| Medios (Indie Hoy, etc.) | Parcial (selección) | No | No | No | No | No | Sí |
| Ticketeras | Parcial (solo lo propio) | No verificado | No verificado | Sí | No | No verificado | Sí, para ver |
| Bandsintown | Parcial (giras y salas cargadas) | Sí (salas) | Sí ("cerca de vos"; radio configurable: no verificado) | Sí | No | Sí | Para seguir artistas |
| Songkick | Parcial (giras) | No verificado | Por ciudad | Sí | No | Sí | Para alertas |
| **Concierto Finder** | **Sí** (de agendade) | **Sí** | **Sí** (1 a 40 km, círculo en el mapa) | **Sí** (sin tildes) | **Sí** | **No** | **Sí** |

"No observado" y "No verificado" quieren decir que no se encontró evidencia, no que no exista: es una
limitación de este relevamiento.

## 4. Conclusiones

**Qué aporta Concierto Finder:**

1. **Filtro por distancia en km con un mapa**, sobre la escena local y sin registrarse. Bandsintown
   ofrece cercanía, pero con foco en giras y artistas seguidos.
2. **Métricas públicas de la escena** (días y horarios con más shows, lugares más activos,
   anticipación). Ninguna de las soluciones relevadas las ofrece.
3. **Una vista única** de lo que hoy está repartido en más de 30 ticketeras y en notas de medios.

**Qué le falta, comparado con las demás:**

1. **Alertas.** Bandsintown y Songkick avisan; Concierto Finder no (está fuera del alcance).
2. **Depende de una sola fuente**, que además hoy bloquea los pedidos desde el servidor
   ([REQUISITOS](REQUISITOS.md) §7). Las plataformas globales tienen acuerdos con artistas y
   ticketeras.
3. **No detecta suspensiones** (RF-37, propuesto).

**Oportunidad:** la combinación de una cobertura local completa con mapa, distancia y métricas no
aparece en las soluciones relevadas. Un acuerdo con la fuente (agendade) cerraría la principal
debilidad y le daría a la fuente funciones que hoy no tiene.

## 5. Fuentes

- agendade.com.ar: [agenda](https://www.agendade.com.ar/agenda) y [contacto](https://www.agendade.com.ar/contacto) (consultados el 25/10/2026).
- Bandsintown: [Buenos Aires](https://www.bandsintown.com/c/buenos-aires-argentina);
  [comparación Bandsintown vs. Songkick (CB Insights)](https://www.cbinsights.com/compare/bandsintown-vs-songkick);
  [nota de Digital Music News](https://www.digitalmusicnews.com/2015/02/03/bandsintown-15m-users-artists-can-finally-use-data/).
- Songkick: [reseña de Music Gateway](https://www.musicgateway.com/blog/live-music/songkick-review).
- Medios: [Indie Hoy](https://indiehoy.com/lugares-para-ver-conciertos-en-argentina/),
  [Rolling Stone](https://es.rollingstone.com/etiqueta/agenda/),
  [Buenos Aires Secreta](https://bairessecreta.com/lugares-shows-musica-vivo-buenos-aires/).
- Plataformas de entradas: análisis de los links de los 216 conciertos publicados ([relevamiento](relevamiento.md), HA-01).
