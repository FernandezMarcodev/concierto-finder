import styles from "./tarjetaDato.module.css";

const formato = new Intl.NumberFormat("es-AR");

// Indicador simple: un número con su etiqueta (por ejemplo, "Conciertos · 400").
function TarjetaDato({ etiqueta, valor, detalle }) {
  return (
    <div className={styles.tarjeta}>
      <span className={styles.etiqueta}>{etiqueta}</span>
      <span className={styles.valor}>{formato.format(valor)}</span>
      {detalle && <span className={styles.detalle}>{detalle}</span>}
    </div>
  );
}

export default TarjetaDato;
