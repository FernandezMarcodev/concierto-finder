# Matriz de trazabilidad de requisitos

Vincula cada requisito de [REQUISITOS.md](REQUISITOS.md) con su **fuente** (por qué existe), su
**implementación** (dónde está) y su **verificación** (cómo se comprueba). Permite responder dos
preguntas:

- *Hacia atrás:* ¿por qué existe este código?
- *Hacia adelante:* si cambia este requisito, ¿qué código y qué pruebas hay que tocar?

Actualizada al 25/10/2026.

**Fuentes:**
- `COD`: ingeniería inversa del código.
- `HA-xx`: hallazgo del [relevamiento](relevamiento.md).
- `D-x`: decisión de [ARQUITECTURA.md](ARQUITECTURA.md).
- `OPS`: incidente de operación.

**Verificación:**
- Los tests de `tests/` se nombran como `archivo::test`, sin el prefijo `test_` del archivo.
- `CP-xx` son los casos de [aceptación](casos-de-prueba.md).
- `Demo` es demostración manual en la app publicada; `Insp.` es inspección del código o de la configuración.

## 1. Interfaces externas

| ID | Fuente | Implementación | Verificación | Estado |
|---|---|---|---|---|
| IE-01 | COD | `web/src/App.jsx`, `componentes/Encabezado/` | Demo | Implementado |
| IE-02 | COD | `app/routes/`, [`openapi.json`](openapi.json) | `contrato_api::test_la_respuesta_cumple_el_contrato`, `contrato_api::test_el_contrato_documenta_exactamente_las_rutas_que_existen` | Implementado |
| IE-03 | COD | `app/services/scraper_service.py` | `scraper_parseo`, `scraper_recorrido` | Implementado |
| IE-04 | COD | `app/services/geocoding_service.py`, `services/http.py` | `geocodificacion::test_nominatim_se_consulta_solo_en_argentina` | Implementado |
| IE-05 | COD | `componentes/Mapa/`, `componentes/TarjetaGrupo/` | Insp. | Implementado |
| IE-06 | COD | URLs `https://` en `web/src/servicios/`, `ingesta.yml`, `services/` | Insp. | Implementado |

## 2. Requisitos funcionales

| ID | Fuente | Implementación | Verificación | Estado |
|---|---|---|---|---|
| RF-01 | COD | `routes/conciertos.py`, `paginas/Inicio.jsx` | `rutas_conciertos::test_conciertos_devuelve_solo_vigentes_y_se_puede_cachear`, CP-07 | Implementado |
| RF-02 | COD | `utilidades/grupos.js`, `componentes/TarjetaGrupo/` | Demo | Implementado |
| RF-03 | COD | `repositories/concierto_repository.py` (`_consulta_vigentes`) | `concierto_repository::test_orden_por_fecha_y_despues_por_hora`, `concierto_repository::test_sin_fecha_es_vigente_y_va_al_final` | Implementado |
| RF-04 | COD | `componentes/TarjetaGrupo/`, `utilidades/fechas.js` | Demo | Implementado |
| RF-05 | COD | `componentes/TarjetaGrupo/` | Demo | Implementado |
| RF-06 | COD | `componentes/Mapa/`, `paginas/Inicio.jsx` (`seleccion`) | Demo | Implementado |
| RF-07 | COD | `componentes/Mapa/` | Demo | Implementado |
| RF-08 | COD | `componentes/Portada/` | Demo | Implementado |
| RF-09 | COD, HA-04 | `utilidades/filtros.js`, `utilidades/texto.js` | CP-05 | Implementado |
| RF-10 | COD | `componentes/Filtros/` | Demo | Implementado |
| RF-11 | COD, HA-02 | `componentes/Filtros/` | CP-06, CP-07 | Implementado |
| RF-12 | COD, HA-02 | `utilidades/filtros.js`, `utilidades/geo.js` | CP-01, CP-02, CP-03 | Implementado |
| RF-13 | COD | `componentes/Filtros/`, `componentes/Mapa/`, `constantes.js` | CP-04 | Implementado |
| RF-14 | COD | `paginas/Inicio.jsx`, `hooks/useDebounce.js` | CP-05 | Implementado |
| RF-15 | COD | `componentes/EstadoVacio/` | CP-02 | Implementado |
| RF-16 | COD | `componentes/EstadoVacio/`, `componentes/Cargando/`, `hooks/useDemorado.js` | Demo | Implementado |
| RF-19 | COD | `.github/workflows/ingesta.yml` | Insp. (historial de ejecuciones en Actions) | Implementado (detenido por el bloqueo de la fuente, §7 de REQUISITOS) |
| RF-19 bis | COD | `services/tareas.py` (`ingesta_inicial`), `scraper_service.py` (`_candado_ingesta`) | Insp. | Implementado |
| RF-20 | COD | `routes/autorizacion.py`, `routes/conciertos.py` | `rutas_conciertos::test_ingesta_deshabilitada_sin_token_configurado`, `rutas_conciertos::test_ingesta_rechaza_token_incorrecto` | Implementado |
| RF-21 | COD | `scraper_service.py` (`_urls_de_eventos`, `_parsear_evento`) | `scraper_parseo::test_parsear_fecha`, `scraper_parseo::test_parsear_hora`, `scraper_recorrido` | Implementado |
| RF-22 | COD, OPS | `scraper_service.py`, `geocoding_service.py`, `lugares_conocidos.py` | `geocodificacion` (11 tests) | Implementado |
| RF-23 | COD | `geocoding_service.py` (`dentro_de_amba`), `scraper_service.py` | `geocodificacion::test_lugar_fuera_de_amba_dice_el_motivo`, `geocodificacion::test_cada_descarte_dice_el_motivo_y_se_geocodifica_una_sola_vez` | Implementado |
| RF-24 | COD | `concierto_repository.py` (`existe_concierto`) | `concierto_repository::test_existe_concierto_considera_iguales_las_fechas_nulas` | Implementado |
| RF-25 | COD | `routes/conciertos.py` | Insp. | Implementado |
| RF-26 | COD | `services/tareas.py`, `concierto_repository.py` (`eliminar_conciertos_duplicados`) | `concierto_repository::test_eliminar_duplicados_conserva_el_de_menor_id`, `tareas::test_limpieza_borra_duplicados_y_conserva_pasados` | Implementado |
| RF-26 bis | D-8 | `concierto_repository.py` (`_consulta_vigentes`) | `concierto_repository::test_listado_excluye_pasados_pero_los_conserva_en_la_base` | Implementado |
| RF-27 | COD | `routes/conciertos.py`, `routes/ubicaciones.py` | `rutas_conciertos::test_conciertos_cerca`, `concierto_repository::test_cerca_filtra_por_distancia` | Implementado |
| RF-28 | COD | `paginas/Metricas.jsx`, `servicios/metricasServicio.js` | CP-08 | Implementado |
| RF-29 | COD | `metricas_repository.py` (`resumen`), `componentes/TarjetaDato/` | `metricas_repository::test_resumen`, `metricas_nuevas::test_concentracion_en_los_5_lugares_mas_activos`, CP-08 | Implementado |
| RF-30 | COD | `metricas_repository.py` (`conciertos_por_mes`), `componentes/GraficoArea/` | `metricas_repository::test_conciertos_por_mes_completa_los_meses_vacios` | Implementado |
| RF-31 | COD | `metricas_repository.py`, `componentes/GraficoBarras/` | `metricas_repository::test_ranking_de_lugares`, `metricas_repository::test_ranking_de_artistas_agrupa_variantes_de_escritura` | Implementado |
| RF-32 | COD | `metricas_repository.py`, `componentes/GrillaDiaHorario/`, `GraficoBarras/` | `metricas_nuevas::test_proximos_dias_incluye_los_dias_sin_conciertos`, `metricas_nuevas::test_dia_y_horario_devuelve_la_grilla_completa`, `metricas_nuevas::test_anticipacion_por_rangos_y_mediana` | Implementado |
| RF-33 | COD | `metricas_repository.py` (`densidad`), `componentes/MapaCalor/` | `metricas_repository::test_densidad_agrupa_lugares_cercanos_segun_la_celda`, `rutas_metricas::test_densidad_devuelve_lng_lat_cantidad` | Implementado |
| RF-34 | COD | `componentes/FiltroRango/`, `utilidades/periodos.js`, `services/metricas_service.py` | `metricas_service::test_filtro_invalido`, `rutas_metricas::test_todos_rechazan_fechas_invalidas`, CP-09, CP-10 | Implementado (observación OBS-01) |
| RF-35 | COD | `metricas_repository.py` (`calidad`, `ingesta_por_dia`), `componentes/MedidorCalidad/`, `PanelGrafico/` | `metricas_nuevas::test_calidad_cuenta_los_datos_faltantes`, `metricas_nuevas::test_ingesta_por_dia_usa_la_fecha_argentina` | Implementado |
| RF-36 | D-10 | `routes/metricas.py` | `rutas_metricas::test_todos_responden_con_filtro_y_cache`, `contrato_api` | Implementado |
| RF-37 | HA-05 | — (propuesta: columnas `url_fuente` y `estado`, migración 0006) | — | **Propuesto** |

## 3. Reglas de negocio

| ID | Fuente | Implementación | Verificación |
|---|---|---|---|
| RN-01 | COD | `geocoding_service.py` (límites), `web/src/constantes.js` | `geocodificacion::test_todos_los_lugares_conocidos_estan_en_amba`, `datos_ficticios::test_todos_los_lugares_estan_en_amba` |
| RN-02 | D-8 | `concierto_repository.py` (`_consulta_vigentes`), `services/fechas.py` | `concierto_repository::test_la_vigencia_depende_del_parametro_hoy`, `tareas::test_a_las_22_de_argentina_en_utc_ya_es_el_dia_siguiente`, CP-08 |
| RN-03 | COD | `concierto_repository.py` (`existe_concierto`) | `concierto_repository::test_existe_concierto_considera_iguales_las_fechas_nulas` |
| RN-04 | COD | `scraper_service.py` (`_parsear_fecha`, `_parsear_hora`) | `scraper_parseo::test_parsear_fecha`, `scraper_parseo::test_parsear_hora` |
| RN-05 | COD | `scraper_service.py` (`_recortar`), `models/concierto.py` | `scraper_parseo::test_recortar_al_largo_de_la_columna` |
| RN-06 | COD | `componentes/Mapa/` | Insp. |
| RN-07 | COD | `web/src/constantes.js` | Insp. |
| RN-08 | COD | `metricas_repository.py` (`FILTRO_FECHAS`) | `metricas_repository::test_el_filtro_de_fechas_es_inclusivo_y_excluye_los_sin_fecha` |
| RN-09 | COD | `metricas_repository.py` | `metricas_repository::test_ranking_de_lugares`, `metricas_repository::test_densidad_agrupa_lugares_cercanos_segun_la_celda` |
| RN-10 | COD | `metricas_repository.py` (`distribucion_de_distancias`) | `metricas_repository::test_distancias_desde_el_obelisco`, `rutas_metricas::test_distancias_con_punto_y_rangos` |
| RN-11 | D-12 | `metricas_repository.py` (`ARTISTA_NORMALIZADO`) | `metricas_repository::test_ranking_de_artistas_agrupa_variantes_de_escritura` |
| RN-12 | COD | Alcance de la ingesta (`PAGINAS`) | Insp. |
| RN-13 | COD | `metricas_repository.py` (`FRANJAS_HORARIAS`) | `metricas_nuevas::test_dia_y_horario_devuelve_la_grilla_completa` |
| RN-14 | COD | `metricas_repository.py` (`anticipacion`) | `metricas_nuevas::test_anticipacion_por_rangos_y_mediana` |
| RN-15 | COD | `metricas_repository.py` (`calidad`) | `metricas_nuevas::test_calidad_cuenta_los_datos_faltantes` |

## 4. Requisitos no funcionales

| ID | Tipo (Sommerville) | Fuente | Implementación | Verificación |
|---|---|---|---|---|
| RNF-01 | Producto: eficiencia | COD | `concierto_repository.py` (`joinedload`), índices de la migración 0003 | `concierto_repository::test_trae_la_ubicacion_en_la_misma_consulta`, `migraciones::test_los_modelos_coinciden_con_las_migraciones` |
| RNF-02 | Producto: eficiencia | D-1 | `utilidades/filtros.js` | Insp. |
| RNF-03 | Producto: eficiencia | COD | `routes/conciertos.py`, `routes/metricas.py`, `web/nginx.conf` | `rutas_conciertos::test_conciertos_devuelve_solo_vigentes_y_se_puede_cachear`, `rutas_metricas::test_todos_responden_con_filtro_y_cache` |
| RNF-04 | Producto: eficiencia | COD | `app/config.py` (pool), `app/__init__.py` (handler 503) | Insp. |
| RNF-05 | Producto: confiabilidad | COD | `services/tareas.py` (`mantener_despierta`) | `tareas::test_dentro_de_franja` |
| RNF-06 | Producto: confiabilidad | COD | `services/http.py` (`TIMEOUT_SEGUNDOS`), `scraper_service.py` | `scraper_recorrido`, Insp. |
| RNF-07 | Externo: ético | COD, OPS | `services/http.py` (`USER_AGENT`), `PAUSA_ENTRE_EVENTOS` | Insp. |
| RNF-08 | Producto: protección | COD | `app/config.py`, `routes/autorizacion.py` (`hmac.compare_digest`) | `rutas_conciertos::test_ingesta_rechaza_token_incorrecto` |
| RNF-09 | Producto: protección | D-13 | Migración `0004_seguridad_rls` | `seguridad_rls::test_las_tablas_del_proyecto_tienen_rls`, `seguridad_rls::test_un_rol_ajeno_no_ve_filas_aunque_tenga_permiso_de_lectura` |
| RNF-10 | Organización: operacional | D-7 | `migrations/` | `migraciones::test_los_modelos_coinciden_con_las_migraciones`, `migraciones::test_downgrade_y_upgrade_completos` |
| RNF-11 | Producto: usabilidad | COD, HA-03 | `index.css`, módulos CSS | CP-01 a CP-10, Demo (teléfono) |
| RNF-12 | Organización: ambiental | COD | `docker-compose.yml`, `Dockerfile`, `web/Dockerfile` | Demo |
| RNF-13 | Organización: de desarrollo | COD | Todo el repositorio | Insp. |
| RNF-14 | Organización: de desarrollo | D-9 | `tests/`, `.github/workflows/ci.yml` | Insp. (CI en cada PR) |
| RNF-15 | Producto: eficiencia | D-10, D-11 | `metricas_repository.py`, `React.lazy` en `App.jsx` | `rutas_metricas`, Insp. |
| RNF-16 | Externo: legislativo (privacidad) | COD | `componentes/Filtros/`, `utilidades/filtros.js` (la ubicación no sale del navegador) | Insp. |
| RNF-17 | Externo: regulatorio | COD | `componentes/Mapa/` y `MapaCalor/` (`attribution`), `componentes/PieDePagina/` | Insp. |
| RNF-18 | Externo: ético | OPS | Decisión documentada en REQUISITOS §7 y OPERACION §8 | Insp. |
| RNF-19 | Producto: usabilidad | D-14 | `componentes/PanelGrafico/` (tabla para lectores), `utilidades/contraste.js` | Insp. |
| RNF-20 | Producto: confiabilidad | OPS | `.github/workflows/ingesta.yml`, `scraper_service.py` | `scraper_recorrido::test_primera_pagina_sin_lista_se_registra_como_error`, `scraper_recorrido::test_pagina_siguiente_sin_lista_es_el_fin_de_la_agenda` |

## 5. Cobertura

| Grupo | Total | Con prueba automatizada | Solo aceptación (CP) | Solo demostración o inspección | Propuestos |
|---|---|---|---|---|---|
| Interfaces externas (IE) | 6 | 3 | 0 | 3 | 0 |
| Funcionales (RF, incluidos los "bis") | 37 | 18 | 7 | 11 | 1 |
| Reglas de negocio (RN) | 15 | 12 | 0 | 3 | 0 |
| No funcionales (RNF) | 20 | 9 | 1 | 10 | 0 |

**Lectura:**

- Los requisitos sin prueba automatizada son casi todos del frontend, que no tiene tests (REQUISITOS
  §7), o de la organización y externos, que se verifican por inspección.
- El siguiente paso para subir la cobertura es sumar tests del frontend (por ejemplo, con Vitest)
  para RF-02, RF-04 a RF-08, RF-10 y RF-16.

La tabla se calcula a partir de las columnas de verificación de este documento: un requisito cuenta como "con prueba automatizada" si al menos un test de `tests/` lo verifica.

## 6. Trazabilidad hacia atrás: del relevamiento a los requisitos

| Hallazgo ([relevamiento](relevamiento.md)) | Requisitos que respalda o genera |
|---|---|
| HA-01 Entradas repartidas en 32 plataformas | RF-01, RF-19 (reunir en un solo lugar) |
| HA-02 Oferta en CABA, población en el conurbano | RF-11, RF-12, RF-13 (cercanía) |
| HA-03 Consumo masivo y joven; el celular como dispositivo principal | RNF-11 (responsivo) |
| HA-04 Las agendas de medios no se pueden filtrar | RF-09, RF-12 |
| HA-05 Las reprogramaciones existen y generan reclamos | **RF-37 (nuevo, propuesto)** |
| HA-06 Los datos de la fuente están completos | RF-35 (calidad de datos) |
