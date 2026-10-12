import styles from "./estadoVacio.module.css";

// Configuración de mensajes según el tipo
const configs = {
  "sin-resultados": {
    titulo: "No hay conciertos",
    descripcion: "No se encontraron conciertos con los filtros seleccionados. Probá ajustar la búsqueda.",
  },
  error: {
    titulo: "Error al cargar",
    descripcion: "Hubo un problema al cargar los conciertos. Intentá de nuevo.",
  },
  "sin-metricas": {
    titulo: "No hay conciertos en este período",
    descripcion: "Probá con otro rango de fechas.",
  },
  "error-metricas": {
    titulo: "Error al cargar las métricas",
    descripcion: "Hubo un problema al pedir las métricas. Intentá de nuevo.",
  },
};

const EstadoVacio = ({ tipo = "sin-resultados" }) => {
  // Elegimos la configuración según el tipo
  const config = configs[tipo] || configs["sin-resultados"];

  return (
    <div className={styles.estadoVacio}>
      <h3>{config.titulo}</h3>
      <p>{config.descripcion}</p>
      {tipo.startsWith("error") && (
        <button type="button" onClick={() => window.location.reload()}>
          Reintentar
        </button>
      )}
    </div>
  );
};

export default EstadoVacio;
