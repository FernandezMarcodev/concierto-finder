import styles from "./filtros.module.css";
import { useEffect, useMemo, useRef, useState } from "react";
import { FaLocationArrow, FaSearch, FaTimes } from "react-icons/fa";
import { normalizarTexto } from "../../utilidades/texto";
import { RADIO_ATAJOS, RADIO_MAX, RADIO_MIN } from "../../constantes";

const MAX_SUGERENCIAS = 8;

const OPCIONES_GEOLOCALIZACION = { enableHighAccuracy: false, timeout: 10000, maximumAge: 5 * 60 * 1000 };

function mensajeErrorUbicacion(error) {
  if (error?.code === 1) {
    return "Bloqueaste el acceso a tu ubicación. Habilitalo en los permisos del navegador.";
  }
  return "No pudimos obtener tu ubicación. Intentá de nuevo.";
}

function Filtros({ filtros, setFiltros, artistas }) {
  const [abierto, setAbierto] = useState(false);
  const [buscandoUbicacion, setBuscandoUbicacion] = useState(false);
  const [errorUbicacion, setErrorUbicacion] = useState(null);
  const contenedorRef = useRef(null);
  const busqueda = filtros.artista;
  const ubicacionActiva = Boolean(filtros.ubicacionActual);

  // Actualización funcional: la geolocalización responde de forma asíncrona y
  // no debe pisar lo que el usuario haya escrito mientras tanto.
  const actualizar = (cambios) => setFiltros((previos) => ({ ...previos, ...cambios }));

  // Los nombres normalizados se calculan una vez, no en cada tecla.
  const artistasNormalizados = useMemo(
    () => artistas.map((artista) => ({ artista, normalizado: normalizarTexto(artista) })),
    [artistas],
  );

  // Cierra el desplegable al hacer clic fuera del buscador.
  useEffect(() => {
    const alHacerClicFuera = (evento) => {
      if (!contenedorRef.current?.contains(evento.target)) {
        setAbierto(false);
      }
    };
    document.addEventListener("mousedown", alHacerClicFuera);
    return () => document.removeEventListener("mousedown", alHacerClicFuera);
  }, []);

  const consulta = normalizarTexto(busqueda);

  const sugerencias = consulta
    ? artistasNormalizados
        .filter(({ normalizado }) => normalizado.includes(consulta))
        .slice(0, MAX_SUGERENCIAS)
        .map(({ artista }) => artista)
    : [];

  const elegirArtista = (artista) => {
    actualizar({ artista });
    setAbierto(false);
  };

  const limpiarArtista = () => actualizar({ artista: "" });

  const alternarUbicacion = () => {
    setErrorUbicacion(null);

    if (ubicacionActiva) {
      actualizar({ ubicacionActual: null });
      return;
    }

    if (!navigator.geolocation) {
      setErrorUbicacion("Tu navegador no permite obtener la ubicación.");
      return;
    }

    setBuscandoUbicacion(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setBuscandoUbicacion(false);
        actualizar({
          ubicacionActual: { lat: pos.coords.latitude, lng: pos.coords.longitude },
        });
      },
      (err) => {
        setBuscandoUbicacion(false);
        setErrorUbicacion(mensajeErrorUbicacion(err));
      },
      OPCIONES_GEOLOCALIZACION,
    );
  };

  const descripcionUbicacion = buscandoUbicacion
    ? "Obteniendo tu ubicación…"
    : ubicacionActiva
      ? `Mostrando conciertos a menos de ${filtros.radio} km`
      : "Filtrá por distancia a donde estás";

  // Porcentaje recorrido del slider, para pintar el tramo activo de la barra
  const progresoRadio = ((filtros.radio - RADIO_MIN) / (RADIO_MAX - RADIO_MIN)) * 100;

  return (
    <section className={styles.filtros} aria-labelledby="tituloFiltros">
      <h2 id="tituloFiltros" className={styles.titulo}>
        Filtrar conciertos
      </h2>

      <div className={styles.columnas}>
        {/* Buscador por artista */}
        <div className={styles.campo}>
          <label htmlFor="buscadorArtista" className={styles.etiqueta}>
            Artista
          </label>
          <div className={styles.buscador} ref={contenedorRef}>
            <div className={styles.buscadorCampo}>
              <FaSearch className={styles.buscadorIcono} aria-hidden="true" />
              <input
                id="buscadorArtista"
                type="text"
                className={styles.buscadorInput}
                placeholder="Escribí el nombre de un artista"
                value={busqueda}
                onChange={(e) => {
                  actualizar({ artista: e.target.value });
                  setAbierto(true);
                }}
                onFocus={() => setAbierto(true)}
                onKeyDown={(e) => {
                  if (e.key === "Escape") setAbierto(false);
                  if (e.key === "Enter" && sugerencias.length > 0) {
                    e.preventDefault();
                    elegirArtista(sugerencias[0]);
                  }
                }}
                autoComplete="off"
              />
              {busqueda && (
                <button
                  type="button"
                  className={styles.buscadorLimpiar}
                  onClick={limpiarArtista}
                  aria-label="Limpiar búsqueda"
                >
                  <FaTimes />
                </button>
              )}
            </div>

            {abierto && sugerencias.length > 0 && (
              <ul className={styles.sugerencias}>
                {sugerencias.map((artista) => (
                  <li key={artista}>
                    <button type="button" onClick={() => elegirArtista(artista)}>
                      {artista}
                    </button>
                  </li>
                ))}
              </ul>
            )}

            {abierto && consulta && sugerencias.length === 0 && (
              <p className={styles.sinResultados}>Sin resultados para "{busqueda}"</p>
            )}
          </div>
        </div>

        {/* Cercanía: interruptor de ubicación + radio */}
        <div className={styles.campo}>
          <span className={styles.etiqueta} id="etiquetaUbicacion">
            Cercanía
          </span>
          <button
            type="button"
            role="switch"
            aria-checked={ubicacionActiva}
            aria-labelledby="etiquetaUbicacion textoUbicacion"
            aria-busy={buscandoUbicacion}
            disabled={buscandoUbicacion}
            className={`${styles.interruptor} ${ubicacionActiva ? styles.interruptorActivo : ""}`}
            onClick={alternarUbicacion}
          >
            <span className={styles.interruptorIcono} aria-hidden="true">
              {buscandoUbicacion ? <span className={styles.girando} /> : <FaLocationArrow />}
            </span>
            <span className={styles.interruptorTextos} id="textoUbicacion">
              <span className={styles.interruptorTitulo}>Cerca de mí</span>
              <span className={styles.interruptorDetalle}>{descripcionUbicacion}</span>
            </span>
            <span className={styles.interruptorPista} aria-hidden="true" />
          </button>

          {errorUbicacion && (
            <p className={styles.error} role="alert">
              {errorUbicacion}
            </p>
          )}

          {ubicacionActiva && (
            <div className={styles.radio}>
              <div className={styles.radioEncabezado}>
                <label htmlFor="radioKm" className={styles.radioEtiqueta}>
                  Radio de búsqueda
                </label>
                <output htmlFor="radioKm" className={styles.radioValor}>
                  {filtros.radio} km
                </output>
              </div>

              <input
                id="radioKm"
                type="range"
                className={styles.radioSlider}
                style={{ "--progreso": `${progresoRadio}%` }}
                min={RADIO_MIN}
                max={RADIO_MAX}
                step="1"
                value={filtros.radio}
                onChange={(e) => actualizar({ radio: parseInt(e.target.value, 10) })}
              />

              <div className={styles.radioAtajos} role="group" aria-label="Radios rápidos">
                {RADIO_ATAJOS.map((km) => (
                  <button
                    key={km}
                    type="button"
                    className={`${styles.radioAtajo} ${filtros.radio === km ? styles.radioAtajoActivo : ""}`}
                    aria-pressed={filtros.radio === km}
                    onClick={() => actualizar({ radio: km })}
                  >
                    {km} km
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default Filtros;
