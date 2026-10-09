import styles from "./tarjetaGrupo.module.css";
import { FaMapMarkerAlt, FaCalendar, FaClock, FaMapPin, FaTicketAlt, FaDirections } from "react-icons/fa";
import { fechaLegible, horaLegible } from "../../utilidades/texto";

const TarjetaGrupo = ({ grupo, seleccionadoId, onVerEnMapa }) => {
  const ubicacion = grupo.ubicacion_detalle?.nombre || "Sin ubicación definida";
  const conciertos = grupo.conciertos;

  return (
    <div className={styles.grupo}>
      <div className={styles.cabecera}>
        <div className={styles.lugar}>
          <FaMapMarkerAlt className={styles.iconoLugar} />
          <span className={styles.nombreLugar}>{ubicacion}</span>
        </div>
        <span className={styles.contador}>
          {conciertos.length} {conciertos.length === 1 ? "concierto" : "conciertos"}
        </span>
      </div>

      <div className={styles.lista}>
        {conciertos.map((concierto) => (
          <div
            key={concierto.id}
            className={`${styles.fila} ${concierto.id === seleccionadoId ? styles.filaSeleccionada : ""}`}
          >
            <div className={styles.filaPrincipal}>
              <div className={styles.filaInfo}>
                <div className={styles.tituloFila}>
                  <span className={styles.artistaFila}>{concierto.artista}</span>
                  {concierto.nombre && concierto.nombre !== concierto.artista && (
                    <span className={styles.nombreFila}>{concierto.nombre}</span>
                  )}
                </div>

                <div className={styles.metaFila}>
                  <span className={styles.metaItem}>
                    <FaCalendar className={styles.iconoMeta} />
                    {fechaLegible(concierto.fecha)}
                  </span>
                  {horaLegible(concierto.hora) && (
                    <span className={styles.metaItem}>
                      <FaClock className={styles.iconoMeta} />
                      {horaLegible(concierto.hora)}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className={styles.filaAcciones}>
              {concierto.ubicacion_detalle?.coordenadas && (
                <>
                  <button className={styles.botonMapa} onClick={() => onVerEnMapa(concierto)}>
                    <FaMapPin className={styles.iconoAccion} />
                    Ver en mapa
                  </button>
                  <a
                    className={styles.enlaceSecundario}
                    href={`https://www.google.com/maps/dir/?api=1&destination=${concierto.ubicacion_detalle.coordenadas[1]},${concierto.ubicacion_detalle.coordenadas[0]}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <FaDirections className={styles.iconoAccion} />
                    Cómo llegar
                  </a>
                </>
              )}

              {concierto.url_evento && (
                <a
                  className={styles.botonEntradas}
                  href={concierto.url_evento}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FaTicketAlt className={styles.iconoAccion} />
                  Entradas
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TarjetaGrupo;
