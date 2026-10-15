// Contraste de colores según WCAG: sirve para elegir el color del texto sobre un fondo que se
// calcula en el momento (por ejemplo, las celdas de la grilla de calor).

// "#0277bd" -> [2, 119, 189]
export function hexARgb(hex) {
  const limpio = hex.trim().replace("#", "");
  const completo = limpio.length === 3 ? [...limpio].map((c) => c + c).join("") : limpio;
  return [0, 2, 4].map((i) => parseInt(completo.slice(i, i + 2), 16));
}

// Mezcla como color-mix(in srgb, a p%, b): canal por canal, en sRGB
export function mezclar(a, b, proporcion) {
  return a.map((canal, i) => Math.round(canal * proporcion + b[i] * (1 - proporcion)));
}

// Luminancia relativa (WCAG 2.x)
function luminancia([r, g, b]) {
  const lineal = (c) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lineal(r) + 0.7152 * lineal(g) + 0.0722 * lineal(b);
}

// Contraste entre dos colores: de 1 (iguales) a 21 (negro sobre blanco)
export function contraste(a, b) {
  const [claro, oscuro] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return (claro + 0.05) / (oscuro + 0.05);
}
