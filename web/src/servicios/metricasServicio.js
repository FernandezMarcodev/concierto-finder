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
  // "próximos días" e "ingesta" miran desde hoy y no usan el filtro de fechas.
  async obtenerTodas(filtro) {
    const [
      resumen,
      porMes,
      lugares,
      artistas,
      densidad,
      diaHorario,
      proximos,
      calidad,
      ingesta,
      anticipacion,
    ] = await Promise.all([
      pedir("resumen", filtro),
      pedir("conciertos_por_mes", filtro),
      pedir("lugares", filtro, { limite: 10 }),
      pedir("artistas", filtro, { limite: 10 }),
      pedir("densidad", filtro),
      pedir("dia_horario", filtro),
      pedir("proximos_dias", {}, { dias: 14 }),
      pedir("calidad", filtro),
      pedir("ingesta", {}, { dias: 30 }),
      pedir("anticipacion", filtro),
    ]);
    return {
      resumen,
      meses: porMes.meses,
      lugares: lugares.lugares,
      artistas: artistas.artistas,
      puntos: densidad.puntos,
      celdas: diaHorario.celdas,
      proximos: proximos.dias,
      calidad,
      ingesta,
      anticipacion,
    };
  },
};
