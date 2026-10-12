import { useEffect, useMemo, useState } from "react";
import { FaCalendarCheck, FaHistory, FaMapMarkerAlt, FaMicrophone, FaMusic } from "react-icons/fa";
import Encabezado from "../componentes/Encabezado/Encabezado";
import Portada, { DatoPortada } from "../componentes/Portada/Portada";
import PieDePagina from "../componentes/PieDePagina/PieDePagina";
import Cargando from "../componentes/Cargando/Cargando";
import EstadoVacio from "../componentes/EstadoVacio/EstadoVacio";
import FiltroRango from "../componentes/FiltroRango/FiltroRango";
import TarjetaDato from "../componentes/TarjetaDato/TarjetaDato";
import PanelGrafico from "../componentes/PanelGrafico/PanelGrafico";
import GraficoBarras from "../componentes/GraficoBarras/GraficoBarras";
import MapaCalor from "../componentes/MapaCalor/MapaCalor";
import { metricasServicio } from "../servicios/metricasServicio";
import { fechaIso, mesCorto, mesLargo } from "../utilidades/fechas";
import { fechaLegible } from "../utilidades/texto";
import { PERIODO_INICIAL, PERIODOS } from "../utilidades/periodos";
import styles from "./metricas.module.css";

const filtroInicial = () => ({
  periodo: PERIODO_INICIAL,
  ...PERIODOS.find((p) => p.id === PERIODO_INICIAL).calcular(new Date()),
});

// Etiqueta de un rango de distancia: "0–5 km" o, el último, "40 km o más"
const textoRango = (fila) =>
  fila.hasta_km == null ? `${fila.desde_km} km o más` : `${fila.desde_km}–${fila.hasta_km} km`;

// Versión corta para el eje del gráfico, que en el teléfono tiene poco lugar: "0–5", "40+"
const textoRangoCorto = (texto) => texto.replace(" km o más", "+").replace(" km", "");

const COLUMNA_CANTIDAD = { clave: "cantidad", titulo: "Conciertos" };

// Con menos meses que esto, se avisa que el historial recién se está armando
const MESES_HISTORIAL_CORTO = 4;

// "2026-10": el mes actual, para marcarlo en el gráfico mensual
const mesActual = () => fechaIso(new Date()).slice(0, 7);

function NotaDatos({ resumen }) {
  const sinFecha = resumen.sin_fecha;
  return (
    <p className={styles.nota}>
      Datos acumulados desde el {fechaLegible(resumen.primera_fecha)}. Solo cuentan los conciertos publicados
      en agendade.com.ar dentro de AMBA; los cancelados o reprogramados pueden figurar igual.
      {sinFecha === 1 && " 1 concierto no tiene fecha y no aparece en el gráfico por mes."}
      {sinFecha > 1 && ` ${sinFecha} conciertos no tienen fecha y no aparecen en el gráfico por mes.`}
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

  // Los rangos de distancia con su etiqueta, para el gráfico y la tabla
  const rangos = useMemo(
    () => (datos?.rangos ?? []).map((fila) => ({ ...fila, rango: textoRango(fila) })),
    [datos],
  );

  const resumen = datos?.resumen;
  const historialCorto = datos && datos.meses.length < MESES_HISTORIAL_CORTO;
  const esteMes = mesActual();

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
        </div>

        <div className={styles.grilla}>
          <PanelGrafico
            ancho
            titulo="Conciertos por mes"
            descripcion="Estacionalidad: cuántos conciertos hubo (o hay anunciados) cada mes."
            columnas={[{ clave: "mes", titulo: "Mes", formatear: mesLargo }, COLUMNA_CANTIDAD]}
            filas={datos.meses}
          >
            <GraficoBarras
              datos={datos.meses}
              claveCategoria="mes"
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
            <GraficoBarras datos={datos.lugares} claveCategoria="nombre" horizontal numerar mostrarValores />
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
            />
          </PanelGrafico>

          <PanelGrafico
            titulo="Distancia al Obelisco"
            descripcion="Cuántos conciertos hay en cada rango de distancia, en km y en línea recta."
            columnas={[{ clave: "rango", titulo: "Distancia" }, COLUMNA_CANTIDAD]}
            filas={rangos}
          >
            <GraficoBarras
              datos={rangos}
              claveCategoria="rango"
              formatearEje={textoRangoCorto}
              mostrarValores
            />
          </PanelGrafico>

          <PanelGrafico
            titulo="Mapa de calor"
            descripcion="Dónde se concentran los conciertos. Los lugares a menos de ≈ 500 m se suman juntos."
          >
            <MapaCalor puntos={datos.puntos} />
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
