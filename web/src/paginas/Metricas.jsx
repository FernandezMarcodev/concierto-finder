import { useEffect, useMemo, useState } from "react";
import {
  FaCalendarCheck,
  FaChartPie,
  FaHistory,
  FaMapMarkerAlt,
  FaMicrophone,
  FaMusic,
} from "react-icons/fa";
import Encabezado from "../componentes/Encabezado/Encabezado";
import Portada, { DatoPortada } from "../componentes/Portada/Portada";
import PieDePagina from "../componentes/PieDePagina/PieDePagina";
import Cargando from "../componentes/Cargando/Cargando";
import EstadoVacio from "../componentes/EstadoVacio/EstadoVacio";
import FiltroRango from "../componentes/FiltroRango/FiltroRango";
import TarjetaDato from "../componentes/TarjetaDato/TarjetaDato";
import PanelGrafico from "../componentes/PanelGrafico/PanelGrafico";
import GraficoBarras from "../componentes/GraficoBarras/GraficoBarras";
import GraficoArea from "../componentes/GraficoArea/GraficoArea";
import GrillaDiaHorario from "../componentes/GrillaDiaHorario/GrillaDiaHorario";
import MedidorCalidad from "../componentes/MedidorCalidad/MedidorCalidad";
import MapaCalor from "../componentes/MapaCalor/MapaCalor";
import { metricasServicio } from "../servicios/metricasServicio";
import { diaCorto, diaLargo, esFinDeSemana, fechaIso, mesCorto, mesLargo } from "../utilidades/fechas";
import { fechaLegible } from "../utilidades/texto";
import { PERIODO_INICIAL, PERIODOS } from "../utilidades/periodos";
import styles from "./metricas.module.css";

const filtroInicial = () => ({
  periodo: PERIODO_INICIAL,
  ...PERIODOS.find((p) => p.id === PERIODO_INICIAL).calcular(new Date()),
});

const COLUMNA_CANTIDAD = { clave: "cantidad", titulo: "Conciertos" };

// Con menos meses que esto, se avisa que el historial recién se está armando
const MESES_HISTORIAL_CORTO = 4;

// "2026-10": el mes actual, para marcarlo en el gráfico mensual
const mesActual = () => fechaIso(new Date()).slice(0, 7);

// Rango de anticipación: "0 a 7 días", ..., "más de 90 días"
const textoAnticipacion = (fila) =>
  fila.hasta_dias == null
    ? `más de ${fila.desde_dias - 1} días`
    : `${fila.desde_dias} a ${fila.hasta_dias - 1} días`;
const textoAnticipacionCorto = (texto) => texto.replace(" días", "").replace("más de ", "+");

const DIAS_SEMANA = ["", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"];

function NotaDatos({ resumen }) {
  const sinFecha = resumen.sin_fecha;
  return (
    <p className={styles.nota}>
      Datos acumulados desde el {fechaLegible(resumen.primera_fecha)}. Solo cuentan los conciertos publicados
      en agendade.com.ar dentro de AMBA; los cancelados o reprogramados pueden figurar igual.
      {sinFecha === 1 && " 1 concierto no tiene fecha y no aparece en los gráficos por fecha."}
      {sinFecha > 1 && ` ${sinFecha} conciertos no tienen fecha y no aparecen en los gráficos por fecha.`}
    </p>
  );
}

// Para las métricas que dependen de creado_en: se empezaron a medir hace poco
function SinDatosTodavia({ desde }) {
  return (
    <p className={styles.sinDatos}>
      {desde
        ? `Se empezó a medir el ${fechaLegible(desde)}. Los datos se van a ir sumando con cada actualización.`
        : "Todavía no hay datos: se empiezan a registrar con la próxima actualización de conciertos."}
    </p>
  );
}

const Metricas = () => {
  const [filtro, setFiltro] = useState(filtroInicial);
  const [datos, setDatos] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  // Con "desde" posterior a "hasta" no se pide nada: se avisa en el filtro
  const filtroInvalido = Boolean(filtro.desde && filtro.hasta && filtro.desde > filtro.hasta);

  useEffect(() => {
    document.title = "Métricas · Concierto Finder";
    return () => {
      document.title = "Concierto Finder";
    };
  }, []);

  // Cada cambio de filtro vuelve a pedir las métricas. Los datos anteriores quedan a la vista
  // mientras llegan los nuevos; `activo` descarta la respuesta de un pedido viejo.
  useEffect(() => {
    if (filtroInvalido) return undefined;
    let activo = true;
    setCargando(true);

    metricasServicio
      .obtenerTodas({ desde: filtro.desde, hasta: filtro.hasta })
      .then((resultado) => {
        if (!activo) return;
        setDatos(resultado);
        setError(null);
      })
      .catch((err) => {
        console.error(err);
        if (activo) setError("error-metricas");
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, [filtro.desde, filtro.hasta, filtroInvalido]);

  // Filas con etiquetas listas para los gráficos y las tablas
  const anticipacion = useMemo(
    () => (datos?.anticipacion.rangos ?? []).map((fila) => ({ ...fila, rango: textoAnticipacion(fila) })),
    [datos],
  );
  const celdasConNombre = useMemo(
    () =>
      (datos?.celdas ?? [])
        .filter((c) => c.cantidad > 0)
        .map((c) => ({ ...c, nombre_dia: DIAS_SEMANA[c.dia] })),
    [datos],
  );

  const resumen = datos?.resumen;
  const historialCorto = datos && datos.meses.length < MESES_HISTORIAL_CORTO;
  const esteMes = mesActual();
  const totalAnticipacion = anticipacion.reduce((suma, fila) => suma + fila.cantidad, 0);
  const totalProximos = (datos?.proximos ?? []).reduce((suma, fila) => suma + fila.cantidad, 0);

  let contenido;
  if (error) {
    contenido = <EstadoVacio tipo={error} />;
  } else if (!datos) {
    contenido = <Cargando mensaje="Cargando métricas..." />;
  } else if (resumen.total === 0) {
    contenido = <EstadoVacio tipo="sin-metricas" />;
  } else {
    contenido = (
      <div className={cargando ? styles.actualizando : undefined} aria-busy={cargando}>
        {historialCorto && resumen.primera_fecha && (
          <p className={styles.aviso}>
            <FaHistory aria-hidden="true" className={styles.avisoIcono} />
            <span>
              El historial se empezó a guardar el {fechaLegible(resumen.primera_fecha)}. Los gráficos se van a
              ir completando con cada actualización, dos veces por día.
            </span>
          </p>
        )}

        <div className={styles.tarjetas}>
          <TarjetaDato icono={FaMusic} etiqueta="Conciertos" valor={resumen.total} />
          <TarjetaDato
            icono={FaCalendarCheck}
            etiqueta="Vigentes"
            valor={resumen.vigentes}
            detalle="de hoy en adelante"
          />
          <TarjetaDato icono={FaHistory} etiqueta="Pasados" valor={resumen.pasados} detalle="historial" />
          <TarjetaDato icono={FaMapMarkerAlt} etiqueta="Lugares" valor={resumen.lugares} />
          <TarjetaDato icono={FaMicrophone} etiqueta="Artistas" valor={resumen.artistas} />
          <TarjetaDato
            icono={FaChartPie}
            etiqueta="Concentración"
            valor={resumen.concentracion_top5}
            sufijo=" %"
            detalle="en los 5 lugares más activos"
          />
        </div>

        <div className={styles.grilla}>
          <PanelGrafico
            ancho
            titulo="Próximos 14 días"
            descripcion={`${totalProximos} conciertos anunciados, día por día. No depende del período elegido arriba.`}
            columnas={[{ clave: "fecha", titulo: "Día", formatear: diaLargo }, COLUMNA_CANTIDAD]}
            filas={datos.proximos}
          >
            <GraficoBarras
              datos={datos.proximos}
              claveCategoria="fecha"
              formatearEje={diaCorto}
              formatearDetalle={diaLargo}
              mostrarValores
              destacar={(fila) => esFinDeSemana(fila.fecha)}
              leyenda={[
                { texto: "Lunes a viernes", color: "--color-grafico" },
                { texto: "Sábado y domingo", color: "--color-serie-finde" },
              ]}
            />
          </PanelGrafico>

          <PanelGrafico
            titulo="¿Cuándo hay más conciertos?"
            descripcion="Por día de la semana y horario de inicio. Pasá el mouse por una celda para ver el detalle."
            columnas={[
              { clave: "nombre_dia", titulo: "Día" },
              { clave: "nombre_franja", titulo: "Horario" },
              COLUMNA_CANTIDAD,
            ]}
            filas={celdasConNombre}
          >
            <GrillaDiaHorario celdas={datos.celdas} />
          </PanelGrafico>

          <PanelGrafico
            titulo="¿Con cuánta anticipación se anuncian?"
            descripcion={
              datos.anticipacion.mediana_dias != null
                ? `La mitad de los conciertos se anuncia con ${Math.round(datos.anticipacion.mediana_dias)} días o más de anticipación.`
                : "Días entre que el concierto aparece en la agenda y su fecha."
            }
            columnas={[{ clave: "rango", titulo: "Anticipación" }, COLUMNA_CANTIDAD]}
            filas={totalAnticipacion > 0 ? anticipacion : []}
          >
            {totalAnticipacion > 0 ? (
              <GraficoBarras
                datos={anticipacion}
                claveCategoria="rango"
                formatearEje={textoAnticipacionCorto}
                color="--color-serie-anticipacion"
                mostrarValores
              />
            ) : (
              <SinDatosTodavia desde={datos.ingesta.desde_que_se_mide} />
            )}
          </PanelGrafico>

          <PanelGrafico
            ancho
            titulo="Conciertos por mes"
            descripcion="Cómo evoluciona la cantidad de conciertos (los meses futuros solo cuentan lo ya anunciado)."
            columnas={[{ clave: "mes", titulo: "Mes", formatear: mesLargo }, COLUMNA_CANTIDAD]}
            filas={datos.meses}
          >
            <GraficoArea
              datos={datos.meses}
              claveX="mes"
              formatearEje={mesCorto}
              formatearDetalle={mesLargo}
              marca={{ categoria: esteMes, texto: "Este mes" }}
            />
          </PanelGrafico>

          <PanelGrafico
            titulo="Lugares más activos"
            descripcion="Los 10 lugares con más conciertos."
            columnas={[{ clave: "nombre", titulo: "Lugar" }, COLUMNA_CANTIDAD]}
            filas={datos.lugares}
          >
            <GraficoBarras
              datos={datos.lugares}
              claveCategoria="nombre"
              horizontal
              numerar
              mostrarValores
              color="--color-serie-lugares"
            />
          </PanelGrafico>

          <PanelGrafico
            titulo="Artistas que más tocan"
            descripcion="Los 10 artistas con más conciertos (sin distinguir acentos ni mayúsculas)."
            columnas={[
              { clave: "artista", titulo: "Artista" },
              { clave: "lugares", titulo: "Lugares distintos" },
              COLUMNA_CANTIDAD,
            ]}
            filas={datos.artistas}
          >
            <GraficoBarras
              datos={datos.artistas}
              claveCategoria="artista"
              horizontal
              numerar
              mostrarValores
              color="--color-serie-artistas"
            />
          </PanelGrafico>

          <PanelGrafico
            ancho
            titulo="Mapa de calor"
            descripcion="Dónde se concentran los conciertos. Los lugares a menos de ≈ 500 m se suman juntos."
          >
            <MapaCalor puntos={datos.puntos} />
          </PanelGrafico>
        </div>

        <h2 className={styles.seccion}>Calidad de los datos</h2>
        <p className={styles.seccionDescripcion}>
          Cómo viene la información que alimenta la página. Si la fuente cambia y el scraper deja de leer
          bien, se nota acá primero.
        </p>

        <div className={styles.grilla}>
          <PanelGrafico
            titulo="Datos completos"
            descripcion="Qué porcentaje de los conciertos tiene cada dato."
          >
            <MedidorCalidad calidad={datos.calidad} />
          </PanelGrafico>

          <PanelGrafico
            titulo="Conciertos nuevos por día"
            descripcion="Cuántos conciertos nuevos encontró cada actualización, en los últimos 30 días."
            columnas={[
              { clave: "fecha", titulo: "Día", formatear: diaLargo },
              { clave: "nuevos", titulo: "Nuevos" },
            ]}
            filas={datos.ingesta.desde_que_se_mide ? datos.ingesta.dias : []}
          >
            {datos.ingesta.desde_que_se_mide ? (
              <GraficoArea
                datos={datos.ingesta.dias}
                claveX="fecha"
                claveValor="nuevos"
                formatearEje={diaCorto}
                formatearDetalle={diaLargo}
                formatearValor={(n) => `${n} ${n === 1 ? "concierto nuevo" : "conciertos nuevos"}`}
              />
            ) : (
              <SinDatosTodavia desde={null} />
            )}
          </PanelGrafico>
        </div>
      </div>
    );
  }

  return (
    <div className="pagina-inicio">
      <Encabezado />

      <main className="contenedor-principal">
        <Portada
          titulo="Métricas"
          descripcion="Cómo se mueve la música en vivo en Buenos Aires y alrededores: cuándo, dónde y quiénes tocan."
        >
          {!error && (
            <>
              <DatoPortada cargando={!datos} valor={resumen?.total} texto="conciertos analizados" />
              <DatoPortada cargando={!datos} valor={resumen?.lugares} texto="lugares" />
            </>
          )}
        </Portada>

        <FiltroRango
          filtro={filtro}
          onCambiar={setFiltro}
          error={filtroInvalido ? "La fecha «desde» no puede ser posterior a «hasta»." : null}
        />

        {contenido}

        {resumen?.primera_fecha && <NotaDatos resumen={resumen} />}
      </main>

      <PieDePagina />
    </div>
  );
};

export default Metricas;
