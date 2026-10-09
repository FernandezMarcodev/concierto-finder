// Agrupa los conciertos por punto exacto para mostrar un solo marcador y una tarjeta por lugar.
// La API ya los devuelve ordenados por fecha y hora, y el agrupamiento respeta ese orden.
import { latLngDe } from "./geo";

export const claveGrupo = (grupo) => `${grupo.lat},${grupo.lng}`;

export function agruparPorPunto(conciertos) {
  const grupos = new Map();
  const sueltos = [];

  for (const concierto of conciertos) {
    const punto = latLngDe(concierto);
    if (!punto) {
      sueltos.push(concierto);
      continue;
    }

    const clave = claveGrupo(punto);
    if (!grupos.has(clave)) {
      grupos.set(clave, { ...punto, ubicacion_detalle: concierto.ubicacion_detalle, conciertos: [] });
    }
    grupos.get(clave).conciertos.push(concierto);
  }

  // Los que no tienen coordenadas no se pueden dibujar en el mapa, pero igual se listan
  return [...grupos.values(), ...sueltos.map((concierto) => ({ conciertos: [concierto] }))];
}
