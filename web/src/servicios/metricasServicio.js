// Misma base que conciertoServicio: VITE_API_URL o, sin valor, la API publicada.
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://concierto-finder.onrender.com";

// filtro = { desde: "YYYY-MM-DD" | null, hasta: "YYYY-MM-DD" | null }
function consulta(filtro, extras = {}) {
  const parametros = new URLSearchParams();
  for (const [clave, valor] of Object.entries({ ...filtro, ...extras })) {
    if (valor != null && valor !== "") parametros.set(clave, valor);
  }
  const texto = parametros.toString();
  return texto ? `?${texto}` : "";
}

async function pedir(endpoint, filtro, extras) {
  const respuesta = await fetch(`${API_BASE_URL}/api/metricas/${endpoint}${consulta(filtro, extras)}`);
  if (!respuesta.ok) {
    throw new Error(`Error HTTP ${respuesta.status} al pedir /api/metricas/${endpoint}`);
  }
  return respuesta.json();
}

export const metricasServicio = {
  // Pide todas las métricas en paralelo. Si alguna falla, falla todo (la página muestra el error).
  async obtenerTodas(filtro) {
    const [resumen, porMes, lugares, artistas, distancias, densidad] = await Promise.all([
      pedir("resumen", filtro),
      pedir("conciertos_por_mes", filtro),
      pedir("lugares", filtro, { limite: 10 }),
      pedir("artistas", filtro, { limite: 10 }),
      pedir("distancias", filtro),
      pedir("densidad", filtro),
    ]);
    return {
      resumen,
      meses: porMes.meses,
      lugares: lugares.lugares,
      artistas: artistas.artistas,
      rangos: distancias.rangos,
      puntos: densidad.puntos,
    };
  },
};
