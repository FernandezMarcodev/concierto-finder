import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import styles from "./graficoArea.module.css";

const ALTO = 240;

function ContenidoTooltip({ active, payload, label, formatearDetalle, formatearValor }) {
  if (!active || !payload?.length) return null;
  return (
    <div className={styles.tooltip}>
      <div className={styles.tooltipTitulo}>{formatearDetalle(label)}</div>
      <div className={styles.tooltipValor}>{formatearValor(payload[0].value)}</div>
    </div>
  );
}

/**
 * Serie de tiempo: una línea de 2 px con un área suave debajo. Se usa para lo que evoluciona
 * en el tiempo (conciertos por mes, conciertos nuevos por día de ingesta), donde importa la
 * tendencia más que cada valor por separado.
 * - color: variable CSS de la serie (por defecto, el azul de los gráficos).
 * - marca: { categoria, texto } resalta un punto del eje con una línea vertical (por ejemplo, el mes
 *   actual). El texto va en una leyenda arriba del gráfico: dentro del dibujo se superponía con la serie.
 */
function GraficoArea({
  datos,
  claveX,
  claveValor = "cantidad",
  color = "--color-grafico",
  marca = null,
  formatearEje = (valor) => valor,
  formatearDetalle = (valor) => valor,
  formatearValor = (n) => `${n} ${n === 1 ? "concierto" : "conciertos"}`,
}) {
  const hayMarca = marca && datos.some((fila) => fila[claveX] === marca.categoria);

  return (
    <div style={{ "--color-serie": `var(${color})` }}>
      {hayMarca && (
        <div className={styles.leyenda}>
          <span className={styles.leyendaMuestra} aria-hidden="true" />
          {marca.texto}
        </div>
      )}
      <div className={styles.grafico} style={{ height: ALTO }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={datos} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey={claveX}
              tickLine={false}
              tickFormatter={formatearEje}
              interval="preserveStartEnd"
              minTickGap={16}
            />
            <YAxis allowDecimals={false} axisLine={false} tickLine={false} width={32} />
            {hayMarca && (
              // En una serie de tiempo cada mes es un punto: la marca es una línea vertical, no una franja
              <ReferenceLine x={marca.categoria} className={styles.marca} />
            )}
            <Tooltip
              cursor={{ className: styles.cursor }}
              content={(props) => (
                <ContenidoTooltip
                  {...props}
                  formatearDetalle={formatearDetalle}
                  formatearValor={formatearValor}
                />
              )}
            />
            <Area
              type="monotone"
              dataKey={claveValor}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, className: styles.punto }}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default GraficoArea;
