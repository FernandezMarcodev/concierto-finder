# Concierto Finder — frontend

SPA en React 18 + Vite + Leaflet. Publicada en https://conciertosfinder.pages.dev/

| Comando          | Qué hace                                |
| ---------------- | --------------------------------------- |
| `npm run dev`    | Servidor de desarrollo                  |
| `npm run build`  | Build de producción en `dist/`          |
| `npm run lint`   | ESLint                                  |
| `npm run format` | Prettier (`format:check` solo verifica) |

La URL de la API se toma de `VITE_API_URL` (por ejemplo, en `.env.local`). Sin ese valor
se usa la API de producción.

La arquitectura, la API y la operación del sistema completo están documentadas en la carpeta
[`docs/`](../docs) del repositorio (`ARQUITECTURA.md`, `API.md`, `OPERACION.md`).
