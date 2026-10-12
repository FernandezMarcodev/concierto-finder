import styles from "./encabezado.module.css";
import { FiMoon, FiSun } from "react-icons/fi";
import { Link, NavLink } from "react-router-dom";
import { useTema } from "../../hooks/useTema";

const claseEnlace = ({ isActive }) => `${styles.enlace} ${isActive ? styles.enlaceActivo : ""}`;

function Encabezado() {
  const { tema, alternarTema } = useTema();
  const esOscuro = tema === "oscuro";
  const etiqueta = esOscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro";

  return (
    <header className={styles.encabezado}>
      <Link to="/" className={styles.marcaNombre}>
        Concierto Finder
      </Link>

      <div className={styles.acciones}>
        <nav className={styles.navegacion} aria-label="Secciones">
          {/* end: "Conciertos" solo se marca en "/" exacto, no en "/metricas" */}
          <NavLink to="/" end className={claseEnlace}>
            Conciertos
          </NavLink>
          <NavLink to="/metricas" className={claseEnlace}>
            Métricas
          </NavLink>
        </nav>

        <button
          type="button"
          className={styles.botonTema}
          onClick={alternarTema}
          aria-label={etiqueta}
          title={etiqueta}
        >
          {esOscuro ? <FiSun /> : <FiMoon />}
        </button>
      </div>
    </header>
  );
}

export default Encabezado;
