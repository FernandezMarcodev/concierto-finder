import { FaGithub } from "react-icons/fa";
import { Link } from "react-router-dom";
import styles from "./pieDePagina.module.css";

const PieDePagina = () => {
  return (
    <footer className={styles.pieDePagina}>
      <div className={styles.contenedor}>
        <div>
          <strong>Concierto Finder</strong>
          <p className={styles.lema}>Los próximos conciertos de Buenos Aires y alrededores, en un mapa.</p>
        </div>

        <nav className={styles.enlaces} aria-label="Pie de página">
          <Link to="/">Conciertos</Link>
          <Link to="/metricas">Métricas</Link>
          <a
            href="https://github.com/FernandezMarcodev/concierto-finder"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaGithub aria-hidden="true" /> GitHub
          </a>
        </nav>
      </div>

      <p className={styles.fuentes}>
        Datos de{" "}
        <a href="https://www.agendade.com.ar" target="_blank" rel="noopener noreferrer">
          agendade.com.ar
        </a>{" "}
        · Mapa ©{" "}
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">
          OpenStreetMap
        </a>{" "}
        · © {new Date().getFullYear()} Concierto Finder
      </p>
    </footer>
  );
};

export default PieDePagina;
