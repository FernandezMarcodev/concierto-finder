// Centro por defecto del mapa: Obelisco, Buenos Aires.
export const CENTRO_BSAS = [-34.6037, -58.3816];
export const ZOOM_INICIAL = 11;
export const ZOOM_LUGAR = 15;

// Región renderizable: Buenos Aires y alrededores (AMBA).
// Coincide con app/services/geocoding_service.py (dentro_de_amba), que es la
// fuente de verdad para lo que se guarda en la base. Cambiar ambos juntos.
export const AMBA = {
  minLat: -35.15,
  maxLat: -34.2,
  minLng: -58.95,
  maxLng: -57.7,
};

// Límite de navegación del mapa: Argentina completa.
export const ARG_MAX_BOUNDS = [
  [-55.05, -73.6],
  [-21.7, -53.6],
];

// Slider de radio de búsqueda (km).
export const RADIO_MIN = 1;
export const RADIO_MAX = 40;
export const RADIO_INICIAL = 5;
export const RADIO_ATAJOS = [5, 20, 40];

export const DEBOUNCE_FILTROS_MS = 300;
