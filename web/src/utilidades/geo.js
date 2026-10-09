import { AMBA } from "../constantes";

// El backend serializa las coordenadas como [lng, lat].
export function latLngDe(concierto) {
  const coordenadas = concierto.ubicacion_detalle?.coordenadas;
  if (!coordenadas || coordenadas.length !== 2) return null;
  return { lat: coordenadas[1], lng: coordenadas[0] };
}

export function enAmba({ lat, lng }) {
  return lat >= AMBA.minLat && lat <= AMBA.maxLat && lng >= AMBA.minLng && lng <= AMBA.maxLng;
}

// Distancia en km entre dos puntos {lat, lng} (fórmula de Haversine).
export function distanciaKm(a, b) {
  const toRad = (v) => (v * Math.PI) / 180;
  const R = 6371; // Radio de la Tierra en km
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const h =
    Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}
