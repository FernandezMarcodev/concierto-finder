import { useDemorado } from "../../hooks/useDemorado";
import styles from "./esqueletoLista.module.css";

// Tarjetas "fantasma" con la forma de la lista mientras cargan los conciertos. Si tarda, explica por qué.
function EsqueletoLista({ cantidad = 3 }) {
  const demorado = useDemorado();

  return (
    <div role="status" aria-live="polite">
      <p className={styles.mensaje}>
        {demorado
          ? "Estamos despertando el servidor. La primera carga puede tardar hasta un minuto…"
          : "Cargando conciertos…"}
      </p>
      {Array.from({ length: cantidad }, (_, indice) => (
        <div key={indice} className={styles.tarjeta} aria-hidden="true">
          <div className={`${styles.barra} ${styles.cabecera}`} />
          {[0, 1].map((fila) => (
            <div key={fila} className={styles.fila}>
              <div className={`${styles.barra} ${styles.fecha}`} />
              <div className={styles.textos}>
                <div className={`${styles.barra} ${styles.linea}`} />
                <div className={`${styles.barra} ${styles.lineaCorta}`} />
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export default EsqueletoLista;
