import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Inicio from "./paginas/Inicio.jsx";
import Cargando from "./componentes/Cargando/Cargando.jsx";

// La página de métricas se descarga recién cuando se visita (code splitting): así los gráficos
// (Recharts) no agregan peso a la página principal.
const Metricas = lazy(() => import("./paginas/Metricas.jsx"));

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route
          path="/metricas"
          element={
            <Suspense fallback={<Cargando mensaje="Cargando métricas..." />}>
              <Metricas />
            </Suspense>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
