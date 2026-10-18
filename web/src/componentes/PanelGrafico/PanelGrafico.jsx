import styles from "./panelGrafico.module.css";

// Tarjeta de un gráfico: título, descripción, el gráfico y sus datos como tabla.
// La tabla no se ve en pantalla (la página queda más limpia), pero los lectores de pantalla
// la leen: un gráfico de Recharts es un dibujo y, sin la tabla, sus números no llegan a quien no ve.
// columnas: [{ clave, titulo, formatear? }]
function PanelGrafico({ titulo, descripcion, columnas, filas, ancho = false, children }) {
  return (
    <section className={`${styles.panel} ${ancho ? styles.ancho : ""}`}>
      <h2 className={styles.titulo}>{titulo}</h2>
      {descripcion && <p className={styles.descripcion}>{descripcion}</p>}

      <div className={styles.contenido}>{children}</div>

      {columnas && filas?.length > 0 && (
        // El div es el que se oculta: una tabla ignora width: 1px y seguiría ocupando su ancho
        <div className={styles.soloLectores}>
          <table>
            <caption>{titulo}</caption>
            <thead>
              <tr>
                {columnas.map((columna) => (
                  <th key={columna.clave} scope="col">
                    {columna.titulo}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filas.map((fila, indice) => (
                <tr key={indice}>
                  {columnas.map((columna) => (
                    <td key={columna.clave}>
                      {columna.formatear ? columna.formatear(fila[columna.clave], fila) : fila[columna.clave]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default PanelGrafico;
