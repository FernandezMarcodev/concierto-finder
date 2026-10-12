import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import styles from "./graficoBarras.module.css";

const ALTO_COLUMNAS = 260;
const ALTO_POR_BARRA = 34;
const LARGO_MAXIMO_ETIQUETA = 20;

const conciertos = (n) => `${n} ${n === 1 ? "concierto" : "conciertos"}`;

// Nombres largos se recortan en el eje; el nombre completo queda en el tooltip y en la tabla.
const recortar = (texto) =>
  texto.length > LARGO_MAXIMO_ETIQUETA ? `${texto.slice(0, LARGO_MAXIMO_ETIQUETA - 1)}…` : texto;

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
 * Los colores no se pasan como props: los pone el CSS con las variables del tema claro/oscuro.
 */
function GraficoBarras({
  datos,
  claveCategoria,
  claveValor = "cantidad",
  horizontal = false,
  mostrarValores = false,
  formatearEje = (valor) => valor,
  formatearDetalle = (valor) => valor,
}) {
  const alto = horizontal ? datos.length * ALTO_POR_BARRA + 32 : ALTO_COLUMNAS;

  // Eje de categorías y eje de valores, según la orientación
  const ejeCategorias = {
    dataKey: claveCategoria,
    type: "category",
    tickLine: false,
    tickFormatter: horizontal ? (valor) => recortar(formatearEje(valor)) : formatearEje,
    interval: horizontal ? 0 : "preserveStartEnd",
  };
  const ejeValores = { type: "number", allowDecimals: false, axisLine: false, tickLine: false };

  return (
    <div className={styles.grafico} style={{ height: alto }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={datos}
          layout={horizontal ? "vertical" : "horizontal"}
          margin={{ top: 8, right: mostrarValores ? 32 : 8, bottom: 0, left: 0 }}
        >
          {/* Solo las líneas de referencia del eje de valores: grilla tenue y sin cortes */}
          <CartesianGrid horizontal={!horizontal} vertical={horizontal} />
          {horizontal ? (
            <>
              <XAxis {...ejeValores} hide={mostrarValores} />
              <YAxis {...ejeCategorias} width={150} />
            </>
          ) : (
            <>
              <XAxis {...ejeCategorias} />
              <YAxis {...ejeValores} width={32} />
            </>
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
