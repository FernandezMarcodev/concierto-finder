import styles from "./tarjetaGrupo.module.css";
import { FaMapMarkerAlt, FaClock, FaMapPin, FaTicketAlt, FaDirections } from "react-icons/fa";
import { horaLegible } from "../../utilidades/texto";
import { etiquetaCercania, partesFecha } from "../../utilidades/fechas";

// Bloque de fecha tipo entrada: día de la semana, número grande y mes. Sin fecha: "A confirmar".
const BloqueFecha = ({ fecha }) => {
  const partes = partesFecha(fecha);
  if (!partes) {
    return (
      <div className={`${styles.bloqueFecha} ${styles.bloqueFechaSinDato}`}>
        <span className={styles.fechaConfirmar}>A confirmar</span>
      </div>
    );
  }
  return (
    <div className={styles.bloqueFecha} aria-hidden="true">
      <span className={styles.fechaDiaSemana}>{partes.diaSemana}</span>
      <span className={styles.fechaDia}>{partes.dia}</span>
      <span className={styles.fechaMes}>{partes.mes}</span>
    </div>
  );
};

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
        {conciertos.map((concierto) => {
          const hora = horaLegible(concierto.hora);
          const cercania = etiquetaCercania(concierto.fecha);
          const partes = partesFecha(concierto.fecha);

          return (
            <div
              key={concierto.id}
              className={`${styles.fila} ${concierto.id === seleccionadoId ? styles.filaSeleccionada : ""}`}
            >
              <div className={styles.filaPrincipal}>
                <BloqueFecha fecha={concierto.fecha} />

                <div className={styles.filaInfo}>
                  <div className={styles.tituloFila}>
                    <span className={styles.artistaFila}>{concierto.artista}</span>
                    {cercania && <span className={styles.etiquetaCercania}>{cercania}</span>}
                  </div>
                  {concierto.nombre && concierto.nombre !== concierto.artista && (
                    <div className={styles.nombreFila}>{concierto.nombre}</div>
                  )}

                  <div className={styles.metaFila}>
                    {/* La fecha completa para lectores de pantalla (el bloque visual está oculto) */}
                    {partes && (
                      <span className={styles.soloLectores}>
                        {partes.diaSemana} {partes.dia} de {partes.mes}
                      </span>
                    )}
                    {hora ? (
                      <span className={styles.metaItem}>
                        <FaClock className={styles.iconoMeta} />
                        {hora} h
                      </span>
                    ) : (
                      <span className={styles.metaItem}>Horario a confirmar</span>
                    )}
                  </div>
                </div>
              </div>

              <div className={styles.filaAcciones}>
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
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TarjetaGrupo;
