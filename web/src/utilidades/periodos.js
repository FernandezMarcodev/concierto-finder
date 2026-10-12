import { fechaIso, sumarMeses } from "./fechas";

// Atajos de período de la página de métricas. Cada uno calcula { desde, hasta } a partir de
// hoy, en formato "YYYY-MM-DD" (null = sin límite).
export const PERIODOS = [
  { id: "todo", texto: "Todo", calcular: () => ({ desde: null, hasta: null }) },
  {
    id: "12m",
    texto: "Últimos 12 meses",
    calcular: (hoy) => ({ desde: fechaIso(sumarMeses(hoy, -12)), hasta: fechaIso(hoy) }),
  },
  {
    id: "3m",
    texto: "Últimos 3 meses",
    calcular: (hoy) => ({ desde: fechaIso(sumarMeses(hoy, -3)), hasta: fechaIso(hoy) }),
  },
  { id: "proximos", texto: "Próximos", calcular: (hoy) => ({ desde: fechaIso(hoy), hasta: null }) },
];

export const PERIODO_INICIAL = "todo";
