import { useEffect, useState } from "react";

// Devuelve `valor` recién cuando deja de cambiar durante `ms` milisegundos.
export function useDebounce(valor, ms) {
  const [diferido, setDiferido] = useState(valor);

  useEffect(() => {
    const timeout = setTimeout(() => setDiferido(valor), ms);
    return () => clearTimeout(timeout);
  }, [valor, ms]);

  return diferido;
}
