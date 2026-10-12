import { useEffect, useState } from "react";

// Tema vigente ("claro" | "oscuro"), leído del atributo data-tema de <html>.
// useTema guarda el tema en el estado de cada componente; este hook en cambio observa el
// atributo, así se entera cuando el botón del encabezado cambia el tema.
// Lo usa el mapa de calor, que pinta en un canvas y no puede usar variables CSS.
export function useTemaActual() {
  const [tema, setTema] = useState(() => document.documentElement.dataset.tema);

  useEffect(() => {
    const observador = new MutationObserver(() => setTema(document.documentElement.dataset.tema));
    observador.observe(document.documentElement, { attributes: true, attributeFilter: ["data-tema"] });
    return () => observador.disconnect();
  }, []);

  return tema;
}
