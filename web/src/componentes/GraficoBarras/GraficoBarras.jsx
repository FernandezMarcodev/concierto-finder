import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import styles from "./graficoBarras.module.css";

const ALTO_COLUMNAS = 260;
const ALTO_POR_BARRA = 34;
// Eje de nombres de los rankings: más angosto en el teléfono, para dejarle lugar a las barras.
// El nombre completo siempre está en el tooltip y en la tabla.
const EJE_NOMBRES = { ancho: 176, largoMaximo: 23 };
const EJE_NOMBRES_ANGOSTO = { ancho: 124, largoMaximo: 15 };
const ejeNombres = () =>
  typeof window !== "undefined" && window.matchMedia("(max-width: 480px)").matches
    ? EJE_NOMBRES_ANGOSTO
    : EJE_NOMBRES;

const conciertos = (n) => `${n} ${n === 1 ? "concierto" : "conciertos"}`;

// Nombres largos se recortan en el eje; el nombre completo queda en el tooltip y en la tabla.
const recortar = (texto, largoMaximo) =>
  texto.length > largoMaximo ? `${texto.slice(0, largoMaximo - 1)}…` : texto;

function ContenidoTooltip({ active, payload, label, formatearDetalle }) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <div className={styles.tooltipTitulo}>{formatearDetalle(label)}</div>
      <div className={styles.tooltipValor}>{conciertos(payload[0].value)}</div>
    </div>
  );
}

/**
 * Gráfico de barras de una sola serie (cantidad de conciertos).
 * - horizontal=false: columnas, para categorías ordenadas (meses, rangos de distancia).
 * - horizontal=true: barras, para rankings con nombres largos (lugares, artistas).
 * - numerar: antepone la posición ("1. ", "2. "...) a cada nombre del ranking.
 * - marca: { categoria, texto } resalta una categoría con una franja de fondo (por ejemplo, el mes actual).
 * Los colores no se pasan como props: los pone el CSS con las variables del tema claro/oscuro.
 */
function GraficoBarras({
  datos,
  claveCategoria,
  claveValor = "cantidad",
  horizontal = false,
  mostrarValores = false,
  numerar = false,
  marca = null,
  formatearEje = (valor) => valor,
  formatearDetalle = (valor) => valor,
}) {
  const eje = ejeNombres();
  const alto = horizontal ? datos.length * ALTO_POR_BARRA + 32 : ALTO_COLUMNAS;
  // Lugar arriba para el texto de la marca
  const margenSuperior = marca ? 24 : 8;

  // Eje de categorías y eje de valores, según la orientación
  const ejeCategorias = {
    dataKey: claveCategoria,
    type: "category",
    tickLine: false,
    // Recharts le pasa al formateador el valor y su posición en el eje
    tickFormatter: horizontal
      ? (valor, indice) =>
          recortar(`${numerar ? `${indice + 1}. ` : ""}${formatearEje(valor)}`, eje.largoMaximo)
      : formatearEje,
    interval: horizontal ? 0 : "preserveStartEnd",
  };
  const ejeValores = { type: "number", allowDecimals: false, axisLine: false, tickLine: false };

  return (
    <div className={styles.grafico} style={{ height: alto }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={datos}
          layout={horizontal ? "vertical" : "horizontal"}
          margin={{ top: margenSuperior, right: mostrarValores ? 32 : 8, bottom: 0, left: 0 }}
        >
          {/* Solo las líneas de referencia del eje de valores: grilla tenue y sin cortes */}
          <CartesianGrid horizontal={!horizontal} vertical={horizontal} />
          {horizontal ? (
            <>
              <XAxis {...ejeValores} hide={mostrarValores} />
              <YAxis {...ejeCategorias} width={eje.ancho} />
            </>
          ) : (
            <>
              <XAxis {...ejeCategorias} />
              <YAxis {...ejeValores} width={32} />
            </>
          )}
          {marca && datos.some((fila) => fila[claveCategoria] === marca.categoria) && (
            <ReferenceArea
              x1={marca.categoria}
              x2={marca.categoria}
              // El texto va arriba del gráfico (en el margen superior) para que la barra no lo tape
              label={{ value: marca.texto, position: "top" }}
            />
          )}
          <Tooltip
            cursor={{ className: styles.cursor }}
            content={(props) => <ContenidoTooltip {...props} formatearDetalle={formatearDetalle} />}
          />
          <Bar
            dataKey={claveValor}
            maxBarSize={24}
            // Extremo de la barra redondeado (4 px) y la base recta, apoyada en el eje
            radius={horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]}
            isAnimationActive={false}
          >
            {mostrarValores && <LabelList dataKey={claveValor} position={horizontal ? "right" : "top"} />}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default GraficoBarras;
