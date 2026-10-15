import styles from "./medidorCalidad.module.css";

const formatoPorcentaje = new Intl.NumberFormat("es-AR", { maximumFractionDigits: 0 });

// Qué se mide y con qué campo de /api/metricas/calidad
const CAMPOS = [
  { clave: "sin_fecha", texto: "Con fecha" },
  { clave: "sin_hora", texto: "Con hora" },
  { clave: "sin_entradas", texto: "Con link de entradas" },
  { clave: "sin_ubicacion", texto: "Con lugar en el mapa" },
];

/**
 * Completitud de los datos: una barra por campo con el porcentaje de conciertos que lo tienen.
 * Es una proporción de un total, así que la forma es un medidor (no un gráfico de barras con eje):
 * la parte llena es lo completo y el riel, el 100 %.
 */
function MedidorCalidad({ calidad }) {
  const { total } = calidad;

  return (
    <ul className={styles.lista}>
      {CAMPOS.map(({ clave, texto }) => {
        const completos = total - calidad[clave];
        const porcentaje = total > 0 ? (100 * completos) / total : 0;
        return (
          <li key={clave} className={styles.item}>
            <div className={styles.encabezado}>
              <span className={styles.texto}>{texto}</span>
              <span className={styles.valor}>
                <strong>{formatoPorcentaje.format(porcentaje)} %</strong> · {completos} de {total}
              </span>
            </div>
            <div
              className={styles.riel}
              role="meter"
              aria-label={texto}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={Math.round(porcentaje)}
            >
              <span className={styles.relleno} style={{ width: `${porcentaje}%` }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export default MedidorCalidad;
