import styles from "./tarjetaDato.module.css";

const formato = new Intl.NumberFormat("es-AR");

// Indicador simple: un número con su etiqueta (por ejemplo, "Conciertos · 400") y un ícono opcional.
// sufijo: por ejemplo " %". Sin valor (null) se muestra una raya.
function TarjetaDato({ etiqueta, valor, detalle, icono: Icono, sufijo = "" }) {
  return (
    <div className={styles.tarjeta}>
      <span className={styles.etiqueta}>
        {Icono && (
          <span className={styles.icono} aria-hidden="true">
            <Icono />
          </span>
        )}
        {etiqueta}
      </span>
      <span className={styles.valor}>{valor == null ? "—" : `${formato.format(valor)}${sufijo}`}</span>
      {detalle && <span className={styles.detalle}>{detalle}</span>}
    </div>
  );
}

export default TarjetaDato;
