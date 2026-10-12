import styles from "./portada.module.css";

// Encabezado de cada página: logo, título, descripción y, debajo, datos destacados (children).
function Portada({ titulo, descripcion, children }) {
  return (
    <section className={styles.portada}>
      <img src="/logo.png" alt="" className={styles.logo} />
      <div className={styles.textos}>
        <h1 className={styles.titulo}>{titulo}</h1>
        {descripcion && <p className={styles.descripcion}>{descripcion}</p>}
        {children && <div className={styles.datos}>{children}</div>}
      </div>
    </section>
  );
}

// Un dato destacado de la portada: "186 conciertos". `cargando` muestra un lugar reservado.
export function DatoPortada({ valor, texto, cargando = false }) {
  return (
    <span className={styles.dato}>
      {cargando ? <span className={styles.datoCargando} aria-hidden="true" /> : <strong>{valor}</strong>}
      {texto}
    </span>
  );
}

export default Portada;
