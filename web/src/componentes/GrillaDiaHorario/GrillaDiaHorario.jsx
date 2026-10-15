import { useMemo } from "react";
import styles from "./grillaDiaHorario.module.css";
import { useTemaActual } from "../../hooks/useTemaActual";
import { contraste, hexARgb, mezclar } from "../../utilidades/contraste";

const DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
const DIAS_LARGOS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"];
// Etiqueta corta de cada franja (la API manda el nombre largo, que va en el tooltip y la tabla)
const FRANJAS_CORTAS = { 1: "6 a 18", 2: "18 a 20", 3: "20 a 22", 4: "22 a 24", 5: "0 a 6" };

// Lee los colores del tema actual (variables CSS de index.css) para calcular el contraste de cada celda
function coloresDelTema() {
  const estilos = getComputedStyle(document.documentElement);
  const color = (nombre) => hexARgb(estilos.getPropertyValue(nombre));
  return {
    grafico: color("--color-grafico"),
    superficie: color("--color-surface"),
    texto: color("--color-text"),
    sobreAcento: color("--color-on-accent"),
  };
}

// Proporción del color en la mezcla: entre 12 % y 100 %, así hasta la celda más chica se distingue
const proporcion = (intensidad) => 0.12 + 0.88 * intensidad;

const conciertos = (n) => `${n} ${n === 1 ? "concierto" : "conciertos"}`;

/**
 * Grilla de calor día de la semana por franja horaria. Cada celda mezcla el color de los gráficos con
 * el fondo en proporción a la cantidad (color-mix): funciona igual en el tema claro y en el oscuro.
 * celdas: [{ dia: 1..7, franja: 1..5, nombre_franja, cantidad }] (la grilla completa, con ceros).
 */
function GrillaDiaHorario({ celdas }) {
  // Al cambiar de tema cambian los colores: se vuelven a leer
  const tema = useTemaActual();
  const colores = useMemo(coloresDelTema, [tema]);

  // Texto de la celda: entre el color de texto normal y el de "texto sobre acento", el de más
  // contraste con el fondo que resulta de la mezcla (una regla fija fallaba en el tema oscuro)
  const colorDeTexto = (intensidad) => {
    const fondo = mezclar(colores.grafico, colores.superficie, proporcion(intensidad));
    return contraste(colores.texto, fondo) >= contraste(colores.sobreAcento, fondo)
      ? "var(--color-text)"
      : "var(--color-on-accent)";
  };

  const maximo = Math.max(1, ...celdas.map((c) => c.cantidad));
  const franjas = [...new Set(celdas.map((c) => c.franja))].sort((a, b) => a - b);
  const celda = (dia, franja) => celdas.find((c) => c.dia === dia && c.franja === franja);

  return (
    <div className={styles.contenedor}>
      <div
        className={styles.grilla}
        role="table"
        aria-label="Conciertos por día de la semana y franja horaria"
      >
        <div role="row" className={styles.fila}>
          <span role="columnheader" className={styles.encabezadoHora}>
            Hora
          </span>
          {DIAS.map((dia) => (
            <span key={dia} role="columnheader" className={styles.encabezadoDia}>
              {dia}
            </span>
          ))}
        </div>

        {franjas.map((franja) => (
          <div key={franja} role="row" className={styles.fila}>
            <span role="rowheader" className={styles.nombreFranja}>
              {FRANJAS_CORTAS[franja]}
            </span>
            {DIAS.map((_, indice) => {
              const dato = celda(indice + 1, franja);
              const cantidad = dato?.cantidad ?? 0;
              const intensidad = cantidad / maximo;
              const descripcion = `${DIAS_LARGOS[indice]}, ${dato?.nombre_franja ?? ""}: ${conciertos(cantidad)}`;
              return (
                <span
                  key={indice}
                  role="cell"
                  className={styles.celda}
                  title={descripcion}
                  aria-label={descripcion}
                  style={
                    cantidad > 0
                      ? {
                          background: `color-mix(in srgb, var(--color-grafico) ${Math.round(100 * proporcion(intensidad))}%, var(--color-surface))`,
                          color: colorDeTexto(intensidad),
                        }
                      : undefined
                  }
                >
                  {cantidad > 0 ? cantidad : ""}
                </span>
              );
            })}
          </div>
        ))}
      </div>

      <div className={styles.leyenda} aria-hidden="true">
        <span>Menos</span>
        <span className={styles.escala} />
        <span>Más conciertos</span>
      </div>
    </div>
  );
}

export default GrillaDiaHorario;
