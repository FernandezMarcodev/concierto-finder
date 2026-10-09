import styles from "./encabezado.module.css";
import { FiMoon, FiSun } from "react-icons/fi";
import { useTema } from "../../hooks/useTema";

function Encabezado() {
  const { tema, alternarTema } = useTema();
  const esOscuro = tema === "oscuro";
  const etiqueta = esOscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro";

  return (
    <header className={styles.encabezado}>
      <span className={styles.marcaNombre}>Concierto Finder</span>

      <button
        type="button"
        className={styles.botonTema}
        onClick={alternarTema}
        aria-label={etiqueta}
        title={etiqueta}
      >
        {esOscuro ? <FiSun /> : <FiMoon />}
      </button>
    </header>
  );
}

export default Encabezado;
