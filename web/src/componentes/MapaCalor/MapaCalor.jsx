import { useEffect } from "react";
import { CircleMarker, MapContainer, TileLayer, ZoomControl, useMap } from "react-leaflet";
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
// Empieza transparente para que el calor se funda con el mapa, sin bordes duros. En el tema oscuro
// "intenso" es más claro (brilla sobre el fondo oscuro); en el claro, el pico no llega a negro.
const GRADIENTES = {
  claro: { 0: "rgba(2, 119, 189, 0)", 0.3: "rgba(79, 168, 222, 0.55)", 0.6: "#0277bd", 1: "#014a7f" },
  oscuro: { 0: "rgba(10, 159, 220, 0)", 0.3: "rgba(10, 159, 220, 0.5)", 0.65: "#0a9fdc", 1: "#d4f3ff" },
};

// Punto chico en cada lugar, encima del calor: el calor muestra la concentración y el punto, dónde está cada lugar
const COLOR_LUGAR = { claro: "#014a7f", oscuro: "#d4f3ff" };

// Leyenda con los mismos colores. Se ordena por la clave porque JavaScript pone primero las
// claves que parecen enteros ("1"), y la escala quedaría desordenada.
const degradeCss = (gradiente) =>
  `linear-gradient(to right, ${Object.entries(gradiente)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([, color]) => color)
    .join(", ")})`;

const ZOOM_CALOR = 10;
// Un poco al oeste del Obelisco: a todo el ancho, centrado en el Obelisco se veía sobre todo el río
const CENTRO_CALOR = [CENTRO_BSAS[0], CENTRO_BSAS[1] - 0.12];

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
        // Radio y difuminado en píxeles, pensados para el zoom inicial (todo el AMBA): más grandes,
        // las manchas de los lugares del centro se pegan en una sola y no se distingue nada
        radius: 22,
        blur: 18,
        // Un poco por encima del máximo: así el lugar con más conciertos no satura en una mancha plana
        max: maximo * 1.25,
        minOpacity: 0.08,
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
          center={CENTRO_CALOR}
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
          {puntos.map(([lng, lat]) => (
            <CircleMarker
              key={`${lng},${lat}`}
              center={[lat, lng]}
              radius={2.5}
              interactive={false}
              pathOptions={{
                stroke: false,
                fillColor: COLOR_LUGAR[tema] ?? COLOR_LUGAR.claro,
                fillOpacity: 0.9,
              }}
            />
          ))}
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
