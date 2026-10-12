import styles from "./panelGrafico.module.css";

// Tarjeta de un gráfico: título, descripción, el gráfico y sus datos como tabla.
// La tabla (desplegable) hace que la información no dependa solo de ver el gráfico:
// sirve para lectores de pantalla y para quien quiera el número exacto.
// columnas: [{ clave, titulo, formatear? }]
function PanelGrafico({ titulo, descripcion, columnas, filas, ancho = false, children }) {
  return (
    <section className={`${styles.panel} ${ancho ? styles.ancho : ""}`}>
      <h2 className={styles.titulo}>{titulo}</h2>
      {descripcion && <p className={styles.descripcion}>{descripcion}</p>}

      <div className={styles.contenido}>{children}</div>

      {columnas && filas?.length > 0 && (
        <details className={styles.tabla}>
          <summary>Ver datos en tabla</summary>
          <table>
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
        </details>
      )}
    </section>
  );
}

export default PanelGrafico;
