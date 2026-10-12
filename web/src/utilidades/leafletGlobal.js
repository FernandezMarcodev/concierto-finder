// leaflet.heat es un plugin viejo (2015) que espera Leaflet en la variable global `L`.
// Este módulo se importa ANTES que "leaflet.heat": los import se ejecutan en orden.
import L from "leaflet";

window.L = L;
