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

// "YYYY-MM-DD" -> Date en hora local (null si no hay fecha válida)
export function fechaLocal(fecha) {
  if (typeof fecha !== "string") return null;
  const [anio, mes, dia] = fecha.split("-").map(Number);
  if (!anio || !mes || !dia) return null;
  return new Date(anio, mes - 1, dia);
}

// Partes de la fecha para el bloque tipo entrada: { dia: "17", mes: "oct", diaSemana: "vie" }
export function partesFecha(fecha) {
  const valor = fechaLocal(fecha);
  if (!valor) return null;
  const formato = (opciones) => valor.toLocaleDateString("es-AR", opciones).replace(".", "");
  return {
    dia: String(valor.getDate()),
    mes: formato({ month: "short" }),
    diaSemana: formato({ weekday: "short" }),
  };
}

// "Hoy" o "Mañana" si la fecha es cercana; null en cualquier otro caso.
export function etiquetaCercania(fecha, hoy = new Date()) {
  const valor = fechaLocal(fecha);
  if (!valor) return null;
  const inicioDeHoy = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
  const dias = Math.round((valor - inicioDeHoy) / 86_400_000);
  if (dias === 0) return "Hoy";
  if (dias === 1) return "Mañana";
  return null;
}
