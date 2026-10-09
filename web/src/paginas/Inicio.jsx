import { useEffect, useMemo, useState } from "react";
import PieDePagina from "../componentes/PieDePagina/PieDePagina";
import Mapa from "../componentes/Mapa/Mapa";
import TarjetaGrupo from "../componentes/TarjetaGrupo/TarjetaGrupo";
import Filtros from "../componentes/Filtros/Filtros";
import EstadoVacio from "../componentes/EstadoVacio/EstadoVacio";
import Cargando from "../componentes/Cargando/Cargando";
import Encabezado from "../componentes/Encabezado/Encabezado";
import { conciertoServicio } from "../servicios/conciertoServicio";
import { useDebounce } from "../hooks/useDebounce";
import { agruparPorPunto, claveGrupo } from "../utilidades/grupos";
import { filtrarConciertos } from "../utilidades/filtros";
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
        <div className="titulo-wrapper">
          <h1 className="titulo-principal">Próximos conciertos</h1>
          {!cargando && conciertos.length > 0 && (
            <span className="contador-conciertos">{conciertos.length}</span>
          )}
        </div>

        <img src="/logo.png" alt="Concierto Finder" className="logo-principal" />

        <p className="descripcion-principal">Explorá los próximos conciertos en Buenos Aires y alrededores</p>

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
              <Cargando />
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
