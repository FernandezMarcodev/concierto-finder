// Fechas para los filtros de métricas. Todo en hora local: nunca new Date("YYYY-MM-DD"),
// que se interpreta como medianoche UTC y en Argentina daría el día anterior.

const dosDigitos = (n) => String(n).padStart(2, "0");

// Date -> "YYYY-MM-DD" (fecha local)
export function fechaIso(fecha) {
  return `${fecha.getFullYear()}-${dosDigitos(fecha.getMonth() + 1)}-${dosDigitos(fecha.getDate())}`;
}

export function sumarMeses(fecha, meses) {
  const resultado = new Date(fecha);
  resultado.setMonth(resultado.getMonth() + meses);
  return resultado;
}

// "2026-03" -> Date del 1 de marzo de 2026
function mesComoFecha(mes) {
  const [anio, numero] = mes.split("-").map(Number);
  return new Date(anio, numero - 1, 1);
}

// "2026-03" -> "mar 26" (eje del gráfico)
export function mesCorto(mes) {
  const fecha = mesComoFecha(mes);
  const nombre = fecha.toLocaleDateString("es-AR", { month: "short" }).replace(".", "");
  return `${nombre} ${String(fecha.getFullYear()).slice(2)}`;
}

// "2026-03" -> "marzo de 2026" (tooltip y tabla)
export function mesLargo(mes) {
  return mesComoFecha(mes).toLocaleDateString("es-AR", { month: "long", year: "numeric" });
}
