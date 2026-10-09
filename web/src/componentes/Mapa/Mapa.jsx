import { useEffect, useMemo, useRef } from "react";
import {
  MapContainer,
  TileLayer,
  ZoomControl,
  Marker,
  Popup,
  useMap,
  Circle,
  CircleMarker,
} from "react-leaflet";
import { FaMapMarkerAlt } from "react-icons/fa";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import styles from "./mapa.module.css";
import { fechaLegible, horaLegible } from "../../utilidades/texto";
import { enAmba } from "../../utilidades/geo";
import { claveGrupo } from "../../utilidades/grupos";
import { ARG_MAX_BOUNDS, CENTRO_BSAS, ZOOM_INICIAL, ZOOM_LUGAR } from "../../constantes";

// Un único ícono compartido: crearlo en cada render obliga a Leaflet a reemplazar el DOM de cada marcador.
const ICONO_LUGAR = L.divIcon({
  html: '<div class="marker-custom"><span class="marker-inner"></span></div>',
  className: "",
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12],
});

const ESTILO_USUARIO = { color: "#1a73e8", fillColor: "#1a73e8", fillOpacity: 1, weight: 2 };
const ESTILO_RADIO = { color: "#1a73e8", fillColor: "#1a73e8", fillOpacity: 0.05, weight: 2 };

// Encuadra el círculo de búsqueda cuando cambia la ubicación del usuario o el radio.
const AjustarVistaRadio = ({ ubicacionUsuario, radioKm }) => {
  const map = useMap();

  useEffect(() => {
    if (!ubicacionUsuario || !radioKm) return;
    const limites = L.latLng(ubicacionUsuario.lat, ubicacionUsuario.lng).toBounds(radioKm * 2000);
    map.fitBounds(limites, { padding: [24, 24] });
  }, [ubicacionUsuario, radioKm, map]);

  return null;
};

// Vuela al lugar del concierto elegido con "Ver en mapa" y abre su popup.
const EnfocarSeleccion = ({ seleccion, grupos, marcadores }) => {
  const map = useMap();

  useEffect(() => {
    if (!seleccion) return;
    const grupo = grupos.find((g) => g.conciertos.some((c) => c.id === seleccion.id));
    if (!grupo) return;

    // Primero el popup y después el vuelo: el auto-pan del popup cancelaría la animación.
    marcadores.current[claveGrupo(grupo)]?.openPopup();
    map.flyTo([grupo.lat, grupo.lng], ZOOM_LUGAR, { duration: 0.8 });
    // Solo reacciona a una nueva selección, no a cada cambio de filtros
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seleccion, map]);

  return null;
};

const FechaHora = ({ concierto }) => {
  const hora = horaLegible(concierto.hora);
  return (
    <>
      {fechaLegible(concierto.fecha)}
      {hora ? ` · ${hora}` : ""}
    </>
  );
};

const ContenidoPopup = ({ grupo, seleccionadoId }) => {
  const lista = grupo.conciertos;
  const lugar = grupo.ubicacion_detalle?.nombre || "Ubicación";

  if (lista.length === 1) {
    const [concierto] = lista;
    return (
      <div className={styles.popupContent}>
        <div className={styles.popupTitle}>{concierto.artista}</div>
        {concierto.nombre && concierto.nombre !== concierto.artista && (
          <div className={styles.popupSub}>{concierto.nombre}</div>
        )}
        <div className={styles.popupLugar}>
          <FaMapMarkerAlt className={styles.iconoLugar} />
          {lugar}
        </div>
        <div className={styles.popupSub}>
          <FechaHora concierto={concierto} />
        </div>
        {concierto.url_evento && (
          <div className={styles.popupActions}>
            <a href={concierto.url_evento} target="_blank" rel="noopener noreferrer">
              Entradas
            </a>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={styles.popupContent}>
      <div className={styles.popupTitle}>
        {lugar} — {lista.length} conciertos
      </div>
      <div className={styles.popupList}>
        {lista.map((c) => (
          <div
            key={c.id}
            className={`${styles.popupItem} ${c.id === seleccionadoId ? styles.popupItemSeleccionado : ""}`}
          >
            <div className={styles.popupItemTitulo}>
              {c.artista}
              {c.nombre && c.nombre !== c.artista ? ` — ${c.nombre}` : ""}
            </div>
            <div className={styles.popupItemMeta}>
              <FechaHora concierto={c} />
            </div>
            {c.url_evento && (
              <div className={styles.popupActions}>
                <a href={c.url_evento} target="_blank" rel="noopener noreferrer">
                  Entradas
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

function Mapa({ grupos = [], ubicacionUsuario, radioKm, seleccion }) {
  const marcadores = useRef({});

  // Solo se dibujan los lugares con coordenadas dentro de AMBA
  const gruposVisibles = useMemo(
    () => grupos.filter((grupo) => grupo.lat != null && enAmba(grupo)),
    [grupos],
  );

  return (
    <div className={styles.contenedorMapa}>
      <MapContainer
        center={CENTRO_BSAS}
        zoom={ZOOM_INICIAL}
        zoomControl={false}
        maxBounds={ARG_MAX_BOUNDS}
        maxBoundsViscosity={1.0}
        style={{ width: "100%", height: "100%" }}
        className={styles.mapa}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoomControl position="bottomright" />
        <AjustarVistaRadio ubicacionUsuario={ubicacionUsuario} radioKm={radioKm} />

        {ubicacionUsuario && (
          <CircleMarker
            center={[ubicacionUsuario.lat, ubicacionUsuario.lng]}
            radius={7}
            pathOptions={ESTILO_USUARIO}
          />
        )}

        {ubicacionUsuario && radioKm > 0 && (
          <Circle
            center={[ubicacionUsuario.lat, ubicacionUsuario.lng]}
            radius={radioKm * 1000}
            pathOptions={ESTILO_RADIO}
          />
        )}

        {gruposVisibles.map((grupo) => {
          const clave = claveGrupo(grupo);
          return (
            <Marker
              key={clave}
              position={[grupo.lat, grupo.lng]}
              icon={ICONO_LUGAR}
              ref={(marcador) => {
                if (marcador) marcadores.current[clave] = marcador;
                else delete marcadores.current[clave];
              }}
            >
              <Popup>
                <ContenidoPopup grupo={grupo} seleccionadoId={seleccion?.id} />
              </Popup>
            </Marker>
          );
        })}

        <EnfocarSeleccion seleccion={seleccion} grupos={gruposVisibles} marcadores={marcadores} />
      </MapContainer>
    </div>
  );
}

export default Mapa;
