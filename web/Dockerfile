# Etapa de build
FROM node:22-alpine AS build

WORKDIR /srv

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# URL de la API que consume el frontend (solo URL, nunca credenciales)
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Etapa de ejecución: solo los archivos estáticos, sin Node ni node_modules
FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /srv/dist /usr/share/nginx/html

EXPOSE 5173
