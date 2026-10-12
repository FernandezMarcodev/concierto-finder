import { useDemorado } from "../../hooks/useDemorado";
import styles from "./cargando.module.css";

const Cargando = ({ mensaje = "Cargando conciertos..." }) => {
  const demorado = useDemorado();

  return (
    <div className={styles.cargando} role="status" aria-live="polite">
      <div className={styles.wrapperIcono}>
        <span className={styles.anillo} aria-hidden="true" />
      </div>
      <p className={styles.mensaje}>{mensaje}</p>
      {demorado && (
        <p className={styles.aviso}>
          Estamos despertando el servidor. La primera carga puede tardar hasta un minuto.
        </p>
      )}
    </div>
  );
};

export default Cargando;
