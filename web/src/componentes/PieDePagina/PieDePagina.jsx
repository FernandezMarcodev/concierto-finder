import { FaGithub } from "react-icons/fa";
import styles from "./pieDePagina.module.css";

const PieDePagina = () => {
  return (
    <footer className={styles.pieDePagina}>
      <div className={styles.contenedor}>
        <div className={styles.enlaces}>
          <a
            href="https://github.com/FernandezMarcodev/concierto-finder"
            target="_blank"
            rel="noopener noreferrer"
          >
            <FaGithub size={20} /> GitHub
          </a>
        </div>
      </div>
      <p className={styles.copy}>
        &copy; {new Date().getFullYear()} Concierto Finder. Todos los derechos reservados.
      </p>
    </footer>
  );
};

export default PieDePagina;
