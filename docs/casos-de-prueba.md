# Casos de prueba de aceptación

Pruebas de aceptación de la **búsqueda por cercanía** y de la **página de métricas**, ejecutadas
sobre la aplicación publicada.

| Dato | Valor |
|---|---|
| Aplicación | https://conciertosfinder.pages.dev (web) y https://concierto-finder.onrender.com (API) |
| Fecha de ejecución | 25/10/2026, 14:58 (hora de Argentina) |
| Datos al momento de la prueba | 216 conciertos vigentes publicados; 305 en total con el historial |
| Navegador | Google Chrome (escritorio, 1280 × 900) |
| Resultado | **10 de 10 casos pasaron**. 1 observación (OBS-01). |

## Cómo se ejecutaron

- **Ubicación simulada.** La búsqueda por cercanía usa la ubicación del navegador. Para probar
  desde un lugar concreto se simuló la geolocalización con estas coordenadas (para repetirlo a mano:
  herramientas de desarrollo de Chrome → *Sensors* → *Location*):

  | Punto | Latitud | Longitud |
  |---|---|---|
  | Obelisco (CABA) | −34,6037 | −58,3816 |
  | Plaza principal de Merlo | −34,6653 | −58,7279 |

- **Resultado esperado calculado aparte.** Para no comparar la aplicación contra sí misma, se
  descargó la lista de conciertos de la API (`GET /conciertos`) y se calculó la distancia de cada
  lugar al punto con la fórmula de Haversine. Esa lista es el resultado esperado: cantidad de
  conciertos y lugares que deberían aparecer.
- **Los números cambian cada día.** La cartelera se actualiza dos veces por día, así que las
  cantidades esperadas valen para la fecha de ejecución. Al repetir la prueba hay que recalcularlas;
  lo que no cambia es el criterio (por ejemplo, "todo lo mostrado está a 5 km o menos").
- Ejecución asistida por un script con Chrome headless, que repite los pasos de cada caso y guarda
  una captura como evidencia en [`evidencia-uat/`](evidencia-uat/).

## Resumen

| ID | Caso | Requisitos | Resultado |
|---|---|---|---|
| CP-01 | Radio de 5 km desde el Obelisco | RF-11, RF-12 | Pasó |
| CP-02 | Ubicación sin conciertos cercanos (Merlo, 5 km) | RF-12, RF-15 | Pasó |
| CP-03 | Ampliar el radio a 20 km desde Merlo | RF-12, RF-13 | Pasó |
| CP-04 | Cambiar el radio con los atajos (5, 20 y 40 km) | RF-13 | Pasó |
| CP-05 | Combinar artista sin tildes y cercanía | RF-09, RF-14 | Pasó |
| CP-06 | Permiso de ubicación bloqueado | RF-11 | Pasó |
| CP-07 | Desactivar "Cerca de mí" | RF-11, RF-01 | Pasó |
| CP-08 | Indicadores de métricas coinciden con la API y la cartelera | RF-28, RF-29, RN-02 | Pasó |
| CP-09 | Período sin conciertos | RF-34 | Pasó |
| CP-10 | Fecha "desde" posterior a "hasta" | RF-34 | Pasó, con observación |

## Búsqueda por cercanía

### CP-01 · Radio de 5 km desde el Obelisco

| Campo | Detalle |
|---|---|
| Precondición | Ubicación del navegador simulada en el Obelisco y permiso de ubicación concedido. |
| Pasos | 1. Abrir la cartelera. 2. Activar **Cerca de mí**. 3. Dejar el radio inicial (5 km). |
| Dato de entrada | Punto: Obelisco. Radio: 5 km. |
| Resultado esperado | Se muestran solo los conciertos cuyo lugar está a 5 km o menos: según el cálculo con Haversine, **69 conciertos en 23 lugares**. |
| Resultado obtenido | 69 conciertos en 23 lugares, los mismos 23 lugares del cálculo. Ningún lugar a más de 5 km. |
| Estado | **Pasó** · Evidencia: [CP-01.png](evidencia-uat/CP-01.png) |

### CP-02 · Ubicación sin conciertos cercanos

| Campo | Detalle |
|---|---|
| Precondición | Ubicación simulada en la plaza de Merlo y permiso concedido. |
| Pasos | 1. Abrir la cartelera. 2. Activar **Cerca de mí** (radio 5 km). |
| Dato de entrada | Punto: Merlo. Radio: 5 km. |
| Resultado esperado | Ningún concierto (el lugar más cercano está a 5,6 km) y un mensaje claro que invite a cambiar la búsqueda. |
| Resultado obtenido | 0 conciertos y el mensaje "No hay conciertos. No se encontraron conciertos con los filtros seleccionados. Probá ajustar la búsqueda." El mapa muestra el círculo de 5 km. |
| Estado | **Pasó** · Evidencia: [CP-02.png](evidencia-uat/CP-02.png) |

### CP-03 · Ampliar el radio desde Merlo

| Campo | Detalle |
|---|---|
| Precondición | La del CP-02 (Merlo, 5 km, sin resultados). |
| Pasos | 1. Elegir el atajo **20 km**. |
| Dato de entrada | Punto: Merlo. Radio: 20 km. |
| Resultado esperado | 6 conciertos en 5 lugares: Teatro Morón, Encuentro Club (San Justo), Estadio Vélez Sarsfield, Estadio Nuevo Francisco Urbano (Morón) y Teatro Gran Ituzaingó. |
| Resultado obtenido | 6 conciertos en esos mismos 5 lugares. |
| Estado | **Pasó** · Evidencia: [CP-03.png](evidencia-uat/CP-03.png) |

### CP-04 · Cambiar el radio con los atajos

| Campo | Detalle |
|---|---|
| Precondición | Obelisco, **Cerca de mí** activo con 5 km. |
| Pasos | 1. Elegir **20 km**. 2. Elegir **40 km**. |
| Dato de entrada | Radios: 5, 20 y 40 km. |
| Resultado esperado | La cantidad crece con el radio y coincide con el cálculo: 69 (5 km), 188 (20 km) y 192 (40 km). El texto del filtro indica el radio elegido. |
| Resultado obtenido | 69, 188 y 192. El filtro dice "Mostrando conciertos a menos de 40 km". |
| Estado | **Pasó** · Evidencia: [CP-04.png](evidencia-uat/CP-04.png) |

### CP-05 · Artista sin tildes combinado con cercanía

| Campo | Detalle |
|---|---|
| Precondición | Obelisco, **Cerca de mí** activo. |
| Pasos | 1. Elegir **20 km**. 2. Escribir "maria becerra" (sin tilde) en el buscador. |
| Dato de entrada | Artista: "maria becerra". Radio: 20 km. |
| Resultado esperado | Solo los conciertos de "María Becerra" a 20 km o menos: 8. Los dos filtros se combinan. |
| Resultado obtenido | 8 conciertos, todos de "María Becerra". |
| Estado | **Pasó** · Evidencia: [CP-05.png](evidencia-uat/CP-05.png) |

### CP-06 · Permiso de ubicación bloqueado

| Campo | Detalle |
|---|---|
| Precondición | El navegador tiene **bloqueado** el permiso de ubicación para el sitio. |
| Pasos | 1. Abrir la cartelera. 2. Activar **Cerca de mí**. |
| Dato de entrada | Permiso de ubicación: bloqueado. |
| Resultado esperado | Un mensaje que explique cómo habilitar el permiso, y la lista sin filtrar (no queda vacía). |
| Resultado obtenido | "Bloqueaste el acceso a tu ubicación. Habilitalo en los permisos del navegador." La lista sigue mostrando los 216 conciertos. |
| Estado | **Pasó** · Evidencia: [CP-06.png](evidencia-uat/CP-06.png) |

### CP-07 · Desactivar "Cerca de mí"

| Campo | Detalle |
|---|---|
| Precondición | La del final del CP-04 (Obelisco, 40 km). |
| Pasos | 1. Volver a tocar **Cerca de mí** para desactivarlo. |
| Dato de entrada | — |
| Resultado esperado | Vuelven a aparecer todos los conciertos vigentes publicados (216). |
| Resultado obtenido | 216 conciertos. |
| Estado | **Pasó** · Sin captura (continúa la sesión del CP-04). |

## Métricas

### CP-08 · Los indicadores coinciden con la API y con la cartelera

| Campo | Detalle |
|---|---|
| Precondición | Período "Todo" (el inicial). |
| Pasos | 1. Abrir **Métricas**. 2. Leer los indicadores **Conciertos** y **Vigentes**. 3. Comparar con `GET /api/metricas/resumen` y con la cantidad de la cartelera. |
| Dato de entrada | — |
| Resultado esperado | Los indicadores muestran lo mismo que la API, y "Vigentes" coincide con lo que publica la cartelera (la vigencia se calcula igual en los dos lados, RN-02). |
| Resultado obtenido | Página: 305 conciertos y 216 vigentes. API: 305 y 216. Cartelera: 216. |
| Estado | **Pasó** · Evidencia: [CP-08.png](evidencia-uat/CP-08.png) |

### CP-09 · Período sin conciertos

| Campo | Detalle |
|---|---|
| Precondición | Página de métricas cargada. |
| Pasos | 1. Cargar **Desde** = 01/01/2020. 2. Cargar **Hasta** = 31/12/2020. |
| Dato de entrada | Período: año 2020 (antes de que existiera el historial). |
| Resultado esperado | Un mensaje claro de que no hay datos, sin gráficos vacíos. |
| Resultado obtenido | "No hay conciertos en este período. Probá con otro rango de fechas." La API confirma total 0 para ese período. |
| Estado | **Pasó** · Evidencia: [CP-09.png](evidencia-uat/CP-09.png) |

### CP-10 · Fecha "desde" posterior a "hasta"

| Campo | Detalle |
|---|---|
| Precondición | Página de métricas cargada. |
| Pasos | 1. Cargar **Hasta** = 01/01/2026. 2. Cargar **Desde** = 31/12/2026. |
| Dato de entrada | Rango invertido. |
| Resultado esperado | Un aviso de que el rango es inválido y **ninguna consulta** a la API con ese rango. |
| Resultado obtenido | Aviso: "La fecha «desde» no puede ser posterior a «hasta»." Pedidos a la API después de cargar el "desde" inválido: 0. |
| Estado | **Pasó, con observación OBS-01** · Evidencia: [CP-10.png](evidencia-uat/CP-10.png) |

## Observaciones

| ID | Caso | Observación | Severidad | Propuesta |
|---|---|---|---|---|
| OBS-01 | CP-10 | Con el rango inválido, debajo del aviso sigue visible el resultado de la consulta anterior. En la prueba era "No hay conciertos en este período" (del rango válido previo, hasta el 01/01/2026), que puede leerse como si fuera el resultado del rango inválido. | Baja (no hay datos incorrectos, pero confunde) | Mientras el rango sea inválido, ocultar los resultados o atenuarlos con un texto "Corregí las fechas para ver las métricas". |

## Fuera de alcance

- La distancia es en línea recta, no por calles ni en tiempo de viaje (es lo que define RF-12).
- No se probó en teléfonos reales: la vista móvil se verificó aparte (RNF-11).
- No se probó la API de búsqueda espacial del servidor (`/conciertos_cerca`), porque la web no la usa (RF-27).
