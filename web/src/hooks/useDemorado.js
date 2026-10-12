import { useEffect, useState } from "react";

// La API gratuita de Render se duerme y el primer pedido puede tardar hasta un minuto.
// Pasados estos milisegundos, las pantallas de carga explican por qué tarda.
export const DEMORA_AVISO_MS = 4000;

// true cuando pasaron `ms` milisegundos desde que se montó el componente.
export function useDemorado(ms = DEMORA_AVISO_MS) {
  const [demorado, setDemorado] = useState(false);

  useEffect(() => {
    const temporizador = setTimeout(() => setDemorado(true), ms);
    return () => clearTimeout(temporizador);
  }, [ms]);

  return demorado;
}
