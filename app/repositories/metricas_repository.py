"""
Consultas de métricas. Todo se calcula dentro de PostgreSQL/PostGIS (GROUP BY, generate_series,
ST_SnapToGrid, ST_Distance): a Python solo llegan los resultados ya agregados, nunca las filas
de conciertos. Así la cantidad de datos que viaja no depende del tamaño del historial.

Todas las consultas reciben el mismo filtro de fechas (`desde` y `hasta`, ambos opcionales e
inclusivos) mediante parámetros enlazados (`:desde`), nunca concatenando texto: eso evita la
inyección SQL. Si no hay filtro, cuentan todos los conciertos (incluidos los sin fecha); con
filtro, solo los que tienen fecha dentro del rango (RN-08).
"""

from sqlalchemy import text

from app.extensions import db

# Condición de fechas común a todas las métricas. `CAST(:desde AS date) IS NULL` vale cuando el
# parámetro no se envió: así una sola consulta sirve con y sin filtro.
FILTRO_FECHAS = """
    (CAST(:desde AS date) IS NULL OR c.fecha >= CAST(:desde AS date))
    AND (CAST(:hasta AS date) IS NULL OR c.fecha <= CAST(:hasta AS date))
"""

# Artista normalizado para agrupar: sin espacios en los extremos, en minúsculas y sin acentos,
# igual que el buscador del frontend ("Sofía Ríos" y "sofia rios" son el mismo artista, RN-11).
# Se resuelve con translate() en vez de la extensión unaccent: no requiere instalar nada.
ARTISTA_NORMALIZADO = "translate(lower(trim(c.artista)), 'áéíóúüñ', 'aeiouun')"


def _filas(sql, **parametros):
    """Ejecuta la consulta y devuelve las filas como diccionarios (columna -> valor)."""
    return db.session.execute(text(sql), parametros).mappings().all()


def resumen(desde, hasta, hoy):
    """
    Totales generales: conciertos, vigentes, pasados, sin fecha, lugares y artistas distintos.

    También la concentración: qué porcentaje de los conciertos con lugar se reparte entre los
    5 lugares más activos. Le da contexto al ranking (¿la escena depende de pocos lugares?).
    """
    sql = f"""
        WITH filtrados AS (
            SELECT c.* FROM conciertos c WHERE {FILTRO_FECHAS}
        ),
        top5 AS (
            SELECT count(*) AS cantidad
            FROM filtrados
            WHERE ubicacion IS NOT NULL
            GROUP BY ubicacion
            ORDER BY cantidad DESC
            LIMIT 5
        )
        SELECT
            count(*) AS total,
            count(*) FILTER (WHERE c.fecha >= :hoy OR c.fecha IS NULL) AS vigentes,
            count(*) FILTER (WHERE c.fecha < :hoy) AS pasados,
            count(*) FILTER (WHERE c.fecha IS NULL) AS sin_fecha,
            count(DISTINCT c.ubicacion) AS lugares,
            count(DISTINCT {ARTISTA_NORMALIZADO}) AS artistas,
            min(c.fecha) AS primera_fecha,
            max(c.fecha) AS ultima_fecha,
            round(
                100.0 * (SELECT coalesce(sum(cantidad), 0) FROM top5)
                / nullif(count(*) FILTER (WHERE c.ubicacion IS NOT NULL), 0),
                1
            ) AS concentracion_top5
        FROM filtrados c
    """
    return _filas(sql, desde=desde, hasta=hasta, hoy=hoy)[0]


def conciertos_por_mes(desde, hasta):
    """
    Cantidad de conciertos por mes, incluidos los meses sin conciertos (con 0).

    generate_series arma la lista completa de meses entre el inicio y el fin (los del filtro o,
    si no hay, el primer y el último mes con datos). El LEFT JOIN conserva los meses vacíos:
    sin eso, un mes sin shows desaparecería del gráfico en lugar de verse como un pozo.
    """
    sql = f"""
        WITH filtrados AS (
            SELECT c.fecha FROM conciertos c
            WHERE c.fecha IS NOT NULL AND {FILTRO_FECHAS}
        ),
        limites AS (
            SELECT
                date_trunc('month', coalesce(CAST(:desde AS date), min(fecha))) AS inicio,
                date_trunc('month', coalesce(CAST(:hasta AS date), max(fecha))) AS fin
            FROM filtrados
        ),
        meses AS (
            SELECT generate_series(inicio, fin, interval '1 month') AS mes FROM limites
        )
        SELECT to_char(meses.mes, 'YYYY-MM') AS mes, count(f.fecha) AS cantidad
        FROM meses
        LEFT JOIN filtrados f ON date_trunc('month', f.fecha) = meses.mes
        GROUP BY meses.mes
        ORDER BY meses.mes
    """
    return _filas(sql, desde=desde, hasta=hasta)


def lugares_mas_activos(desde, hasta, limite):
    """Ranking de lugares por cantidad de conciertos (desempata por nombre)."""
    sql = f"""
        SELECT u.id, u.nombre, count(*) AS cantidad
        FROM conciertos c
        JOIN ubicaciones u ON u.id = c.ubicacion
        WHERE {FILTRO_FECHAS}
        GROUP BY u.id, u.nombre
        ORDER BY cantidad DESC, u.nombre
        LIMIT :limite
    """
    return _filas(sql, desde=desde, hasta=hasta, limite=limite)


def artistas_que_mas_se_repiten(desde, hasta, limite):
    """
    Ranking de artistas por cantidad de conciertos, agrupando las variantes de escritura.
    mode() elige, de cada grupo, la forma de escribir el nombre que más se repite.
    """
    sql = f"""
        SELECT
            mode() WITHIN GROUP (ORDER BY c.artista) AS artista,
            count(*) AS cantidad,
            count(DISTINCT c.ubicacion) AS lugares
        FROM conciertos c
        WHERE {FILTRO_FECHAS}
        GROUP BY {ARTISTA_NORMALIZADO}
        ORDER BY cantidad DESC, artista
        LIMIT :limite
    """
    return _filas(sql, desde=desde, hasta=hasta, limite=limite)


def densidad(desde, hasta, celda_grados):
    """
    Densidad de conciertos para el mapa de calor: cada lugar se "redondea" al punto más cercano
    de una grilla de `celda_grados` (ST_SnapToGrid) y se cuenta cuántos conciertos caen en cada
    punto. Lugares muy cercanos (por ejemplo, dos teatros en la misma cuadra) suman juntos.
    """
    sql = f"""
        SELECT ST_X(punto) AS lng, ST_Y(punto) AS lat, count(*) AS cantidad
        FROM (
            SELECT ST_SnapToGrid(u.coordenadas, :celda) AS punto
            FROM conciertos c
            JOIN ubicaciones u ON u.id = c.ubicacion
            WHERE u.coordenadas IS NOT NULL AND {FILTRO_FECHAS}
        ) AS puntos
        GROUP BY punto
        ORDER BY cantidad DESC
    """
    return _filas(sql, desde=desde, hasta=hasta, celda=celda_grados)


def distribucion_de_distancias(desde, hasta, lat, lng, limites_km):
    """
    Cantidad de conciertos por rango de distancia (en km) desde el punto (lat, lng).

    `limites_km` = [0, 5, 10] arma los rangos [0, 5), [5, 10) y [10, ∞). La tabla de rangos se
    construye en SQL con unnest() y lead() (el límite siguiente), y se cruza con las distancias
    con un LEFT JOIN, así los rangos vacíos aparecen con 0.
    La distancia se mide sobre Geography: en metros sobre el elipsoide terrestre, no en grados.
    """
    sql = f"""
        WITH rangos AS (
            SELECT
                orden,
                desde_km,
                lead(desde_km) OVER (ORDER BY orden) AS hasta_km
            FROM unnest(CAST(:limites AS float8[])) WITH ORDINALITY AS r(desde_km, orden)
        ),
        distancias AS (
            SELECT
                ST_Distance(
                    CAST(u.coordenadas AS geography),
                    CAST(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326) AS geography)
                ) / 1000 AS km
            FROM conciertos c
            JOIN ubicaciones u ON u.id = c.ubicacion
            WHERE u.coordenadas IS NOT NULL AND {FILTRO_FECHAS}
        )
        SELECT r.desde_km, r.hasta_km, count(d.km) AS cantidad
        FROM rangos r
        LEFT JOIN distancias d
            ON d.km >= r.desde_km AND (r.hasta_km IS NULL OR d.km < r.hasta_km)
        GROUP BY r.orden, r.desde_km, r.hasta_km
        ORDER BY r.orden
    """
    return _filas(sql, desde=desde, hasta=hasta, lat=lat, lng=lng, limites=limites_km)


# Franjas horarias de la grilla día por horario. Un concierto a la 1:00 cuenta en la
# "Trasnoche" del día calendario en que figura en la fuente.
FRANJAS_HORARIAS = """
    (VALUES
        (1, 'Día (6 a 18)'),
        (2, '18 a 20'),
        (3, '20 a 22'),
        (4, '22 a 24'),
        (5, 'Trasnoche (0 a 6)')
    ) AS f(orden, nombre)
"""

FRANJA_DE_LA_HORA = """
    CASE
        WHEN extract(hour FROM c.hora) < 6 THEN 5
        WHEN extract(hour FROM c.hora) < 18 THEN 1
        WHEN extract(hour FROM c.hora) < 20 THEN 2
        WHEN extract(hour FROM c.hora) < 22 THEN 3
        ELSE 4
    END
"""


def dia_y_horario(desde, hasta):
    """
    Cantidad de conciertos por día de la semana (1 = lunes ... 7 = domingo) y franja horaria.
    Devuelve la grilla completa (7 días por 5 franjas): las celdas sin conciertos vienen con 0.
    Solo cuentan los conciertos con fecha y hora.
    """
    sql = f"""
        WITH conteo AS (
            SELECT
                CAST(extract(isodow FROM c.fecha) AS int) AS dia,
                {FRANJA_DE_LA_HORA} AS franja,
                count(*) AS cantidad
            FROM conciertos c
            WHERE c.fecha IS NOT NULL AND c.hora IS NOT NULL AND {FILTRO_FECHAS}
            GROUP BY 1, 2
        )
        SELECT d.dia, f.orden AS franja, f.nombre AS nombre_franja, coalesce(conteo.cantidad, 0) AS cantidad
        FROM generate_series(1, 7) AS d(dia)
        CROSS JOIN {FRANJAS_HORARIAS}
        LEFT JOIN conteo ON conteo.dia = d.dia AND conteo.franja = f.orden
        ORDER BY d.dia, f.orden
    """
    return _filas(sql, desde=desde, hasta=hasta)


def proximos_dias(hoy, dias):
    """Conciertos de cada uno de los próximos `dias` días (desde hoy), incluidos los días sin conciertos."""
    sql = """
        SELECT CAST(d AS date) AS fecha, count(c.id) AS cantidad
        FROM generate_series(
            CAST(:hoy AS date),
            CAST(:hoy AS date) + CAST(:dias AS int) - 1,
            interval '1 day'
        ) AS d
        LEFT JOIN conciertos c ON c.fecha = CAST(d AS date)
        GROUP BY d
        ORDER BY d
    """
    return _filas(sql, hoy=hoy, dias=dias)


def calidad(desde, hasta):
    """
    Qué tan completos están los datos: cuántos conciertos no tienen fecha, hora, link de
    entradas o lugar ubicado en el mapa. Sirve para vigilar el scraper: si la fuente cambia su
    HTML, estos números suben.
    """
    sql = f"""
        SELECT
            count(*) AS total,
            count(*) FILTER (WHERE c.fecha IS NULL) AS sin_fecha,
            count(*) FILTER (WHERE c.hora IS NULL) AS sin_hora,
            count(*) FILTER (WHERE c.url_evento IS NULL OR c.url_evento = '') AS sin_entradas,
            count(*) FILTER (WHERE u.coordenadas IS NULL) AS sin_ubicacion
        FROM conciertos c
        LEFT JOIN ubicaciones u ON u.id = c.ubicacion
        WHERE {FILTRO_FECHAS}
    """
    return _filas(sql, desde=desde, hasta=hasta)[0]


# Fecha en que la ingesta encontró el concierto, en hora argentina (creado_en se guarda con zona)
FECHA_DE_INGESTA = "CAST(c.creado_en AT TIME ZONE 'America/Argentina/Buenos_Aires' AS date)"


def ingesta_por_dia(hoy, dias):
    """
    Conciertos nuevos que encontró la ingesta en cada uno de los últimos `dias` días. Una racha
    de ceros cuando antes entraban conciertos es la señal de que el scraper se rompió.
    También devuelve desde cuándo se mide (el primer creado_en registrado).
    """
    sql = f"""
        WITH nuevos AS (
            SELECT {FECHA_DE_INGESTA} AS fecha, count(*) AS cantidad
            FROM conciertos c
            WHERE c.creado_en IS NOT NULL
            GROUP BY 1
        )
        SELECT
            CAST(d AS date) AS fecha,
            coalesce(nuevos.cantidad, 0) AS nuevos,
            (SELECT min({FECHA_DE_INGESTA}) FROM conciertos c) AS desde_que_se_mide
        FROM generate_series(
            CAST(:hoy AS date) - CAST(:dias AS int) + 1,
            CAST(:hoy AS date),
            interval '1 day'
        ) AS d
        LEFT JOIN nuevos ON nuevos.fecha = CAST(d AS date)
        ORDER BY d
    """
    return _filas(sql, hoy=hoy, dias=dias)


# Rangos de anticipación en días: [0, 8) = hasta una semana, ..., [91, sin tope) = más de 3 meses
LIMITES_ANTICIPACION = [0, 8, 31, 61, 91]


def anticipacion(desde, hasta):
    """
    Con cuántos días de anticipación se anuncian los conciertos: fecha del concierto menos fecha
    en que lo encontró la ingesta, agrupado en rangos, más la mediana. Solo cuentan los
    conciertos con fecha y con creado_en (los registrados desde la migración 0005).
    """
    sql = f"""
        WITH datos AS (
            SELECT c.fecha - {FECHA_DE_INGESTA} AS dias
            FROM conciertos c
            WHERE c.creado_en IS NOT NULL AND c.fecha IS NOT NULL AND {FILTRO_FECHAS}
        ),
        validos AS (SELECT dias FROM datos WHERE dias >= 0),
        rangos AS (
            SELECT orden, desde_dias, lead(desde_dias) OVER (ORDER BY orden) AS hasta_dias
            FROM unnest(CAST(:limites AS int[])) WITH ORDINALITY AS r(desde_dias, orden)
        )
        SELECT
            r.desde_dias,
            r.hasta_dias,
            count(v.dias) AS cantidad,
            (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY dias) FROM validos) AS mediana
        FROM rangos r
        LEFT JOIN validos v ON v.dias >= r.desde_dias AND (r.hasta_dias IS NULL OR v.dias < r.hasta_dias)
        GROUP BY r.orden, r.desde_dias, r.hasta_dias
        ORDER BY r.orden
    """
    return _filas(sql, desde=desde, hasta=hasta, limites=LIMITES_ANTICIPACION)
