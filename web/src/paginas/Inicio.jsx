import { useEffect, useMemo, useState } from "react";
import PieDePagina from "../componentes/PieDePagina/PieDePagina";
import Mapa from "../componentes/Mapa/Mapa";
import TarjetaGrupo from "../componentes/TarjetaGrupo/TarjetaGrupo";
import Filtros from "../componentes/Filtros/Filtros";
import EstadoVacio from "../componentes/EstadoVacio/EstadoVacio";
import EsqueletoLista from "../componentes/Cargando/EsqueletoLista";
import Encabezado from "../componentes/Encabezado/Encabezado";
import Portada, { DatoPortada } from "../componentes/Portada/Portada";
import { conciertoServicio } from "../servicios/conciertoServicio";
import { useDebounce } from "../hooks/useDebounce";
import { agruparPorPunto, claveGrupo } from "../utilidades/grupos";
import { filtrarConciertos } from "../utilidades/filtros";
import { etiquetaCercania } from "../utilidades/fechas";
import { DEBOUNCE_FILTROS_MS, RADIO_INICIAL } from "../constantes";

const Inicio = () => {
  const [conciertosBase, setConciertosBase] = useState([]); // Todos los conciertos sin filtrar
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  // Objeto nuevo en cada clic de "Ver en mapa", así el mapa vuelve a enfocar aunque sea el mismo concierto
  const [seleccion, setSeleccion] = useState(null);
  const [filtros, setFiltros] = useState({
    artista: "",
    radio: RADIO_INICIAL,
    ubicacionActual: null,
  });

  // Cargar todos los conciertos una sola vez; el filtrado es local
  useEffect(() => {
    let activo = true;

    conciertoServicio
      .obtenerConciertos()
      .then((datos) => {
        if (activo) setConciertosBase(datos);
      })
      .catch((err) => {
        console.error(err);
        if (activo) setError("Error al cargar los conciertos");
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, []);

  // Lista única de artistas para el autocompletado
  const artistas = useMemo(
    () => [...new Set(conciertosBase.map((c) => c.artista).filter(Boolean))].sort(),
    [conciertosBase],
  );

  // Debounce: evita recalcular en cada tecla o paso del slider
  const filtrosDiferidos = useDebounce(filtros, DEBOUNCE_FILTROS_MS);

  const conciertos = useMemo(
    () => filtrarConciertos(conciertosBase, filtrosDiferidos),
    [conciertosBase, filtrosDiferidos],
  );

  // Un grupo por lugar (en el orden de fecha que trae la API). Lo comparten el mapa y la lista.
  const grupos = useMemo(() => agruparPorPunto(conciertos), [conciertos]);

  // Datos de la portada: lugares con mapa y conciertos de hoy, según los filtros aplicados
  const cantidadLugares = grupos.filter((grupo) => grupo.lat != null).length;
  const cantidadHoy = useMemo(
    () => conciertos.filter((concierto) => etiquetaCercania(concierto.fecha) === "Hoy").length,
    [conciertos],
  );

  const verEnMapa = (concierto) => {
    setSeleccion({ id: concierto.id });
    document.getElementById("col-mapa")?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  };

  return (
    <div className="pagina-inicio">
      <Encabezado />

      <div className="contenedor-principal">
        <Portada
          titulo="Próximos conciertos"
          descripcion="Explorá los próximos conciertos en Buenos Aires y alrededores: dónde, cuándo y cómo llegar."
        >
          {!error && (
            <>
              <DatoPortada
                cargando={cargando}
                valor={conciertos.length}
                texto={conciertos.length === 1 ? "concierto" : "conciertos"}
              />
              <DatoPortada
                cargando={cargando}
                valor={cantidadLugares}
                texto={cantidadLugares === 1 ? "lugar" : "lugares"}
              />
              {!cargando && cantidadHoy > 0 && <DatoPortada valor={cantidadHoy} texto="hoy" />}
            </>
          )}
        </Portada>

        <Filtros filtros={filtros} setFiltros={setFiltros} artistas={artistas} />

        <div className="contenedor-grid">
          <div className="col-mapa" id="col-mapa">
            {error ? (
              <EstadoVacio tipo="error" />
            ) : (
              <Mapa
                grupos={grupos}
                ubicacionUsuario={filtros.ubicacionActual}
                radioKm={filtros.radio}
                seleccion={seleccion}
              />
            )}
          </div>

          <div className="col-lista">
            {error ? (
              <EstadoVacio tipo="error" />
            ) : cargando ? (
              <EsqueletoLista />
            ) : conciertos.length === 0 ? (
              <EstadoVacio tipo="sin-resultados" />
            ) : (
              grupos.map((grupo) => (
                <TarjetaGrupo
                  key={grupo.lat != null ? claveGrupo(grupo) : `suelto-${grupo.conciertos[0].id}`}
                  grupo={grupo}
                  seleccionadoId={seleccion?.id}
                  onVerEnMapa={verEnMapa}
                />
              ))
            )}
          </div>
        </div>
      </div>

      <PieDePagina />
    </div>
  );
};

export default Inicio;
