FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY src ./src
COPY public ./public
# Vite 是多页面入口（vite.config.js 的 rollupOptions.input 列出六个 HTML），
# 只拷 index.html 会在构建时报 Could not resolve entry module "lesson44.html"。
COPY index.html lesson44.html lesson44-detail.html lesson45.html lesson61.html lesson74.html lesson44.css vite.config.js ./
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
