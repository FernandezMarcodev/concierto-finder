import { useEffect, useState } from "react";

// Debe coincidir con el script inline de index.html, que aplica el tema antes del primer pintado.
const CLAVE_TEMA = "tema";
const consultaClaro = () => window.matchMedia("(prefers-color-scheme: light)");

function temaGuardado() {
  try {
    const valor = localStorage.getItem(CLAVE_TEMA);
    return valor === "claro" || valor === "oscuro" ? valor : null;
  } catch {
    return null; // Navegación privada o almacenamiento bloqueado
  }
}

const temaDelSistema = () => (consultaClaro().matches ? "claro" : "oscuro");

// Tema claro/oscuro. Sin elección del usuario sigue al sistema operativo.
export function useTema() {
  const [tema, setTema] = useState(() => temaGuardado() ?? temaDelSistema());

  useEffect(() => {
    document.documentElement.dataset.tema = tema;
  }, [tema]);

  // Mientras el usuario no elija, acompaña los cambios del sistema
  useEffect(() => {
    const consulta = consultaClaro();
    const alCambiar = () => {
      if (!temaGuardado()) setTema(temaDelSistema());
    };
    consulta.addEventListener("change", alCambiar);
    return () => consulta.removeEventListener("change", alCambiar);
  }, []);

  function alternarTema() {
    const nuevo = tema === "oscuro" ? "claro" : "oscuro";
    setTema(nuevo);
    try {
      localStorage.setItem(CLAVE_TEMA, nuevo); // se recuerda la elección para la próxima visita
    } catch {
      // Sin almacenamiento el cambio vale solo para esta visita
    }
  }

  return { tema, alternarTema };
}
