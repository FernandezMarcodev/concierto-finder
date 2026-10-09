// Normaliza texto para comparar sin acentos ni mayúsculas ("Páez" == "paez").

export function normalizarTexto(texto) {
  return (texto ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

// Versiones anteriores del backend serializaban los nulos con str(), así que
// pueden llegar como el texto "None". Se tratan igual que null.
function valorPresente(valor) {
  if (typeof valor !== "string") return null;
  const limpio = valor.trim();
  return limpio && limpio.toLowerCase() !== "none" ? limpio : null;
}

// "21:00:00" -> "21:00". Devuelve null si no hay hora.
export function horaLegible(hora) {
  const valor = valorPresente(hora);
  if (!valor) return null;
  return valor.substring(0, 5);
}

// "YYYY-MM-DD" -> "5/10/2026". Se arma la fecha en hora local: new Date("YYYY-MM-DD")
// la interpreta como medianoche UTC y en Argentina (UTC-3) mostraría el día anterior.
export function fechaLegible(fecha) {
  const valor = valorPresente(fecha);
  if (!valor) return "Fecha a confirmar";

  const [anio, mes, dia] = valor.split("-").map(Number);
  if (!anio || !mes || !dia) return "Fecha a confirmar";

  // En JavaScript los meses van de 0 (enero) a 11 (diciembre)
  return new Date(anio, mes - 1, dia).toLocaleDateString("es-AR");
}
