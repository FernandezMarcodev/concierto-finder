// Se configura con VITE_API_URL (archivo .env o .env.local). Sin valor, usa la API publicada.
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://concierto-finder.onrender.com";

export const conciertoServicio = {
  // Lanza un error si la API falla, para que la página muestre el estado de error
  // en lugar de una lista vacía.
  async obtenerConciertos() {
    const response = await fetch(`${API_BASE_URL}/conciertos`);
    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status} al pedir /conciertos`);
    }
    const data = await response.json();
    return Array.isArray(data?.conciertos) ? data.conciertos : [];
  },
};
