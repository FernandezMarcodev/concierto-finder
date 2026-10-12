import styles from "./filtroRango.module.css";
import { PERIODOS } from "../../utilidades/periodos";

// Filtro de fechas de la página de métricas: atajos y, para un rango a medida, dos campos de fecha.
// filtro = { periodo, desde, hasta }; periodo es el id del atajo o "personalizado".
function FiltroRango({ filtro, onCambiar, error }) {
  const elegirPeriodo = (periodo) => onCambiar({ periodo: periodo.id, ...periodo.calcular(new Date()) });
  const cambiarFecha = (campo, valor) =>
    onCambiar({ ...filtro, periodo: "personalizado", [campo]: valor || null });

  return (
    <div className={styles.filtro}>
      <div className={styles.periodos} role="group" aria-label="Período">
        {PERIODOS.map((periodo) => (
          <button
            key={periodo.id}
            type="button"
            className={`${styles.periodo} ${filtro.periodo === periodo.id ? styles.periodoActivo : ""}`}
            aria-pressed={filtro.periodo === periodo.id}
            onClick={() => elegirPeriodo(periodo)}
          >
            {periodo.texto}
          </button>
        ))}
      </div>

      <div className={styles.fechas}>
        <label className={styles.campo}>
          Desde
          <input
            type="date"
            value={filtro.desde ?? ""}
            onChange={(e) => cambiarFecha("desde", e.target.value)}
          />
        </label>
        <label className={styles.campo}>
          Hasta
          <input
            type="date"
            value={filtro.hasta ?? ""}
            onChange={(e) => cambiarFecha("hasta", e.target.value)}
          />
        </label>
      </div>

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export default FiltroRango;
