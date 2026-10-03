# 构建上下文是 companion/water-platform-demo（见 docker-compose.yml 的 build.context），
# 不是 frontend/ 本身：src/utils/readings.js 与 src/lesson71/*.js 通过
# ../../../shared/time.mjs 引用前后端共用的时间解析函数，该目录在 frontend/ 之外，
# 上下文若只取 frontend/，Docker 内的 npm run build 会报
# Could not resolve "../../../shared/time.mjs"。镜像内保持同样的相对目录结构。
FROM node:20-alpine AS build
WORKDIR /work/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY shared /work/shared
COPY frontend/src ./src
COPY frontend/public ./public
# Vite 是多页面入口（vite.config.js 的 rollupOptions.input 列出六个 HTML）
COPY frontend/index.html frontend/lesson44.html frontend/lesson44-detail.html \
     frontend/lesson45.html frontend/lesson61.html frontend/lesson74.html \
     frontend/lesson44.css frontend/vite.config.js ./
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /work/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
