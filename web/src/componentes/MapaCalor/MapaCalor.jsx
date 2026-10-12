import { useEffect } from "react";
import { MapContainer, TileLayer, ZoomControl, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "../../utilidades/leafletGlobal";
import "leaflet.heat";
// Mismo contenedor, tiles y filtro de modo oscuro que el mapa de la página principal
import estilosMapa from "../Mapa/mapa.module.css";
import styles from "./mapaCalor.module.css";
import { useTemaActual } from "../../hooks/useTemaActual";
import { ARG_MAX_BOUNDS, CENTRO_BSAS } from "../../constantes";

// Escala secuencial de un solo tono (azul de la marca): poco = tenue, mucho = intenso.
// Nunca un arcoíris (el que trae leaflet.heat por defecto): sus colores no tienen un orden natural.
// En el tema oscuro "intenso" es más claro, porque el mapa de fondo es oscuro.
const GRADIENTES = {
  claro: { 0.25: "#4fa8de", 0.6: "#0277bd", 1: "#01304f" },
  oscuro: { 0.25: "#0d6e96", 0.6: "#0a9fdc", 1: "#d4f3ff" },
};

// Leyenda con los mismos colores. Se ordena por la clave porque JavaScript pone primero las
// claves que parecen enteros ("1"), y la escala quedaría desordenada.
const degradeCss = (gradiente) =>
  `linear-gradient(to right, ${Object.entries(gradiente)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([, color]) => color)
    .join(", ")})`;

const ZOOM_CALOR = 10;

// Capa de calor de leaflet.heat. react-leaflet no la trae: se crea a mano con el mapa de useMap.
function CapaCalor({ puntos, tema }) {
  const mapa = useMap();

  useEffect(() => {
    if (puntos.length === 0) return undefined;
    // Intensidad = raíz cuadrada de la cantidad: con la cantidad directa, un lugar con 10 conciertos
    // al lado de uno con 100 quedaría casi invisible. La raíz achica la diferencia sin invertir el orden.
    const intensidad = (cantidad) => Math.sqrt(cantidad);
    const maximo = Math.max(...puntos.map(([, , cantidad]) => intensidad(cantidad)));

    // La API manda [lng, lat, cantidad]; Leaflet usa [lat, lng, intensidad]
    const capa = L.heatLayer(
      puntos.map(([lng, lat, cantidad]) => [lat, lng, intensidad(cantidad)]),
      {
        radius: 28,
        blur: 22,
        max: maximo,
        minOpacity: 0.35,
        // leaflet.heat divide cada intensidad por 2^(maxZoom - zoom). Con el máximo por defecto (18)
        // y el mapa en zoom 10, todo pesaba 256 veces menos y casi no se veía nada.
        maxZoom: ZOOM_CALOR,
        gradient: GRADIENTES[tema] ?? GRADIENTES.claro,
      },
    ).addTo(mapa);
    return () => {
      capa.remove();
    };
  }, [mapa, puntos, tema]);

  return null;
}

function MapaCalor({ puntos }) {
  const tema = useTemaActual();
  const gradiente = GRADIENTES[tema] ?? GRADIENTES.claro;

  return (
    <>
      <div className={`${estilosMapa.contenedorMapa} ${styles.contenedor}`}>
        <MapContainer
          center={CENTRO_BSAS}
          zoom={ZOOM_CALOR}
          zoomControl={false}
          maxBounds={ARG_MAX_BOUNDS}
          maxBoundsViscosity={1.0}
          className={estilosMapa.mapa}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ZoomControl position="bottomright" />
          <CapaCalor puntos={puntos} tema={tema} />
        </MapContainer>
      </div>

      {/* Referencia de la escala: de menos a más conciertos */}
      <div className={styles.leyenda} aria-hidden="true">
        <span>Menos</span>
        <span className={styles.escala} style={{ background: degradeCss(gradiente) }} />
        <span>Más conciertos</span>
      </div>
    </>
  );
}

export default MapaCalor;
