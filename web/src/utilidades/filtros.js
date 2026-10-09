import { distanciaKm, latLngDe } from "./geo";
import { normalizarTexto } from "./texto";

// Aplica los filtros de artista (sin acentos ni mayúsculas) y de radio alrededor del usuario.
export function filtrarConciertos(conciertos, { artista, radio, ubicacionActual }) {
  const consulta = normalizarTexto(artista);
  if (!consulta && !ubicacionActual) return conciertos;

  return conciertos.filter((concierto) => {
    if (consulta && !normalizarTexto(concierto.artista).includes(consulta)) return false;

    if (ubicacionActual) {
      const punto = latLngDe(concierto);
      // Sin coordenadas no se puede medir la distancia: se mantiene en la lista.
      if (punto) return distanciaKm(ubicacionActual, punto) <= radio;
    }

    return true;
  });
}
